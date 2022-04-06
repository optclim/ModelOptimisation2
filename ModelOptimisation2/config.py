__all__ = ['MODELS', 'ModelOptimisationConfig']

from pathlib import Path

import ObjectiveFunction
from .dummy import DummyModel
from .UKESM import UKESM
from .MITgcm import MITgcm
from .HadCM3 import HadCM3

MODELS = {'DummyModel': DummyModel,
          'UKESM': UKESM,
          'MITgcm': MITgcm,
          'HadCM3': HadCM3}


class ModelOptimisationConfig(ObjectiveFunction.ObjFunConfig):
    defaultCfgStr = ObjectiveFunction.ObjFunConfig.defaultCfgStr.replace(
        'objfun = string(default=misfit)', 'objfun = string(default=misfit)\n'
        'model = string(default=DummyModel)')

    def __init__(self, fname: Path) -> None:
        super().__init__(fname)

        self._scales = None
        self._model = None

    @property
    def scales(self):
        if self._scales is None:
            self._scales = {}
            for obs in self.observationNames:
                if obs in self.cfg['scales']:
                    self._scales[obs] = self.cfg['scales'][obs]
                else:
                    self._scales[obs] = 1.
        return self._scales

    def modelDir(self, runID, create=False):
        if runID is None:
            cdir = Path('default')
        else:
            cdir = Path(f'run_{runID:04d}')
        modeldir = self.basedir / cdir
        runid_name = modeldir / 'objfun.runid'
        if create:
            if modeldir.exists():
                raise RuntimeError(
                    f'target directory {modeldir} already exists')
            modeldir.mkdir()
            runid_name.write_text(f'{runID}')
        else:
            if not modeldir.exists():
                raise RuntimeError(
                    f'model directory {modeldir} does not exist')
            if not runid_name.exists():
                raise RuntimeError(
                    f'run ID file {runid_name} does not exist')
            if runid_name.read_text() != f'{runID}':
                raise RuntimeError('run ID does not match')
        return modeldir

    @property
    def model(self):
        if self._model is None:
            self._model = MODELS[self.cfg['setup']['model']]
        return self._model
