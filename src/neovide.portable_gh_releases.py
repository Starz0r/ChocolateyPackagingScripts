import logging
import subprocess
import checksum
import tempfile
import os
import zipfile
from pathlib import Path

from common.common import abort_on_nonzero
from common.events import on_new_git_release
from common.common import get_correct_release_asset
from common.common import find_and_replace_templates_new


def main():
    logger = logging.getLogger('Neovide GitHub Releases')
    logger.setLevel(logging.DEBUG)

    for rel in on_new_git_release("neovide.portable", "kethku/neovide"):
        # correlate assets
        asset = get_correct_release_asset(rel.get_assets(), "neovide-windows",
                                          "installer")

        if asset is None:
            logger.warn(
                "Versioned release missing assets, therefore, ineligible for packaging, skipping."
            )
            continue

        # download and hash
        url = asset.browser_download_url
        fname = asset.name
        abort_on_nonzero(
            subprocess.call(["wget", url, "--output-document", fname]))
        f = zipfile.ZipFile(fname)
        f.extractall()
        fname = f.namelist()[0]
        f.close()
        os.remove(asset.name)
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
        find_and_replace_templates_new("neovide.portable", tmpdir, d)
        os.mkdir(Path(tmpdir) / "tools/x64")
        os.rename(fname, os.path.join(tmpdir, "tools/x64", fname))
        abort_on_nonzero(
            subprocess.call(["choco", "pack",
                             Path(tmpdir) / "neovide.portable.nuspec"]))


if __name__ == "__main__":
    main()
