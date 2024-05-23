#!/usr/bin/env python3

import hashlib
from pathlib import Path
import re
import argparse


def entry_exists(index_path: Path, entry: str) -> bool:
    with index_path.open("r") as f:
        return any(entry in line for line in f)


def append_entry(index_path: Path, new_line: str):
    with index_path.open("a") as f:
        f.write(new_line)


def create_index_file(pkg_path: Path):
    path = Path()
    for dir in str(pkg_path).split("/"):
        index_path = path / "index.html"
        if not index_path.exists():
            index_path.write_text("<!DOCTYPE html>")

        if not entry_exists(index_path, f'>{dir}<'):
            new_line = f'\n<a href="{dir}">{dir}</a><br>'
            append_entry(index_path, new_line)
        path /= dir


def publish_entry(
    index_path: Path, whl_file_name: str, pkg: str, ver: str, whl_path: Path
):
    print(f"Publishing {whl_file_name} to {index_path}")
    sha256 = hashlib.sha256(whl_path.read_bytes()).hexdigest()
    new_line = (
        f'\n<a href="https://github.com/vectorch-ai/{pkg}/releases/download/v{ver}/'
        f'{whl_file_name}#sha256={sha256}">{whl_file_name}</a><br>'
    )
    append_entry(index_path, new_line)


def publish_whl(whls_path: str):
    whl_files = sorted(Path(whls_path).glob("*.whl"))

    for whl_path in whl_files:
        whl_file_name = whl_path.name
        pkg, ver, cu, torch = re.findall(
            r"(.+)-([0-9.]+)\+cu(\d+)torch([0-9.]+)-", whl_file_name
        )[0]

        pkg_path = Path(f"cu{cu}/torch{torch}/{pkg}")
        pkg_path.mkdir(parents=True, exist_ok=True)

        create_index_file(pkg_path)

        index_path = pkg_path / "index.html"
        if not index_path.exists():
            index_path.write_text("<!DOCTYPE html>")
        if not entry_exists(index_path, f">{whl_file_name}<"):
            publish_entry(index_path, whl_file_name, pkg, ver, whl_path)
        else:
            print(f"{whl_file_name} already exists in {index_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--whl_path", type=str, default="dist", help="Path to .whl files"
    )
    args = parser.parse_args()

    publish_whl(args.whl_path)
