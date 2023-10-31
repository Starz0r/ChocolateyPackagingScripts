import os
import subprocess
import zipfile
from pathlib import Path
from typing import Final

import checksum
from github.GitRelease import GitRelease

from common.common import (TempDir, abort_on_nonzero,
                           find_and_replace_templates_new,
                           get_correct_release_asset)
from common.events import on_new_git_release

PKG_NAME: Final[str] = "selene"
REPO: Final[str] = "Kampfkarren/selene"
EXE_NAME: Final[str] = f"{PKG_NAME}.exe"
NUSPEC_NAME: Final[str] = f"{PKG_NAME}.nuspec"
REPO_URL: Final[str] = f"https://github.com/{REPO}"

PKG_DEFS: Final[dict[str, str]] = {
    "id": f"{PKG_NAME}",
    "pkgSrcUrl": "https://github.com/Starz0r/ChocolateyPackagingScripts",
    "owners": "Starz0r",
    "title": "Selene",
    "authors": "Nathan Riemer",
    "project": "https://kampfkarren.github.io/selene/",
    "icon": "",
    "copyright": "Copyright © 2019 - 2023, Nathan Riemer",
    "licenseUrl": "",
    "requireLicenseAcceptance": "false",
    "src": f"{REPO_URL}",
    "docs": "https://kampfkarren.github.io/selene/",
    "mailingList": "",
    "bugtracker": f"{REPO_URL}/issues",
    "tags": "selene lua oss luajit roblox linter rust foss",
    "summary": "A blazing-fast modern Lua linter written in Rust",
    "desc": "",
    "notes": "",
    "deps": "",
}


def on_release(rel: GitRelease):
    asset = get_correct_release_asset(rel.get_assets(), "-windows", "-linux")

    if asset is None:
        return

    url = asset.browser_download_url
    fname = asset.name
    abort_on_nonzero(subprocess.call(
        ["wget", url, "--output-document", fname]))
    chksum = checksum.get_for_file(fname, "sha512")

    relnotes = rel.body
    if rel.body is None:
        relnotes = ""
    else:
        relnotes = (
            relnotes.replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("&", "&amp;")
            .replace("\u200b", "")  # zero-width space
        )
    version = rel.tag_name.replace("v", "")
    gittag = rel.tag_name
    PKG_DEFS["version"] = version
    PKG_DEFS["tag"] = gittag
    PKG_DEFS["checksum"] = chksum
    PKG_DEFS["fname"] = fname
    PKG_DEFS["url"] = url
    PKG_DEFS["notes"] = relnotes
    PKG_DEFS["licenseUrl"] = f"{REPO_URL}/blob/{gittag}/LICENSE.md"
    PKG_DEFS["release"] = f"{REPO_URL}/releases/tag/{gittag}"
    PKG_DEFS["src"] = f"{REPO_URL}/tree/{gittag}"

    with TempDir() as tmpdir:
        find_and_replace_templates_new(PKG_NAME, tmpdir, PKG_DEFS)
        os.mkdir(Path(tmpdir) / "tools/x64")
        with zipfile.ZipFile(fname) as zf:
            zf.extract(EXE_NAME, os.path.join(tmpdir, "tools/x64"))
        abort_on_nonzero(subprocess.call(["rrr", fname]))
        abort_on_nonzero(subprocess.call(
            ["choco", "pack", Path(tmpdir) / NUSPEC_NAME]))


def main():
    for rel in on_new_git_release(PKG_NAME, REPO):
        on_release(rel)


if __name__ == "__main__":
    main()
