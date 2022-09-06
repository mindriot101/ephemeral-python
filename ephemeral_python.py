#!/usr/bin/env python3


import argparse
import copy
import os
import subprocess as sp
import tempfile
import venv
from pathlib import Path
from types import SimpleNamespace
from typing import List


class EnvBuilder(venv.EnvBuilder):
    def __init__(self, env_dir: Path, packages: List[str]) -> None:
        super().__init__(with_pip=True)
        self.env_dir = env_dir
        self.additional_packages = packages

    def post_setup(self, context: SimpleNamespace) -> None:
        print("Adding packages")
        packages = [
            "IPython",
        ] + self.additional_packages

        self._install_packages(packages)

        return super().post_setup(context)

    def _install_packages(self, packages: List[str]) -> None:
        interpreter_path = self.env_dir / "bin" / "python"
        if not interpreter_path.is_file():
            raise RuntimeError(f"cannot find python interpreter at {interpreter_path}")

        cmd = [
            interpreter_path,
            "-m",
            "pip",
            "install",
        ] + packages
        sp.run(cmd, check=True)

    def run_ipython(self) -> None:
        ipython_path = self.env_dir / "bin" / "ipython"
        if not ipython_path.is_file():
            raise RuntimeError(f"cannot find ipython command at {ipython_path}")

        env = copy.deepcopy(os.environ)
        env["VIRTUAL_ENV"] = str(self.env_dir)

        os.execle(str(ipython_path), str(ipython_path), env)

    def create(self) -> None:
        super().create(self.env_dir)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("package", nargs="*")
    args = parser.parse_args()

    dest = Path(tempfile.mkdtemp(prefix="ephemeral-python-"))
    print(f"Creating venv {dest}")
    builder = EnvBuilder(dest, args.package)
    builder.create()
    builder.run_ipython()
