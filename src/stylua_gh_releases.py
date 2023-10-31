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

PKG_NAME: Final[str] = "stylua"
REPO: Final[str] = "JohnnyMorganz/StyLua"
EXE_NAME: Final[str] = f"{PKG_NAME}.exe"
NUSPEC_NAME: Final[str] = f"{PKG_NAME}.nuspec"
REPO_URL: Final[str] = f"https://github.com/{REPO}"

PKG_DEFS: Final[dict[str, str]] = {
    "id": f"{PKG_NAME}",
    "pkgSrcUrl": "https://github.com/Starz0r/ChocolateyPackagingScripts",
    "owners": "Starz0r",
    "title": "StyLua",
    "authors": "Johnny Morganz",
    "project": "https://github.com/JohnnyMorganz/StyLua",
    "icon": "",
    "copyright": "Copyright © 2020 - 2023, Johnny Morganz",
    "licenseUrl": "",
    "requireLicenseAcceptance": "false",
    "src": f"{REPO_URL}",
    "docs": "",
    "mailingList": "",
    "bugtracker": f"{REPO_URL}/issues",
    "tags": "stylua formatter printer lua oss luajit roblox pretty-printer luau luaformatter rust foss",
    "summary": "An opinionated Lua code formatter",
    "desc": "",
    "notes": "",
    "deps": "",
}


def on_release(rel: GitRelease):
    asset = get_correct_release_asset(
        rel.get_assets(), "-windows-x86_64", "-linux"
    ) or get_correct_release_asset(rel.get_assets(), "-win64", "-linux")

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
    PKG_DEFS["docs"] = f"{REPO_URL}/blob/{gittag}/README.md"

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
