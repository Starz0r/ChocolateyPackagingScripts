import logging
import subprocess
import urllib.request
import zipfile
import checksum
import tempfile
import os
from pathlib import Path

from common.common import abort_on_nonzero
from common.events import on_new_git_release
from common.common import get_correct_release_asset
from common.common import find_and_replace_templates_new


def main():
    logger = logging.getLogger('ruff GitHub Releases')
    logger.setLevel(logging.DEBUG)

    for rel in on_new_git_release("ruff", "charliermarsh/ruff"):
        # correlate assets
        asset = get_correct_release_asset(rel.get_assets(), "i686-pc-windows-msvc",
                                          ".tar.gz")
        asset64 = get_correct_release_asset(rel.get_assets(), "x86_64-pc-windows-msvc",
                                          ".tar.gz")

        if asset is None or asset64 is None:
            logger.warn(
                "Versioned release missing required assets, therefore, ineligible for packaging, skipping."
            )
            continue

        # download and hash
        url = asset.browser_download_url
        fname = asset.name
        urllib.request.urlretrieve(url, fname)
        with zipfile.ZipFile(fname) as zipf:
            zipf.extractall()
            fname = zipf.namelist()[0]
        chksum = checksum.get_for_file(fname)
        os.rename(fname, "ruff-x86.exe") # HACK: need to prevent future filename collisions
        fname = "ruff-x86.exe"
        abort_on_nonzero(subprocess.call(["rrr", asset.name]))

        url64 = asset64.browser_download_url
        fname64 = asset64.name
        urllib.request.urlretrieve(url64, fname64)
        with zipfile.ZipFile(fname64) as zipf64:
            zipf64.extractall()
            fname64 = zipf64.namelist()[0]
        chksum64 = checksum.get_for_file(fname64)
        os.rename(fname64, "ruff-x64.exe") # HACK: need to prevent future filename collisions
        fname64 = "ruff-x64.exe"
        abort_on_nonzero(subprocess.call(["rrr", asset64.name]))


        # assemble information
        relnotes = rel.body
        if rel.body is None:
            relnotes = ""
        else:
            relnotes = relnotes.replace("<", "&lt;").replace(
                ">", "&gt;").replace("&",
                                     "&amp;").replace("\u200b",
                                                      "")  # zero-width space
        version = rel.tag_name.replace("v", "")
        gittag = rel.tag_name
        d = dict(version=version,
                 tag=gittag,
                 checksum=chksum,
                 checksum64=chksum64,
                 fname=fname,
                 fname64=fname64,
                 url=url,
                 url64=url64,
                 notes=relnotes)

        # template and pack
        tmpdir = tempfile.mkdtemp()
        find_and_replace_templates_new("ruff", tmpdir, d)
        # HACK: Python is dumb and won't recursively create directories sometimes, why...
        os.mkdir(Path(tmpdir) / "tools/x64")
        os.mkdir(Path(tmpdir) / "tools/x86")
        os.rename(fname, os.path.join(tmpdir, "tools", "x86", "ruff.exe"))
        os.rename(fname64, os.path.join(tmpdir, "tools", "x64", "ruff.exe"))
        abort_on_nonzero(
            subprocess.call(["choco", "pack",
                             Path(tmpdir) / "ruff.nuspec"]))


if __name__ == "__main__":
    main()
