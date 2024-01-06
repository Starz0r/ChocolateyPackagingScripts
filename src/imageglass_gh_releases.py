import logging
import os
import subprocess
import tempfile
from pathlib import Path

import checksum

from common.common import (abort_on_nonzero, find_and_replace_templates_new,
                           get_correct_release_asset)
from common.events import on_new_git_release


def main():
    logger = logging.getLogger("ImageGlass GitHub Releases")
    logger.setLevel(logging.DEBUG)

    for rel in on_new_git_release("imageglass", "d2phap/imageglass"):
        # correlate assets
        asset64 = get_correct_release_asset(rel.get_assets(), "_x64.msi", None)

        if asset64 is None:
            logger.warn(
                "Versioned release missing required assets, therefore, ineligible for packaging, skipping."
            )
            continue

        # download and hash
        url64 = asset64.browser_download_url
        fname64 = asset64.name
        abort_on_nonzero(subprocess.call(
            ["wget", url64, "--output-document", fname64]))
        chksum64 = checksum.get_for_file(fname64, "sha512")

        # assemble information
        relnotes = rel.body
        if rel.body is None:
            relnotes = ""
        else:
            relnotes = (
                relnotes.replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("&", "&amp;")
                .replace("\u200b", "")
            )  # zero-width space

        version = rel.tag_name.replace("v", "")
        gittag = rel.tag_name
        d = dict(
            version=version,
            tag=gittag,
            checksum64=chksum64,
            fname64=fname64,
            url64=url64,
            notes=relnotes,
        )

        # template and pack
        tmpdir = tempfile.mkdtemp()
        find_and_replace_templates_new("imageglass", tmpdir, d)
        os.rename(fname64, os.path.join(tmpdir, "tools", fname64))
        abort_on_nonzero(
            subprocess.call(
                ["choco", "pack", Path(tmpdir) / "imageglass.nuspec"])
        )


if __name__ == "__main__":
    main()
