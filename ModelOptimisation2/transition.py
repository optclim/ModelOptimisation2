import argparse
import logging
from pathlib import Path
import ObjectiveFunction_client

from .config import ModelOptimisationConfig

STATES = ObjectiveFunction_client.LookupState._member_names_


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('config', type=Path,
                        help="name of configuration file")
    parser.add_argument('current', choices=STATES,
                        help="select current state")
    parser.add_argument('new', choices=STATES,
                        help="select new state")
    parser.add_argument('-i', '--runid', type=int, const=-1, nargs='?',
                        help="change state of run with ID. "
                        "If no ID is specified read it from objfun.runid")
    args = parser.parse_args()

    current_state = ObjectiveFunction_client.LookupState[args.current]
    new_state = ObjectiveFunction_client.LookupState[args.new]

    if new_state.value <= current_state.value:
        parser.error('new state must follow current state')

    config = ModelOptimisationConfig(args.config)

    if args.runid is not None:
        if args.runid == -1:
            runid = int(config.RUNID.read_text())
        else:
            runid = args.runid
        try:
            state = config.objectiveFunction.getState(runid)
        except LookupError:
            parser.error(f'no run with ID {runid}')
        if state != current_state:
            parser.error(f'run is in wrong state {state.name}')
        config.objectiveFunction.setState(runid, new_state)
    else:
        try:
            runid, params = config.objectiveFunction.get_with_state(
                current_state, with_id=True, new_state=new_state)
        except LookupError as e:
            parser.error(e)

        modeldir = config.modelDir(runid)

        print(modeldir)


if __name__ == '__main__':
    main()
