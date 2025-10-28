import argparse
import os
import sys
from profiler.wrapper import run_profiled_script


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Python code profiler with flame graph and statistics export',
        usage='python -m my_profiler [OPTIONS] <script_to_profile.py> [SCRIPT_ARGS...]'
    )
    parser.add_argument(
        'script',
        help='Path to the Python script to profile'
    )
    parser.add_argument(
        '--flame-graph',
        '-fg',
        action='store_true',
        help='Show flame graph visualization'
    )
    parser.add_argument(
        "--save-stats",
        "-ss",
        metavar="FILE",
        help="Save profiling statistics to JSON file"
    )
    parser.add_argument(
        '--top-slowest',
        action="store_true",
        help="Show top slowest functions by cumulative time"
    )
    parser.add_argument(
        'script_args',
        nargs=argparse.REMAINDER,
        help='Arguments to pass to the profiled script'
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    if not args.script:
        print("Error: No script specified")
        print("Usage: python -m profiler [OPTIONS] <script_to_profile.py> [SCRIPT_ARGS...]")
        sys.exit(1)
    if args.top_slowest and not args.save_stats:
        print("Error: Can't make top of slowest functions without saving stats")
    if not os.path.exists(args.script):
        print(f"Error: Script not found: {args.script}")
        sys.exit(1)
    run_profiled_script(args.script, args)