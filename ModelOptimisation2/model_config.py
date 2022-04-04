import argparse
import logging
from pathlib import Path
import shutil
import ObjectiveFunction

from .config import MODELS


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('config', type=Path,
                        help="name of configuration file")
    parser.add_argument('-d', '--default-values', action='store_true',
                        default=False,
                        help="use default values from config file")
    parser.add_argument('-C', '--clone', required=True,
                        help="model setup to clone")
    args = parser.parse_args()

    config = ObjectiveFunction.ObjFunConfig(args.config)
    model = config.cfg['setup']['model']
    modeldir = config.basedir

    if args.default_values:
        params = config.values
        cdir = Path('default')
        runid = None
    else:
        try:
            runid, params = config.objectiveFunction.get_with_state(
                ObjectiveFunction.LookupState.NEW, with_id=True,
                new_state=ObjectiveFunction.LookupState.CONFIGURING)
        except LookupError as e:
            parser.error(e)
        cdir = Path(f'run_{runid:04d}')

    if args.clone:
        modeldir = modeldir / cdir
        clonedir = Path(args.clone)
        if not clonedir.is_dir():
            parser.error(f'clone directory {clonedir} does not exist')
        if modeldir.exists():
            parser.error(f'target directory {modeldir} already exists')
        shutil.copytree(args.clone, modeldir)
        if runid is not None:
            (modeldir / 'objfun.runid').write_text(f'{runid}')

    model = MODELS[model](modeldir)
    model.write_params(params)

    config.objectiveFunction.setState(
        runid, ObjectiveFunction.LookupState.CONFIGURED)

    print(modeldir)


if __name__ == '__main__':
    main()
