import argparse
import logging
from pathlib import Path
import shutil
import ObjectiveFunction

from .config import ModelOptimisationConfig


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('config', type=Path,
                        help="name of configuration file")
    parser.add_argument('-d', '--default-values', action='store_true',
                        default=False,
                        help="use default values from config file")
    parser.add_argument('-C', '--clone',
                        help="model setup to clone")
    args = parser.parse_args()

    config = ModelOptimisationConfig(args.config)
    modeldir = config.basedir

    if args.clone is not None:
        clonedir = Path(args.clone)
    else:
        clonedir = config.cloneDir
    if clonedir is None:
        parser.error('no clone directory specified')
    if not clonedir.is_dir():
        parser.error(f'clone directory {clonedir} does not exist')

    if args.default_values:
        params = config.values
        runid = None
    else:
        try:
            runid, params = config.objectiveFunction.get_with_state(
                ObjectiveFunction.LookupState.NEW, with_id=True,
                new_state=ObjectiveFunction.LookupState.CONFIGURING)
        except LookupError as e:
            parser.error(e)

    modeldir = config.modelDir(runid, create=True)
    shutil.copytree(clonedir, modeldir, dirs_exist_ok=True)

    model = config.model(modeldir)
    model.write_params(params)

    config.objectiveFunction.setState(
        runid, ObjectiveFunction.LookupState.CONFIGURED)

    print(modeldir)


if __name__ == '__main__':
    main()
