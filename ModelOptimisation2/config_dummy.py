from .model import SimpleNamelistValue, RepeatedNamelistValue
from .model import InterpolatedValue, NamelistModel


class DummyModel(NamelistModel):
    NAMELIST_MAP = {
        'ab': RepeatedNamelistValue('config.nml', 'POLYNOMIAL', ['a', 'b']),
        'c': SimpleNamelistValue('config.nml', 'POLYNOMIAL', 'c'),
        'de': InterpolatedValue('config.nml', 'POLYNOMIAL', 'd', 'e',
                                [-10, 0, 10], [10, 0, -5]),
        'f': SimpleNamelistValue('config.nml', 'POLYNOMIAL', 'f')}
