#
# main.py
#
# Command-line entry point for the satellite-lighting service.
#

import argparse
import logging
import sys

from output.factory import build_output
from service import LightingService
from tracking.factory import build_tracker
from utils.config import load_config
from utils.errors import SatelliteLightingError


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    _setup_logging(args.log_level)
    try:
        config = load_config(args.config)
        tracker = build_tracker(config)
        output = build_output(config)
    except (SatelliteLightingError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    LightingService(config, tracker, output).run()
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="satellite-lighting",
        description="Emit lighting commands for satellites passing over a location.",
    )
    parser.add_argument("--config", required=True, help="Path to the JSON config file.")
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level for STDERR (DEBUG, INFO, WARNING, ...). Default: INFO.",
    )
    return parser.parse_args(argv)


def _setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        stream=sys.stderr,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


if __name__ == "__main__":
    raise SystemExit(main())
