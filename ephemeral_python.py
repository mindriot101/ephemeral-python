#!/usr/bin/env python3


import argparse
import copy
import hashlib
import os
import shutil
import subprocess as sp
import sys
import threading
import time
import venv
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import List

from xdg import xdg_data_home


class Spinner:
    """
    https://stackoverflow.com/a/39504463
    """

    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1:
            for cursor in "|/-\\":
                yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay):
            self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write("\b")
            sys.stdout.flush()

    def __enter__(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def __exit__(self, exception, value, tb):
        self.busy = False
        time.sleep(self.delay)
        if exception is not None:
            return False


@dataclass
class Args:
    package: List[str]
    recreate: bool
    update: bool


class EnvBuilder(venv.EnvBuilder):
    def __init__(
        self, env_dir: Path, packages: List[str], update: bool, recreate: bool
    ) -> None:
        super().__init__(with_pip=True)

        self.env_dir = env_dir
        self.packages = packages
        self.update = update
        self.recreate = recreate

    def post_setup(self, context: SimpleNamespace) -> None:
        self._install_packages()

        return super().post_setup(context)

    def _install_packages(self) -> None:
        interpreter_path = self.env_dir / "bin" / "python"
        if not interpreter_path.is_file():
            raise RuntimeError(f"cannot find python interpreter at {interpreter_path}")

        cmd = [
            interpreter_path,
            "-m",
            "pip",
            "install",
        ]
        if self.update:
            cmd.append("-U")

        cmd.extend(self.packages)
        sp.run(cmd, check=True, stdout=sp.PIPE, stderr=sp.PIPE)

    def run_ipython(self) -> None:
        ipython_path = self.env_dir / "bin" / "ipython"
        if not ipython_path.is_file():
            raise RuntimeError(f"cannot find ipython command at {ipython_path}")

        env = copy.deepcopy(os.environ)
        env["VIRTUAL_ENV"] = str(self.env_dir)

        os.execle(str(ipython_path), str(ipython_path), env)

    def create(self) -> None:
        if self.env_dir.is_dir() and not self.recreate:
            return

        with Spinner():
            if self.recreate:
                shutil.rmtree(self.env_dir)

            super().create(self.env_dir)


def compute_package_list_hash(package_list: List[str]) -> str:
    hasher = hashlib.md5()

    for package in package_list:
        hasher.update(package.encode("utf8"))

    return hasher.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("package", nargs="*")
    parser.add_argument("-r", "--recreate", action="store_true", default=False)
    parser.add_argument("-u", "--update", action="store_true", default=False)
    args = parser.parse_args()

    all_packages = sorted(
        list(set(["ipython"] + [every.lower() for every in args.package]))
    )

    # re-usable environments
    package_list_hash = compute_package_list_hash(all_packages)

    dest = (
        Path(xdg_data_home())
        / "ephemeral-python-venvs"
        / f"ephemeral-python-{package_list_hash}"
    )

    builder = EnvBuilder(
        env_dir=dest, packages=all_packages, recreate=args.recreate, update=args.update
    )
    builder.create()
    builder.run_ipython()
