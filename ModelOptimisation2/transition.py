import argparse
import logging
from pathlib import Path
import ObjectiveFunction

STATES = ObjectiveFunction.LookupState._member_names_


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('config', type=Path,
                        help="name of configuration file")
    parser.add_argument('current', choices=STATES,
                        help="select current state")
    parser.add_argument('new', choices=STATES,
                        help="select new state")
    args = parser.parse_args()

    current_state = ObjectiveFunction.LookupState[args.current]
    new_state = ObjectiveFunction.LookupState[args.new]

    if new_state.value <= current_state.value:
        parser.error('new state must follow current state')

    config = ObjectiveFunction.ObjFunConfig(args.config)

    try:
        runid, params = config.objectiveFunction.get_with_state(
            current_state, with_id=True, new_state=new_state)
    except LookupError as e:
        parser.error(e)

    modeldir = config.basedir / Path(f'run_{runid:04d}')

    if not modeldir.exists():
        parser.error(f'model directory {modeldir} does not exist')
    runid_name = modeldir / 'objfun.runid'
    if not runid_name.exists():
        parser.error(f'run ID file {runid_name} does not exist')
    if runid_name.read_text() != f'{runid}':
        parser.error('run ID does not match')

    print(modeldir)


if __name__ == '__main__':
    main()
