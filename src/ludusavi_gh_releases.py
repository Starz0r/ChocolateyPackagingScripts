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
    logger = logging.getLogger('Ludusavi GitHub Releases')
    logger.setLevel(logging.DEBUG)

    looped_back = False

    asset = None
    asset64 = None
    altasset = None
    altasset64 = None

    for rel in on_new_git_release("ludusavi", "mtkennerly/ludusavi"):
        # correlate assets
        if asset is None:
            asset = get_correct_release_asset(
                rel.get_assets(), "win32.zip",
                "opengl")
        if asset64 is None:
            asset64 = get_correct_release_asset(
                rel.get_assets(), "win64.zip",
                "opengl")
        if altasset is None:
            altasset = get_correct_release_asset(
                rel.get_assets(), "+opengl-win32", "linux")
        if altasset64 is None:
            altasset64 = get_correct_release_asset(
                rel.get_assets(), "+opengl-win64.zip", "linux")

        if looped_back is False:
            print(asset)
            print(asset64)
            print(altasset)
            print(altasset64)
            looped_back = True
            continue

        if asset is None or asset64 is None or altasset is None or altasset64 is None:
            logger.warn(
                'Versioned release missing required assets, therefore, ineligible for packaging, skipping.'
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
                 url=url,
                 checksum=chksum,
                 fname=fname,
                 url64=url64,
                 checksum64=chksum64,
                 fname64=fname64,
                 alturl=alturl,
                 altchecksum=altchksum,
                 altfname=altfname,
                 alturl64=alturl64,
                 altchecksum64=altchksum64,
                 altfname64=altfname64,
                 notes=relnotes)

        # template and pack
        tmpdir = tempfile.mkdtemp()
        find_and_replace_templates_new("ludusavi", tmpdir, d)
        os.rename(fname, os.path.join(tmpdir, "tools", fname))
        os.rename(fname64, os.path.join(tmpdir, "tools", fname64))
        os.rename(altfname, os.path.join(tmpdir, "tools", altfname))
        os.rename(altfname64, os.path.join(tmpdir, "tools", altfname64))
        abort_on_nonzero(
            subprocess.call(
                ["choco", "pack",
                 Path(tmpdir) / "ludusavi.nuspec"]))

        # reset variables
        looped_back = False
        asset = None
        asset64 = None
        altasset = None
        altasset64 = None


if __name__ == "__main__":
    main()
