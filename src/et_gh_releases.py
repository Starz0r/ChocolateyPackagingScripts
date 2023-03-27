import logging
import subprocess
import urllib.request
import checksum
import tempfile
import os
from pathlib import Path

from common.common import abort_on_nonzero
from common.events import on_new_git_release
from common.common import get_correct_release_asset
from common.common import find_and_replace_templates_new


def main():
    logger = logging.getLogger('et GitHub Releases')
    logger.setLevel(logging.DEBUG)

    for rel in on_new_git_release("et", "solidiquis/erdtree"):
        # correlate assets
        asset = get_correct_release_asset(rel.get_assets(), ".exe",
                                          ".tar.gz")

        if asset is None:
            logger.warn(
                "Versioned release missing required assets, therefore, ineligible for packaging, skipping."
            )
            continue

        # download and hash
        url = asset.browser_download_url
        fname = asset.name
        urllib.request.urlretrieve(url, fname)
        chksum = checksum.get_for_file(fname)
        os.rename(fname, "et.exe")
        fname = "et.exe"

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
                 fname=fname,
                 url=url,
                 notes=relnotes)

        # template and pack
        tmpdir = tempfile.mkdtemp()
        find_and_replace_templates_new("et", tmpdir, d)
        # HACK: Python is dumb and won't recursively create directories sometimes, why...
        os.mkdir(Path(tmpdir) / "tools/x64")
        os.rename(fname, os.path.join(tmpdir, "tools", "x64", fname))
        abort_on_nonzero(
            subprocess.call(["choco", "pack",
                             Path(tmpdir) / "et.nuspec"]))


if __name__ == "__main__":
    main()
