import subprocess
import sys


def main():
    print("Running controlled test suite...")
    cmd = [sys.executable, "-m", "pytest", "tests"]
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
