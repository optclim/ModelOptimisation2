__all__ = ['MODELS', 'ModelOptimisationConfig']

from pathlib import Path

import ObjectiveFunction_client
from .config_dummy import DummyModel
from .config_UKESM import UKESM
from .config_MITgcm import MITgcm
from .config_HadCM3 import HadCM3

MODELS = {'DummyModel': DummyModel,
          'UKESM': UKESM,
          'MITgcm': MITgcm,
          'HadCM3': HadCM3}


class ModelOptimisationConfig(ObjectiveFunction_client.ObjFunConfig):
    setupCfgStr = """
    [setup]
      app = string() # the name of ObjectiveFunction app
      # the URL of the ObjectiveFunction server
      baseurl = string(default=http://localhost:5000/api/)
      study = string() # the name of the study
      scenario = string() # the name of the scenario
      basedir = string() # the base directory
      model = string(default=DummyModel)
      clone = string(default=None)
    """

    modeloptCfgStr = """
    [scales]
      __many__ = float
    """

    RUNID = Path('objfun.runid')

    def __init__(self, fname: Path) -> None:
        super().__init__(fname)

        self._scales = None
        self._model = None

    @property
    def defaultCfgStr(self):
        return super().defaultCfgStr + '\n' + self.modeloptCfgStr

    @property
    def objfunType(self):
        """the objective function type"""
        return "simobs"

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

    @property
    def cloneDir(self):
        if self.cfg['setup']['clone'] is not None:
            return self.expand_path(self.cfg['setup']['clone'])

    def modelDir(self, runID, create=False):
        if runID is None:
            cdir = Path('default')
        else:
            cdir = Path(f'run_{runID:04d}')
        modeldir = self.basedir / cdir
        runid_name = modeldir / self.RUNID
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


if __name__ == '__main__':
    import sys
    from pprint import pprint
    config = ModelOptimisationConfig(Path(sys.argv[1]))
    pprint(config.cfg)
    print(config.cloneDir)
