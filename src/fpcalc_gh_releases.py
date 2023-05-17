import os
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Final

import checksum
from github.GitRelease import GitRelease

from common.common import (abort_on_nonzero,
                           find_and_replace_templates_with_default,
                           get_correct_release_asset)
from common.events import on_new_git_release

PKG_NAME: Final[str] = "fpcalc"
REPO: Final[str] = "acoustid/chromaprint"
EXE_NAME: Final[str] = f"{PKG_NAME}.exe"
NUSPEC_NAME: Final[str] = f"{PKG_NAME}.nuspec"
REPO_URL: Final[str] = f"https://github.com/{REPO}"

PKG_DEFS: Final[dict[str, str]] = {
    "id": f"{PKG_NAME}",
    "pkgSrcUrl": "https://github.com/Starz0r/ChocolateyPackagingScripts",
    "owners": "Starz0r",
    "title": "fpcalc",
    "authors": "Lukáš Lalinský &amp; AcoustID",
    "project": "https://acoustid.org/chromaprint",
    "icon": "https://avatars.githubusercontent.com/u/19508937",
    "copyright": "Copyright © 2010 - 2023, Lukáš Lalinský",
    "licenseUrl": "",
    "requireLicenseAcceptance": "false",
    "src": f"{REPO_URL}",
    "docs": "",
    "mailingList": "",
    "bugtracker": f"{REPO_URL}/issues",
    "tags": "fpcalc chromaprint acoustid oss foss cli audio fingerprint fingerprinting sound music",
    "summary": "Generate audio fingerprints from the terminal.",
    "desc": "fpcalc is a utility for generating fingerprints from audio sources programatically. It can produce JSON output, which should be easy to parse in any language. This is the recommended way to use Chromaprint if all you need is generate fingerprints for AcoustID.",
    "notes": "",
    "deps": "",
}


def on_release(rel: GitRelease):
    asset = get_correct_release_asset(
        rel.get_assets(), "-windows-x86_64", None)

    if asset is None:
        return

    url = asset.browser_download_url
    fname = asset.name
    abort_on_nonzero(subprocess.call(
        ["wget", url, "--output-document", fname]))
    chksum = checksum.get_for_file(fname, "sha512")
    with zipfile.ZipFile(fname) as zf:
        for member in zf.infolist():
            if "fpcalc.exe" in member.filename:
                with open(EXE_NAME, "wb") as f:
                    f.write(zf.read(member))
    abort_on_nonzero(subprocess.call(["rrr", fname]))

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
    PKG_DEFS["fname"] = EXE_NAME
    PKG_DEFS["url"] = url
    PKG_DEFS["notes"] = relnotes
    PKG_DEFS["licenseUrl"] = f"{REPO_URL}/blob/{gittag}/LICENSE.md"
    PKG_DEFS["release"] = f"{REPO_URL}/releases/tag/{gittag}"
    PKG_DEFS["src"] = f"{REPO_URL}/tree/{gittag}"
    PKG_DEFS["docs"] = f"{REPO_URL}/blob/{gittag}/README.md"

    tmpdir = tempfile.mkdtemp()
    find_and_replace_templates_with_default(PKG_NAME, tmpdir, PKG_DEFS)
    os.mkdir(Path(tmpdir) / "tools/x64")
    os.rename(EXE_NAME, os.path.join(tmpdir, "tools/x64", EXE_NAME))
    abort_on_nonzero(subprocess.call(
        ["choco", "pack", Path(tmpdir) / NUSPEC_NAME]))


def main():
    for rel in on_new_git_release(PKG_NAME, REPO):
        on_release(rel)


if __name__ == "__main__":
    main()
