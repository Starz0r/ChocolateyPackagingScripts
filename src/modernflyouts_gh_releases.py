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
    logger = logging.getLogger('ModernFlyouts GitHub Releases')
    logger.setLevel(logging.DEBUG)

    for rel in on_new_git_release("modernflyouts", "shankarbus/modernflyouts"):
        # correlate assets
        asset = get_correct_release_asset(rel.get_assets(), ".Msixbundle",
                                          None)

        if asset is None:
            logger.warn(
                "Versioned release missing required assets, therefore, ineligible for packaging, skipping."
            )
            continue

        # download and hash
        url = asset.browser_download_url
        fname = asset.name
        subprocess.call(["wget", url])
        chksum = checksum.get_for_file(fname, "sha512")

        # certificate download
        alturl = "https://github.com/ShankarBUS/ModernFlyouts/releases/download/v0.5.0/ModernFlyouts.Package_0.5.0.0_AnyCPU.cer"
        altfname = "ModernFlyouts.Package_0.5.0.0_AnyCPU.cer" 
        abort_on_nonzero(
                subprocess.call(["wget", alturl, "--output-document", 
                    "ModernFlyouts.Package_0.5.0.0_AnyCPU.cer"]))

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
                 altfname=altfname,
                 notes=relnotes)

        # template and pack
        tmpdir = tempfile.mkdtemp()
        find_and_replace_templates_new("modernflyouts", tmpdir, d)
        os.rename(fname, os.path.join(tmpdir, "tools", fname))
        os.rename(altfname, os.path.join(tmpdir, "tools", altfname))
        abort_on_nonzero(
            subprocess.call(["choco", "pack",
                             Path(tmpdir) / "modernflyouts.nuspec"]))


if __name__ == "__main__":
    main()
