import io
import os
import shutil
import sys
import tempfile
from pathlib import Path
from string import Template
from typing import TYPE_CHECKING, Dict, Iterable, List, Optional, Union

import requests

if TYPE_CHECKING:
    from _typeshed import StrPath

from github.GitReleaseAsset import GitReleaseAsset
from github.PaginatedList import PaginatedList
from jenkinsapi.artifact import Artifact


def get_correct_release_asset(
    assets: PaginatedList, include: str, exclude: Optional[str]
) -> Optional[GitReleaseAsset]:
    if exclude is None:
        for asset in assets:
            if include in asset.name:
                return asset
    else:
        for asset in assets:
            if (include in asset.name) and exclude not in asset.name:
                return asset
    return None


def get_correct_release_artifact(
    assets: Iterable[Artifact], include: str, exclude: Optional[str]
) -> Optional[Artifact]:
    if exclude is None:
        for asset in assets:
            if include in asset.url:
                return asset
    else:
        for asset in assets:
            if (include in asset.url) and exclude not in asset.url:
                return asset
    return None


def get_correct_release_artifact_exclist(
    assets: Iterable[Artifact], include: str, exclude: Optional[List[str]]
) -> Optional[Artifact]:
    if exclude is None:
        for asset in assets:
            if include in asset.url:
                return asset
    else:
        for asset in assets:
            if include in asset.url:
                for exclusion in exclude:
                    if exclusion in asset.url:
                        break
                    return asset
    return None


def find_and_replace_templates(
    package_name: str,
    directory: str,
    version: str,
    tag: str,
    url: str,
    checksum: str,
    fname: Optional[str],
    url64: Optional[str],
    checksum64: Optional[str],
    fname64: Optional[str],
    notes: Optional[str],
) -> None:
    os.mkdir(Path(directory) / "tools")
    os.mkdir(Path(directory) / "tools/x86")
    os.mkdir(Path(directory) / "tools/x64")
    os.mkdir(Path(directory) / "legal")
    d = {
        "version": version,
        "tag": tag,
        "url": url,
        "checksum": checksum,
        "fname": fname,
        "url64": url64,
        "checksum64": checksum64,
        "fname64": fname64,
        "notes": notes,
    }
    basepath = Path(os.getcwd()) / "src/templates/" / package_name
    templates = [
        package_name + ".nuspec",
        "tools/chocolateyinstall.ps1",
        "tools/chocolateyuninstall.ps1",
        "tools/chocolateybeforemodify.ps1",
        "legal/LICENSE.txt",
        "legal/VERIFICATION.txt",
        "tools/LICENSE.txt",
        "tools/VERIFICATION.txt",
    ]

    for template in templates:
        print(template)
        try:
            with io.open(basepath / template, "r", encoding="utf-8-sig") as f:
                contents = f.read()
                temp = Template(contents).safe_substitute(d)
                f = io.open(
                    Path(directory) / template, "a+", encoding="utf-8", errors="ignore"
                )
                f.write(temp)
                f.close()
        except FileNotFoundError as err:
            print("Could not find file to be templated.")
            print(err)
    return


def find_and_replace_templates_new(
    package_name: str, directory: str, d: Dict[str, str]
) -> None:
    try:
        os.mkdir(Path(directory) / "tools")
    except:
        print("Tools directory was not made, continuing on.")

    try:
        os.mkdir(Path(directory) / "legal")
    except:
        print("Legal directory was not made, continuing on.")
    basepath = Path(os.getcwd()) / "src/templates/" / package_name
    templates = [
        package_name + ".nuspec",
        "tools/chocolateyinstall.ps1",
        "tools/chocolateyuninstall.ps1",
        "tools/chocolateybeforemodify.ps1",
        "legal/LICENSE.txt",
        "legal/VERIFICATION.txt",
        "tools/LICENSE.txt",
        "tools/VERIFICATION.txt",
    ]

    for template in templates:
        print(template)
        try:
            with io.open(basepath / template, "r", encoding="utf-8-sig") as f:
                contents = f.read()
                temp = Template(contents).safe_substitute(d)
                f = io.open(
                    Path(directory) / template, "a+", encoding="utf-8", errors="ignore"
                )
                f.write(temp)
                f.close()
        except FileNotFoundError as err:
            print("Could not find file to be templated.")
            print(err)
    return


def find_and_replace_templates_with_default(
    package_name: str, directory: str, d: Dict[str, str]
) -> None:
    try:
        os.mkdir(Path(directory) / "tools")
    except:
        print("Tools directory was not made, continuing on.")

    try:
        os.mkdir(Path(directory) / "legal")
    except:
        print("Legal directory was not made, continuing on.")
    basepath = Path(os.getcwd()) / "src/templates/" / package_name
    templates: list[Union[Path, str]] = [
        Path(os.getcwd()) / "src/templates/default.nuspec",
        "tools/chocolateyinstall.ps1",
        "tools/chocolateyuninstall.ps1",
        "tools/chocolateybeforemodify.ps1",
        "legal/LICENSE.txt",
        "legal/VERIFICATION.txt",
        "tools/LICENSE.txt",
        "tools/VERIFICATION.txt",
    ]

    for template in templates:
        print(template)
        try:
            temp = ""
            with io.open(basepath / template, "r", encoding="utf-8-sig") as f:
                contents = f.read()
                temp = Template(contents).safe_substitute(d)

            p = Path(directory) / template
            if "default.nuspec" in template.__str__():
                p = Path(directory) / f"{package_name}.nuspec"
            with io.open(p, "a+", encoding="utf-8", errors="ignore") as f:
                f.write(temp)
                f.close()
        except FileNotFoundError as err:
            print("Could not find file to be templated.")
            print(err)
    return


def abort_on_nonzero(retcode):
    if retcode != 0:
        sys.exit(retcode)


def escape_text(text: str) -> str:
    return (
        text.replace('"', "&quot;")
        .replace("'", "&apos;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("&", "&amp;")
        .replace("\u200b", "")
    )


def dl_file(url: str, fname: str):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(fname, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
class TempDir:
    td: str = ""

    def __enter__(self, suffix: str = None, prefix: str = None, dir: "StrPath" = None):
        self.td = tempfile.mkdtemp()
        return self.td

    def __str__(self):
        return self.td

    def __exit__(self, suffix: str = None, prefix: str = None, dir: "StrPath" = None):
        shutil.rmtree(self.td)
