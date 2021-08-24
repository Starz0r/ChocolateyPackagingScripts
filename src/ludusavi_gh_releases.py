import logging
import subprocess
import checksum
import tempfile
import os
from pathlib import Path

from common.common import abort_on_nonzero
from common.events import on_new_git_release
from common.common import get_correct_release_asset
from common.common import find_and_replace_templates_new


def main():
    logger = logging.getLogger('Ludusavi GitHub Releases')
    logger.setLevel(logging.DEBUG)

    for rel in on_new_git_release("ludusavi", "mtkennerly/ludusavi"):
        # correlate assets
        asset = get_correct_release_asset(
                rel.get_assets(), "win32.zip",
                None)
        asset64 = get_correct_release_asset(
                rel.get_assets(), "win64.zip",
                None)

        if asset is None or asset64 is None:
            logger.warn(
                'Versioned release missing required assets, therefore, ineligible for packaging, skipping.'
            )
            continue

        # download and hash
        url = asset.browser_download_url
        fname = asset.name
        abort_on_nonzero(
            subprocess.call(["wget", url, "--output-document", fname]))
        chksum = checksum.get_for_file(fname, "sha512")

        url64 = asset64.browser_download_url
        fname64 = asset64.name
        abort_on_nonzero(
            subprocess.call(["wget", url64, "--output-document", fname64]))
        chksum64 = checksum.get_for_file(fname64, "sha512")

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
                 url=url,
                 checksum=chksum,
                 fname=fname,
                 url64=url64,
                 checksum64=chksum64,
                 fname64=fname64,
                 notes=relnotes)

        # template and pack
        tmpdir = tempfile.mkdtemp()
        find_and_replace_templates_new("ludusavi", tmpdir, d)
        os.rename(fname, os.path.join(tmpdir, "tools", fname))
        os.rename(fname64, os.path.join(tmpdir, "tools", fname64))
        abort_on_nonzero(
            subprocess.call(
                ["choco", "pack",
                 Path(tmpdir) / "ludusavi.nuspec"]))


if __name__ == "__main__":
    main()
