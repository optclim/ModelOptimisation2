__all__ = ['MITgcm']

from .model import SimpleNamelistValue, NamelistModel


class MITgcm(NamelistModel):
    NAMELIST_MAP = {
        'gravity': SimpleNamelistValue(
            'data', 'PARM01', 'gravity'),
        'seaice_strength': SimpleNamelistValue(
            'data.seaice', 'SEAICE_PARM01', 'SEAICE_STRENGTH')}
