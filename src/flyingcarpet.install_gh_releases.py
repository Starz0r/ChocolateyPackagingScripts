import logging
import subprocess
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
    logger = logging.getLogger("FlyingCarpet (Install) GitHub Releases")
    logger.setLevel(logging.DEBUG)

    for rel in on_new_git_release("flyingcarpet.install", "spieglt/FlyingCarpet"):
        # correlate assets
        asset = get_correct_release_asset(
            rel.get_assets(), "FlyingCarpetWindows.zip", None
        )

        if asset is None:
            logger.warn(
                "Versioned release missing required assets, therefore, ineligible for packaging, skipping."
            )
            continue

        # download, and hash
        unpackdir = tempfile.mkdtemp()
        url = asset.browser_download_url
        fname = asset.name
        abort_on_nonzero(subprocess.call(["wget", url, "--output-document", fname]))
        archive = zipfile.ZipFile(fname)
        archive.extractall(unpackdir)
        archive.close()
        chksum = checksum.get_for_file(fname, "sha512")
        os.remove(fname)
        os.rename(unpackdir + "/flyingcarpet.exe", unpackdir + "/flyingcarpetw.exe")

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
        find_and_replace_templates_new("flyingcarpet.install", tmpdir, d)
        # HACK: Python is dumb and won't recursively create directories sometimes, why...
        # os.mkdir(Path(tmpdir) / "tools")
        os.rename(unpackdir, os.path.join(tmpdir, "tools", "x64"))
        abort_on_nonzero(
            subprocess.call(
                ["choco", "pack", Path(tmpdir) / "flyingcarpet.install.nuspec"]
            )
        )


if __name__ == "__main__":
    main()
