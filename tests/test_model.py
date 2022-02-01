import pytest
from pathlib import Path
from OptClim2.model import SimpleNamelistValue

def test_simplenmlvalue():
    nmlfile = Path('test.nml')
    nmlgroup = 'test_grp'
    nmlkey = 'test_patam'
    nmlval = 42

    test_param = SimpleNamelistValue(nmlfile, nmlgroup, nmlkey)

    v = test_param(nmlval)
    assert len(v) == 1
    assert v[0].nmlfile == nmlfile
    assert v[0].nmlgroup == nmlgroup
    assert v[0].nmlkey == nmlkey
    assert v[0].value == nmlval
