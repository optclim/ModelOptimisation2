from .dummy import DummyModel
from .UKESM import UKESM
from .MITgcm import MITgcm
from .HadCM3 import HadCM3

MODELS = {'DummyModel': DummyModel,
          'UKESM': UKESM,
          'MITgcm': MITgcm,
          'HadCM3': HadCM3}
