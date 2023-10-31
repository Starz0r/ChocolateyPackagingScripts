import os
import subprocess
from pathlib import Path
from typing import Final

import checksum
from github.GitRelease import GitRelease

from common.common import (TempDir, abort_on_nonzero,
                           find_and_replace_templates_new,
                           get_correct_release_asset)
from common.events import on_new_git_release

PKG_NAME: Final[str] = "lua-language-server"
REPO: Final[str] = "LuaLS/lua-language-server"
EXE_NAME: Final[str] = f"{PKG_NAME}.exe"
NUSPEC_NAME: Final[str] = f"{PKG_NAME}.nuspec"
REPO_URL: Final[str] = f"https://github.com/{REPO}"

PKG_DEFS: Final[dict[str, str]] = {
    "id": f"{PKG_NAME}",
    "pkgSrcUrl": "https://github.com/Starz0r/ChocolateyPackagingScripts",
    "owners": "Starz0r",
    "title": "Lua Language Server",
    "authors": "孙 颐久 &amp; LuaLS Contributors",
    "project": "https://github.com/LuaLS/lua-language-server",
    "icon": "https://upload.wikimedia.org/wikipedia/commons/c/cf/Lua-Logo.svg",
    "copyright": "Copyright © 2018 - 2023, 孙 颐久",
    "licenseUrl": "",
    "requireLicenseAcceptance": "false",
    "src": f"{REPO_URL}",
    "docs": "https://github.com/LuaLS/lua-language-server/wiki",
    "mailingList": "",
    "bugtracker": f"{REPO_URL}/issues",
    "tags": "lua-language-server oss lua language-server lpeg lsp lsp-server lpeglabel luajit foss",
    "summary": "A language server that offers Lua language support - programmed in Lua",
    "desc": "",
    "notes": "",
    "deps": "",
}


def on_release(rel: GitRelease):
    asset = get_correct_release_asset(rel.get_assets(), "-win32-ia32", "linux")
    asset64 = get_correct_release_asset(rel.get_assets(), "-win32-x64", "linux")

    if asset is None or asset64 is None:
        return

    url = asset.browser_download_url
    fname = asset.name
    abort_on_nonzero(subprocess.call(["wget", url, "--output-document", fname]))
    chksum = checksum.get_for_file(fname, "sha512")

    url64 = asset64.browser_download_url
    fname64 = asset64.name
    abort_on_nonzero(subprocess.call(["wget", url64, "--output-document", fname64]))
    chksum64 = checksum.get_for_file(fname64, "sha512")

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
    PKG_DEFS["checksum64"] = chksum64
    PKG_DEFS["fname64"] = fname64
    PKG_DEFS["url64"] = url64
    PKG_DEFS["notes"] = relnotes
    PKG_DEFS["licenseUrl"] = f"{REPO_URL}/blob/{gittag}/LICENSE"
    PKG_DEFS["release"] = f"{REPO_URL}/releases/tag/{gittag}"
    PKG_DEFS["src"] = f"{REPO_URL}/tree/{gittag}"

    with TempDir() as tmpdir:
        find_and_replace_templates_new(PKG_NAME, tmpdir, PKG_DEFS)
        os.mkdir(Path(tmpdir) / "tools/x64")
        os.mkdir(Path(tmpdir) / "tools/x86")
        os.rename(fname, os.path.join(tmpdir, "tools/x86", fname))
        os.rename(fname64, os.path.join(tmpdir, "tools/x64", fname64))
        abort_on_nonzero(subprocess.call(["choco", "pack", Path(tmpdir) / NUSPEC_NAME]))


def main():
    for rel in on_new_git_release(PKG_NAME, REPO):
        on_release(rel)


if __name__ == "__main__":
    main()
