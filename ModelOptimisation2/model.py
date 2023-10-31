__all__ = ['NMLValue', 'BaseNamelistValue', 'SimpleNamelistValue',
           'RepeatedNamelistValue', 'InterpolatedValue', 'NamelistModel']

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Sequence, Dict
from pathlib import Path
from scipy.interpolate import interp1d
from numpy.typing import ArrayLike
import logging
import f90nml


@dataclass
class NMLValue:
    """a name list key/value pair

     :param nmlfile: the name of the namelist file
     :param nmlgroup: the name of the namelist
     :param nmlkey: the key
     :param value: the value
    """
    nmlfile: Path
    nmlgroup: str
    nmlkey: str
    value: Any


class BaseNamelistValue:
    def __init__(self, nmlfile: str, nmlgroup: str):
        self._nmlfile = nmlfile
        self._nmlgroup = nmlgroup

    def _get_nmlval(self, key, value):
        return NMLValue(nmlfile=self._nmlfile,
                        nmlgroup=self._nmlgroup,
                        nmlkey=key,
                        value=value)

    @abstractmethod
    def __call__(self, value) -> Sequence[NMLValue]:
        """turn value into a list of namelist key/value pairs"""
        pass


class SimpleNamelistValue(BaseNamelistValue):
    """a simple namelist value

    produces a single entry in a namelist

    :param nmlfile: the name of the namelist file
    :type nmlfile: str
    :param nmlgroup: the name of the namelist
    :type nmlgroup: str
    :param nmlkey: the key
    :type nmlkey: str
    """
    def __init__(self, nmlfile: str, nmlgroup: str, nmlkey: str):
        """constructor"""
        super().__init__(nmlfile, nmlgroup)
        self._nmlkey = nmlkey

    def __call__(self, value: Any) -> Sequence[NMLValue]:
        return [self._get_nmlval(self._nmlkey, value)]


class RepeatedNamelistValue(BaseNamelistValue):
    """a repeated namelist value

    produces a list of entries in a namelist with a repeated value

    :param nmlfile: the name of the namelist file
    :type nmlfile: str
    :param nmlgroup: the name of the namelist
    :type nmlgroup: str
    :param nmlkeys: a list of namelist keys
    :type nmlkeys: list
    """
    def __init__(self, nmlfile: str, nmlgroup: str, nmlkeys: Sequence[str]):
        super().__init__(nmlfile, nmlgroup)
        self._nmlkeys = nmlkeys

    def __call__(self, value: Any) -> Sequence[NMLValue]:
        values = []
        for k in self._nmlkeys:
            values.append(self._get_nmlval(k, value))
        return values


class InterpolatedValue(BaseNamelistValue):
    """an interpolated namelist value

    Interpolate a value on a piecewise linear function

    :param nmlfile: the name of the namelist file
    :type nmlfile: str
    :param nmlgroup: the name of the namelist
    :type nmlgroup: str
    :param nmlkey1: the key for the value
    :type nmlkey1: str
    :param nmlkey2: the key for the interpolated value
    :type nmlkey2: str
    :param x: array of x coordinates of the nodes the piecewise linear function
    :type x: arraylike
    :param y: array of y coordinates of the nodes the piecewise linear function
    :type y: arraylike
     """
    def __init__(self, nmlfile: str, nmlgroup: str,
                 nmlkey1: str, nmlkey2: str,
                 x: ArrayLike, y: ArrayLike):
        super().__init__(nmlfile, nmlgroup)
        self._nmlkey1 = nmlkey1
        self._nmlkey2 = nmlkey2

        self._interp = interp1d(x, y, kind='linear', bounds_error=True,
                                assume_sorted=True)

    def __call__(self, value):
        return [self._get_nmlval(self._nmlkey1, value=value),
                self._get_nmlval(self._nmlkey2,
                                 value=float(self._interp(value)))]


class NamelistModel:
    """a model configured by namelists

    :param directory: the base directory where model configuration is kept
    """

    NAMELIST_MAP: Dict[str, BaseNamelistValue] = {}

    def __init__(self, directory: Path):
        """constructor"""

        self._directory = directory

    @property
    def directory(self) -> Path:
        return self._directory

    def process_params(self, params: Dict[str, Any]) -> \
            Dict[Path, Dict[str, Dict[str, Any]]]:
        """map dictionary of parameters to dictionary of namelist files

        :param params: a dictionary containing parameter names and values
        """
        output: Dict[Path, Dict[str, Dict[str, Any]]] = {}
        # map input parameters to output namelist files
        for key in params:
            if key not in self.NAMELIST_MAP:
                raise LookupError(f'parameter {key} not mapped to namelist')
            for nml in self.NAMELIST_MAP[key](params[key]):
                if nml.nmlfile not in output:
                    output[nml.nmlfile] = {}
                if nml.nmlgroup not in output[nml.nmlfile]:
                    output[nml.nmlfile][nml.nmlgroup] = {}
                output[nml.nmlfile][nml.nmlgroup][nml.nmlkey] = nml.value
        return output

    def write_params(self, params: Dict[str, Any]) -> None:
        """modify namelists with parameters from dictionary

        :param params: a dictionary containing parameter names and values
        """
        output = self.process_params(params)

        # write output namelist files
        for nml in output:
            nmlname = self.directory / nml
            if nmlname.exists():
                old = nmlname.with_suffix('.nml~')
                nmlname.replace(old)
                f90nml.patch(old, output[nml], nmlname)
            else:
                logging.warning(f'no namelist file {nmlname}')
