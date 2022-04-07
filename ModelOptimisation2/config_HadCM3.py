import math
import numpy
from scipy.interpolate import interp1d

from .model import NMLValue, BaseNamelistValue, SimpleNamelistValue
from .model import RepeatedNamelistValue, InterpolatedValue, NamelistModel


class SphIce(BaseNamelistValue):
    def __init__(self):
        super().__init__('CNTLATM', 'R2LWCLNL')
        self._sph_ice = {'I_CNV_ICE_LW': 1,
                         'I_ST_ICE_LW': 1,
                         'I_CNV_ICE_SW': 3,
                         'I_ST_ICE_SW': 2}
        self._no_sph_ice = {'I_CNV_ICE_LW': 7,
                            'I_ST_ICE_LW': 7,
                            'I_CNV_ICE_SW': 7,
                            'I_ST_ICE_SW': 7}

    def __call__(self, value):
        if value:
            values = self._sph_ice
        else:
            values = self._no_sph_ice
        nmmlvals = []
        for k, v in values.items:
            nmmlvals.append(self._get_nmlval(k, v))
        return nmmlvals


class RunName(BaseNamelistValue):
    def __init__(self):
        super().__init__('CNTLALL', 'NLSTCALL')

    def __call__(self, value):
        return [self._get_nmlval('EXPT_ID', value[:4]),
                self._get_nmlval('JOB_ID', value[4]),
                NMLValue(nmlfile='CONTCNTL', nmlgroup='NLSTCALL',
                         nmlkey='EXPT_ID', value=value[:4]),
                NMLValue(nmlfile='CONTCNTL', nmlgroup='NLSTCALL',
                         nmlkey='JOBID_ID', value=value[4]),
                NMLValue(nmlfile='INITHIS', nmlgroup='NLCHISTO',
                         nmlkey='RUN_JOB_NAME', value=value + '000')]


class CloudRHcrit(SimpleNamelistValue):
    def __init__(self, num_levels):
        super().__init__('CNTLATM', 'RUNCNST', 'RHCRIT')
        self._num_levels = num_levels

    def __call__(self, value):
        rhcrit = self._num_levels * [value]
        rhcrit[0] = max(0.95, value)
        rhcrit[1] = max(0.9, value)
        rhcrit[2] = max(0.85, value)
        return super().__call__(rhcrit)


class CloudEACF(SimpleNamelistValue):
    def __init__(self, num_levels):
        super().__init__('CNTLATM', 'SLBC21', 'EACF')
        self._num_levels = num_levels
        self._interp = interp1d([0.5, 0.7, 0.8], [0.5, 0.6, 0.65],
                                kind='linear', bounds_error=True,
                                assume_sorted=True)

    def __call__(self, value):
        if value < 0.5:
            raise ValueError(f'value must be ge 0.5, but got {value}')
        eacf1 = self._interp(value)
        cloud_eacf = self._num_levels * [eacf1]
        cloud_eacf[0:5] = 5 * [value]
        cloud_eacf[5] = (2. * value + eacf1) / 3.
        cloud_eacf[6] = (value + 2. * eacf1) / 3.
        return super().__call__(cloud_eacf)


class Diffusion(BaseNamelistValue):
    def __init__(self, num_levels, dlat=2.5, radius=6.37123e06,
                 timestep=1800., diff_pwr=6):
        super().__init__('CNTLATM', 'RUNCNST')
        if diff_pwr not in [6, 4]:
            raise ValueError(f'invalid value for diff_pwr {diff_pwr}')
        self._diff_pwr = diff_pwr
        self._num_levels = num_levels
        dphi = math.radians(dlat)
        self._d2q = 0.25 * radius * radius * dphi * dphi
        self._timestep = timestep

    def __call__(self, value):
        dampn = value * 3600. / self._timestep
        en = 1 - math.exp(-1. / dampn)
        endt = en / self._timestep
        diffval = self._d2q * endt ** (1 / (0.5 * self._diff_pwr))
        tmp = self._diff_pwr / 2  # integral

        diff_coeff = numpy.repeat(diffval, self._num_levels)
        diff_coeff[-1] = 4e06
        diff_coeff_q = numpy.repeat(diffval, self._num_levels)
        diff_coeff_q[13:-1] = 1.5e08
        diff_coeff_q[-1] = 4e06
        diff_exp = numpy.repeat(tmp, self._num_levels)
        diff_exp[-1] = 1
        diff_exp_q = numpy.repeat(tmp, self._num_levels)
        diff_exp_q[13:-1] = 2
        diff_exp_q[-1] = 1

        return [self._get_nmlval('DIFF_COEFF', diff_coeff),
                self._get_nmlval('DIFF_COEFF_Q', diff_coeff_q),
                self._get_nmlval('DIFF_EXP', diff_exp),
                self._get_nmlval('DIFF_EXP_Q', diff_exp_q)]


class HadCM3(NamelistModel):
    NAMELIST_MAP = {
        'sphIce': SphIce(),
        'runName': RunName(),
        'gravityWave': InterpolatedValue(
            'CNTLATM', 'RUNCNST', 'KAY_GWAVE', 'KAY_LEE_GWAVE',
            [1e04, 1.5e04, 2e04], [1.5e05, 2.25e05, 3e05]),
        'iceAlbedo': InterpolatedValue(
            'CNTLATM', 'RUNCNST', 'ALPHAM', 'DTICE',
            [0.5, 0.57, 0.65], [10., 5., 2.]),
        'cloudWater': InterpolatedValue(
            'CNTLATM', 'RUNCNST', 'CW_LAND', 'CW_SEA',
            [1e-04, 2e-04, 2e-03], [2e-05, 5e-05, 5e-04]),
        'cloudRHcrit': CloudRHcrit(19),
        'cloudEACF': CloudEACF(19),
        'diffusion': Diffusion(19),
        'iceDiff': RepeatedNamelistValue('CNTLOCN', 'SEAICENL',
                                         ['EDDYDIFFN', 'EDDYDIFFS']),
        'iceMaxConc': RepeatedNamelistValue('CNTLOCN', 'SEAICENL',
                                            ['AMXNORTH', 'AMXSOUTH']),
        'ocnIsoDiff': RepeatedNamelistValue('CNTLOCN', 'EDDY',
                                            ['AM0_SI', 'AM1_SI'])}
