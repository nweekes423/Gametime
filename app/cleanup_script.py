import os
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")

def apply_autopep8(file_path):
    full_path = os.path.join(BASE_DIR, file_path)
    if os.path.exists(full_path):
        run_command(f"autopep8 --in-place --aggressive --aggressive {full_path}")
    else:
        print(f"File not found: {full_path}")

def apply_pylint(file_path):
    full_path = os.path.join(BASE_DIR, file_path)
    if os.path.exists(full_path):
        run_command(f"pylint {full_path}")
    else:
        print(f"File not found: {full_path}")

def main():
    # List of files to process
    files_to_process = [
        "__init__.py",
        "test_logging.py",
        "locustfile.py",
        "gettoken.py",
        "celeryy.py",
        "celery_setup.py",
        "update_scoreboard.py",
        "settings.py",
        "manage.py",
        "urls.py",
    ]

    # Apply autopep8 and pylint to each file
    for file_path in files_to_process:
        apply_autopep8(file_path)
        apply_pylint(file_path)

if __name__ == "__main__":
    main()

