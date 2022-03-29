import pytest
from pathlib import Path
from ModelOptimisation2.model import SimpleNamelistValue, RepeatedNamelistValue
from ModelOptimisation2.model import InterpolatedValue
from ModelOptimisation2.model import NamelistModel

NML1 = """&grp1
    p1 = {paramA}
    p2 = {paramB}
/

&grp2
    p1 = {paramC}
/
"""

NML2 = """&grp1
    p1 = {paramD}
/
"""


@pytest.fixture
def rundir(tmpdir_factory):
    res = tmpdir_factory.mktemp("example-model")
    return res


def model_setup(rundir):
    with open(rundir / 'test1.nml', 'w') as test1:
        test1.write(NML1.format(
            paramA="'hello'",
            paramB=".true.",
            paramC="1"))
    with open(rundir / 'test2.nml', 'w') as test2:
        test2.write(NML2.format(
            paramD="1.0"))


class ExampleModel(NamelistModel):
    NAMELIST_MAP = {
        'paramA': SimpleNamelistValue('test1.nml', 'grp1', 'p1'),
        'paramB': SimpleNamelistValue('test1.nml', 'grp1', 'p2'),
        'paramC': SimpleNamelistValue('test1.nml', 'grp2', 'p1'),
        'paramD': SimpleNamelistValue('test2.nml', 'grp1', 'p1')}


def test_SimpleNamelistValue():
    nmlfile = 'test.nml'
    nmlgroup = 'test_grp'
    nmlkey = 'test_param'
    nmlval = 42

    test_param = SimpleNamelistValue(nmlfile, nmlgroup, nmlkey)

    v = test_param(nmlval)
    assert len(v) == 1
    assert v[0].nmlfile == nmlfile
    assert v[0].nmlgroup == nmlgroup
    assert v[0].nmlkey == nmlkey
    assert v[0].value == nmlval


def test_RepeatedNamelistValue():
    nmlfile = 'test.nml'
    nmlgroup = 'test_grp'
    nmlkeys = ['p1', 'p2', 'p3']
    nmlval = 42

    test_param = RepeatedNamelistValue(nmlfile, nmlgroup, nmlkeys)

    v = test_param(nmlval)

    for i in range(len(nmlkeys)):
        assert v[i].nmlfile == nmlfile
        assert v[i].nmlgroup == nmlgroup
        assert v[i].nmlkey == nmlkeys[i]
        assert v[i].value == nmlval


def test_InterpolatedValue():
    nmlfile = 'test.nml'
    nmlgroup = 'test_grp'
    nmlkey1 = 'param'
    nmlkey2 = 'interpolated_param'
    nmlval = 42

    test_param = InterpolatedValue(
        nmlfile, nmlgroup, nmlkey1, nmlkey2,
        [0, 21, 63], [0, 20, 10])

    v = test_param(nmlval)
    assert len(v) == 2
    assert v[0].nmlfile == nmlfile
    assert v[0].nmlgroup == nmlgroup
    assert v[0].nmlkey == nmlkey1
    assert v[0].value == nmlval
    assert v[1].nmlfile == nmlfile
    assert v[1].nmlgroup == nmlgroup
    assert v[1].nmlkey == nmlkey2
    assert v[1].value == 15


def test_model_fail(rundir):
    model = ExampleModel(rundir)

    with pytest.raises(LookupError):
        model.write_params({'ZZ': 'fail'})


def test_model(rundir):
    model_setup(rundir)
    model = ExampleModel(Path(rundir))

    params = {'paramA': 'hi world',
              'paramB': False,
              'paramC': 10,
              'paramD': -5.}

    model.write_params(params)

    assert (rundir / 'test1.nml~').exists()
    assert (rundir / 'test2.nml~').exists()

    assert (rundir / 'test1.nml').read() == \
        NML1.format(
            paramA="'hi world'",
            paramB=".false.",
            paramC="10")

    assert (rundir / 'test2.nml').read() == \
        NML2.format(
            paramD="-5.0")
