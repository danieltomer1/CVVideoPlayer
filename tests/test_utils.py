import os
import sys
from pathlib import Path


def change_cwd_to_tests_dir():
    os.chdir(str(Path(__file__).absolute().parent))


def add_project_root_to_path():
    sys.path.append(str(Path(__file__).absolute().parent.parent))
