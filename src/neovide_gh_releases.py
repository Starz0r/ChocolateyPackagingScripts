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
    logger = logging.getLogger("Neovide GitHub Releases")
    logger.setLevel(logging.DEBUG)

    for rel in on_new_git_release("neovide", "kethku/neovide"):
        # correlate assets
        asset = get_correct_release_asset(
            rel.get_assets(), "neovide.msi", ".tar.gz")

        if asset is None:
            logger.warn(
                "Versioned release missing assets, therefore, ineligible for packaging, skipping."
            )
            continue

        # download and hash
        url = asset.browser_download_url
        fname = asset.name
        abort_on_nonzero(subprocess.call(
            ["wget", url, "--output-document", fname]))
        chksum = checksum.get_for_file(fname, "sha512")
        os.remove(fname)

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
        d = {
            "version": version,
            "tag": gittag,
            "checksum": chksum,
            "fname": fname,
            "url": url,
            "notes": relnotes,
        }

        # template and pack
        tmpdir = tempfile.mkdtemp()
        find_and_replace_templates_new("neovide", tmpdir, d)
        abort_on_nonzero(
            subprocess.call(["choco", "pack", Path(tmpdir) / "neovide.nuspec"])
        )


if __name__ == "__main__":
    main()
