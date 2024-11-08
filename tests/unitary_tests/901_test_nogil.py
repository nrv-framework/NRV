import sys

def main():
    print(f"Python Version: {sys.version}")

    # Check GIL status
    py_version = float(".".join(sys.version.split()[0].split(".")[0:2]))

    if py_version >= 3.13:
        status = sys._is_gil_enabled()
    if status is None:
        print("GIL cannot be disabled for Python version <= 3.12")
    if status == 0:
        print("GIL is currently disabled")
    if status == 1:
        print("GIL is currently active")

if __name__ == "__main__":
    main()