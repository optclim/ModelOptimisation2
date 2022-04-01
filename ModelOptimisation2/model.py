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
        pass


class SimpleNamelistValue(BaseNamelistValue):
    def __init__(self, nmlfile: str, nmlgroup: str, nmlkey: str):
        super().__init__(nmlfile, nmlgroup)
        self._nmlkey = nmlkey

    def __call__(self, value: Any) -> Sequence[NMLValue]:
        return [self._get_nmlval(self._nmlkey, value)]


class RepeatedNamelistValue(BaseNamelistValue):
    def __init__(self, nmlfile: str, nmlgroup: str, nmlkeys: Sequence[str]):
        super().__init__(nmlfile, nmlgroup)
        self._nmlkeys = nmlkeys

    def __call__(self, value: Any) -> Sequence[NMLValue]:
        values = []
        for k in self._nmlkeys:
            values.append(self._get_nmlval(k, value))
        return values


class InterpolatedValue(BaseNamelistValue):
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
    NAMELIST_MAP: Dict[str, BaseNamelistValue] = {}

    def __init__(self, directory: Path):
        self._directory = directory

    @property
    def directory(self) -> Path:
        return self._directory

    def process_params(self, params: Dict[str, Any]) -> \
            Dict[Path, Dict[str, Dict[str, Any]]]:
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
