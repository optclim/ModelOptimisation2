import argparse
import logging
import json
from pathlib import Path
import shutil
import ObjectiveFunction

from .config import MODELS


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-p', '--parameters', type=Path,
                       help="name of file containing parameters to apply")
    group.add_argument('-c', '--config', type=Path,
                       help="name of configuration file")
    parser.add_argument('modeldir', type=Path,
                        help="name of model directory")
    parser.add_argument('-t', '--model-type', choices=MODELS.keys(),
                        default='UKESM',
                        help="select the model type")
    parser.add_argument('-d', '--default-values', action='store_true',
                        default=False,
                        help="use default values from config file")
    parser.add_argument('-C', '--clone', help="model setup to clone")
    args = parser.parse_args()

    modeldir = args.modeldir
    if args.parameters is not None:
        params = json.loads(args.parameters.read_text())
        model = args.model_type
    elif args.config is not None:
        config = ObjectiveFunction.ObjFunConfig(args.config)
        model = config.cfg['setup']['model']
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
    else:
        parser.error('need to specify either parameter set or config file')

    model = MODELS[model](modeldir)
    model.write_params(params)

    if args.config is not None:
        config.objectiveFunction.setState(
            runid, ObjectiveFunction.LookupState.CONFIGURED)

    print(modeldir)


if __name__ == '__main__':
    main()
