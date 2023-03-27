import logging
import subprocess
import gzip
import checksum
import tempfile
import shutil
import os
from pathlib import Path

from common.common import abort_on_nonzero
from common.events import on_new_git_release
from common.common import get_correct_release_asset
from common.common import find_and_replace_templates_new


def main():
    logger = logging.getLogger("jwtinfo GitHub Releases")
    logger.setLevel(logging.DEBUG)

    for rel in on_new_git_release("jwtinfo", "lmammino/jwtinfo"):
        # correlate assets
        asset = get_correct_release_asset(
            rel.get_assets(), "jwtinfo-win64.exe.gz", None
        )

        if asset is None:
            logger.warn(
                "Versioned release missing required assets, therefore, ineligible for packaging, skipping."
            )
            continue

        # download, unzip, and hash
        url = asset.browser_download_url
        fname = asset.name
        abort_on_nonzero(subprocess.call(["wget", url, "--output-document", fname]))
        with gzip.open(fname, "rb") as f:
            with open("jwtinfo.exe", "wb") as out:
                shutil.copyfileobj(f, out)
        os.remove(fname)
        fname = "jwtinfo.exe"
        chksum = checksum.get_for_file(fname, "sha512")

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
        version = rel.tag_name.strip("v").replace("-", ".")
        gittag = rel.tag_name
        d = dict(
            version=version,
            tag=gittag,
            checksum=chksum,
            fname=fname,
            url=url,
            notes=relnotes,
        )

        # template and pack
        tmpdir = tempfile.mkdtemp()
        find_and_replace_templates_new("jwtinfo", tmpdir, d)
        # HACK: Python is dumb and won't recursively create directories sometimes, why...
        os.mkdir(Path(tmpdir) / "tools/x64")
        os.rename(fname, os.path.join(tmpdir, "tools", "x64", fname))
        abort_on_nonzero(
            subprocess.call(["choco", "pack", Path(tmpdir) / "jwtinfo.nuspec"])
        )


if __name__ == "__main__":
    main()
