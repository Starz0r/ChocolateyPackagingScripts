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
    logger = logging.getLogger('TweetDuck GitHub Releases')
    logger.setLevel(logging.DEBUG)

    for rel in on_new_git_release("tweetduck.install", "chylex/TweetDuck"):
        # correlate assets
        asset = get_correct_release_asset(rel.get_assets(), "TweetDuck.exe",
                                          None)

        if asset is None:
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
        find_and_replace_templates_new("tweetduck.install", tmpdir, d)
        os.rename(fname, os.path.join(tmpdir, "tools", fname))
        abort_on_nonzero(
            subprocess.call(["choco", "pack",
                             Path(tmpdir) / "tweetduck.install.nuspec"]))


if __name__ == "__main__":
    main()
