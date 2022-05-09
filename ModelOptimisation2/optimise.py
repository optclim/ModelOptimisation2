import argparse
import logging
from pathlib import Path
from dfols import solve
import sys
import ObjectiveFunction_client

from .config import ModelOptimisationConfig


def residual(cfg, x):
    obs = cfg.objectiveFunction(x)

    residual = obs - cfg.targets
    return residual


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('config', type=Path,
                        help="name of configuration file")
    args = parser.parse_args()

    config = ModelOptimisationConfig(args.config)

    for i in range(2):
        # start with lower bounds
        try:
            x = solve(
                lambda x: residual(config, x),
                config.objectiveFunction.params2values(
                    config.values,
                    include_constant=False),
                bounds=(
                    config.objectiveFunction.lower_bounds,
                    config.objectiveFunction.upper_bounds),
                scaling_within_bounds=True
            )
        except ObjectiveFunction_client.PreliminaryRun:
            logging.info('new parameter set')
            continue
        except ObjectiveFunction_client.NewRun:
            print('new')
            sys.exit(1)
        except ObjectiveFunction_client.Waiting:
            print('waiting')
            sys.exit(2)
        break

    logging.info(f"optimum at {x}")
    print('done')


if __name__ == '__main__':
    main()
