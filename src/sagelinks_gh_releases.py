import logging
import subprocess
import tempfile
import os
import checksum
from pathlib import Path

from common.common import abort_on_nonzero
from common.events import on_new_git_release
from common.common import get_correct_release_asset
from common.common import find_and_replace_templates_new


def main() -> int:
    logger = logging.getLogger("SageLinks GitHub Releases")
    logger.setLevel(logging.DEBUG)

    for rel in on_new_git_release("sagelinks", "raspopov/SageLinks"):
        # correlate assets
        asset = get_correct_release_asset(rel.get_assets(), "32-bit", "64-bit")
        asset64 = get_correct_release_asset(rel.get_assets(), "64-bit", "32-bit")

        if asset is None or asset64 is None:
            logger.warn(
                "Versioned release missing required assets, therefore, ineligible for packaging, skipping."
            )
            continue

        # download and hash
        url = asset.browser_download_url
        fname = asset.name
        abort_on_nonzero(subprocess.call(["wget", url, "--output-document", fname]))
        chksum = checksum.get_for_file(fname, "sha512")
        os.rename(fname, "sagelinks_i686.exe")
        fname = "sagelinks_i686.exe"

        url64 = asset64.browser_download_url
        fname64 = asset64.name
        abort_on_nonzero(subprocess.call(["wget", url64, "--output-document", fname64]))
        chksum64 = checksum.get_for_file(fname64, "sha512")
        os.rename(fname64, "sagelinks_amd64.exe")
        fname64 = "sagelinks_amd64.exe"

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
            checksum=chksum,
            fname=fname,
            checksum64=chksum64,
            fname64=fname64,
            url=url,
            url64=url64,
            notes=relnotes,
        )

        # template and pack
        tmpdir = tempfile.mkdtemp()
        find_and_replace_templates_new("sagelinks", tmpdir, d)
        os.rename(fname, os.path.join(tmpdir, "tools", fname))
        os.rename(fname64, os.path.join(tmpdir, "tools", fname64))
        abort_on_nonzero(
            subprocess.call(["choco", "pack", Path(tmpdir) / "sagelinks.nuspec"])
        )

    return 0


if __name__ == "__main__":
    main()
