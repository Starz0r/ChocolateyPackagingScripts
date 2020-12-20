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
    logger = logging.getLogger('youtube-dlc GitHub Releases')
    logger.setLevel(logging.DEBUG)

    for rel in on_new_git_release("youtube-dlc", "blackjack4494/yt-dlc"):
        # correlate assets
        asset = get_correct_release_asset(rel.get_assets(),
                                          "youtube-dlc_x86.exe", None)
        asset64 = get_correct_release_asset(rel.get_assets(),
                                            "youtube-dlc.exe", None)

        if asset is None or asset64 is None:
            logger.warn(
                "Versioned release missing required assets, therefore, ineligible for packaging, skipping."
            )
            continue

        # download and hash
        url = asset.browser_download_url
        fname = asset.name
        abort_on_nonzero(
            subprocess.call(["wget", url, "--output-document", fname]))
        chksum = checksum.get_for_file(fname, "sha512")

        url64 = asset64.browser_download_url
        fname64 = "youtube-dlc_x86_64.exe"  # override the file name so it doesn't collide in the install script
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
        version = rel.tag_name.strip("v").replace("-", ".")
        gittag = rel.tag_name
        d = dict(version=version,
                 tag=gittag,
                 checksum=chksum,
                 fname=fname,
                 url=url,
                 checksum64=chksum64,
                 fname64=fname64,
                 url64=url64,
                 notes=relnotes)

        # template and pack
        tmpdir = tempfile.mkdtemp()
        find_and_replace_templates_new("youtube-dlc", tmpdir, d)
		# HACK: Python is dumb and won't recursively create directories sometimes, why...
        os.mkdir(Path(tmpdir) / "tools/x86")
        os.mkdir(Path(tmpdir) / "tools/x64")
        os.rename(fname, os.path.join(tmpdir, "tools", "x86", "youtube-dlc.exe"))
        os.rename(fname64, os.path.join(tmpdir, "tools", "x64", "youtube-dlc.exe"))
        abort_on_nonzero(
            subprocess.call(
                ["choco", "pack",
                 Path(tmpdir) / "youtube-dlc.nuspec"]))


if __name__ == "__main__":
    main()
