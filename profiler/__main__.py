import sys
from profiler.wrapper import run_profiled_script


if __name__ == "__main__":
    # print(sys.argv)
    if len(sys.argv) < 2:
        print("Usage: python -m my_profiler <script_to_profile.py>")
        sys.exit(1)
    script_to_profile_path = sys.argv[1]
    run_profiled_script(script_to_profile_path, sys.argv)