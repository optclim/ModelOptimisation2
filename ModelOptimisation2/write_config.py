import argparse
import logging
import json
from pathlib import Path

from .config import MODELS


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('modeldir', type=Path,
                        help="name of model directory")
    parser.add_argument('-p', '--parameters', type=Path,
                        help="name of file containing parameters to apply")
    parser.add_argument('-t', '--model-type', choices=MODELS.keys(),
                        default='UKESM',
                        help="select the model type")
    args = parser.parse_args()

    params = json.loads(args.parameters.read_text())
    model = args.model_type

    model = MODELS[model](args.modeldir)
    model.write_params(params)


if __name__ == '__main__':
    main()
