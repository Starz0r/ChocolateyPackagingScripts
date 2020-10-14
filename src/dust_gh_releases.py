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
    logger = logging.getLogger('dust GitHub Releases')
    logger.setLevel(logging.DEBUG)

    for rel in on_new_git_release("dust", "bootandy/dust"):
        # correlate assets
        asset = get_correct_release_asset(rel.get_assets(),
                                          "i686-pc-windows-msvc", "linux")
        asset64 = get_correct_release_asset(rel.get_assets(),
                                            "x86_64-pc-windows-msvc", "linux")
        altasset = get_correct_release_asset(rel.get_assets(),
                                             "i686-pc-windows-gnu", "linux")
        altasset64 = get_correct_release_asset(rel.get_assets(),
                                               "x86_64-pc-windows-gnu",
                                               "linux")

        if asset is None or asset64 is None or altasset is None or altasset64 is None:
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
        fname64 = asset64.name
        abort_on_nonzero(
            subprocess.call(["wget", url64, "--output-document", fname64]))
        chksum64 = checksum.get_for_file(fname64, "sha512")

        alturl = altasset.browser_download_url
        altfname = altasset.name
        abort_on_nonzero(
            subprocess.call(["wget", alturl, "--output-document", altfname]))
        altchksum = checksum.get_for_file(altfname, "sha512")

        alturl64 = altasset64.browser_download_url
        altfname64 = altasset64.name
        abort_on_nonzero(
            subprocess.call(
                ["wget", alturl64, "--output-document", altfname64]))
        altchksum64 = checksum.get_for_file(altfname64, "sha512")

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
                 checksum64=chksum64,
                 fname64=fname64,
                 url64=url64,
                 altchecksum=altchksum,
                 altfname=altfname,
                 alturl=alturl,
                 altchecksum64=altchksum64,
                 altfname64=altfname64,
                 alturl64=alturl64,
                 notes=relnotes)

        # template and pack
        tmpdir = tempfile.mkdtemp()
        find_and_replace_templates_new("dust", tmpdir, d)
        os.rename(fname, os.path.join(tmpdir, "tools", fname))
        os.rename(fname64, os.path.join(tmpdir, "tools", fname64))
        os.rename(altfname, os.path.join(tmpdir, "tools", altfname))
        os.rename(altfname64, os.path.join(tmpdir, "tools", altfname64))
        abort_on_nonzero(
            subprocess.call(["choco", "pack",
                             Path(tmpdir) / "dust.nuspec"]))


if __name__ == "__main__":
    main()
