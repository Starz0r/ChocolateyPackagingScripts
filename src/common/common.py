from github.PaginatedList import PaginatedList
from github.GitReleaseAsset import GitReleaseAsset
from github import Github

from typing import Optional, Dict
from pathlib import Path
import os
import sys
import io
from string import Template


def get_correct_release_asset(
        assets: PaginatedList, include: str,
        exclude: Optional[str]) -> Optional[GitReleaseAsset]:
    if exclude is None:
        for asset in assets:
            if (include in asset.name):
                return asset
    else:
        for asset in assets:
            if (include in asset.name) and not (exclude in asset.name):
                return asset
    return None


def find_and_replace_templates(package_name: str, directory: str, version: str,
                               tag: str, url: str, checksum: str,
                               fname: Optional[str], url64: Optional[str],
                               checksum64: Optional[str],
                               fname64: Optional[str],
                               notes: Optional[str]) -> None:
    os.mkdir(Path(directory) / "tools")
    os.mkdir(Path(directory) / "tools/x86")
    os.mkdir(Path(directory) / "tools/x64")
    os.mkdir(Path(directory) / "legal")
    d = dict(version=version,
             tag=tag,
             url=url,
             checksum=checksum,
             fname=fname,
             url64=url64,
             checksum64=checksum64,
             fname64=fname64,
             notes=notes)
    basepath = Path(os.getcwd()) / "src/templates/" / package_name
    templates = [
        package_name + ".nuspec", "tools/chocolateyinstall.ps1",
        "tools/chocolateyuninstall.ps1", "tools/chocolateybeforemodify.ps1",
        "legal/LICENSE.txt", "legal/VERIFICATION.txt", "tools/LICENSE.txt",
        "tools/VERIFICATION.txt"
    ]

    for template in templates:
        print(template)
        try:
            with io.open(basepath / template, "r", encoding="utf-8-sig") as f:
                contents = f.read()
                temp = Template(contents).safe_substitute(d)
                f = io.open(Path(directory) / template,
                            "a+",
                            encoding="utf-8",
                            errors="ignore")
                f.write(temp)
                f.close()
        except FileNotFoundError as err:
            print("Could not find file to be templated.")
            print(err)
    return


def find_and_replace_templates_new(package_name: str, directory: str,
                                   d: Dict[str, str]) -> None:
    os.mkdir(Path(directory) / "tools")
    os.mkdir(Path(directory) / "legal")
    basepath = Path(os.getcwd()) / "src/templates/" / package_name
    templates = [
        package_name + ".nuspec", "tools/chocolateyinstall.ps1",
        "tools/chocolateyuninstall.ps1", "tools/chocolateybeforemodify.ps1",
        "legal/LICENSE.txt", "legal/VERIFICATION.txt", "tools/LICENSE.txt",
        "tools/VERIFICATION.txt"
    ]

    for template in templates:
        print(template)
        try:
            with io.open(basepath / template, "r", encoding="utf-8-sig") as f:
                contents = f.read()
                temp = Template(contents).safe_substitute(d)
                f = io.open(Path(directory) / template,
                            "a+",
                            encoding="utf-8",
                            errors="ignore")
                f.write(temp)
                f.close()
        except FileNotFoundError as err:
            print("Could not find file to be templated.")
            print(err)
    return


def abort_on_nonzero(retcode):
    if (retcode != 0):
        sys.exit(retcode)
