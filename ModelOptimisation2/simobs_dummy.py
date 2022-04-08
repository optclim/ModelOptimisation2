import argparse
import logging
from pathlib import Path
import xarray
import pandas
import ObjectiveFunction

from .config import ModelOptimisationConfig


COORDS = {'sim0': [0.1, 0.1],
          'sim1': [0.1, 0.5],
          'sim2': [0.1, 0.9],
          'sim3': [0.5, 0.1],
          'sim4': [0.5, 0.9]}


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('config', type=Path,
                        help="name of configuration file")
    parser.add_argument('-d', '--data-file', type=Path,
                        help="name of netCDF file to read data from")
    args = parser.parse_args()

    config = ModelOptimisationConfig(args.config)

    if args.data_file is not None:
        data_file = args.data_file
    else:
        try:
            runid, params = config.objectiveFunction.get_with_state(
                ObjectiveFunction.LookupState.RUN, with_id=True,
                new_state=ObjectiveFunction.LookupState.POSTPROCESSING)
        except LookupError as e:
            parser.error(e)
        modeldir = config.modelDir(runid)
        data_file = modeldir / 'results.nc'

    data = xarray.open_dataset(data_file)
    simobs = {}
    for obs in config.cfg['targets']:
        x, y = COORDS[obs]
        x = float(data.x[0]) + float(data.x[-1] - data.x[0]) * x
        y = float(data.y[0]) + float(data.y[-1] - data.y[0]) * y
        z = float(data.z.sel(x=x, y=y, method='nearest'))
        simobs[obs] = z

    simobs = pandas.Series(simobs)

    if args.data_file is not None:
        print(simobs)
    else:
        config.objectiveFunction.set_result(params, simobs)


if __name__ == '__main__':
    main()
