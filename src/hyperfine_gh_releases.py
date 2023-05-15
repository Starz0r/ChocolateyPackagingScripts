import logging
import os
import subprocess
import tempfile
import zipfile
from pathlib import Path

import checksum

from common.common import (abort_on_nonzero, find_and_replace_templates_new,
                           get_correct_release_asset)
from common.events import on_new_git_release


def main():
    logger = logging.getLogger("hyperfine GitHub Releases")
    logger.setLevel(logging.DEBUG)

    for rel in on_new_git_release("hyperfine", "sharkdp/hyperfine"):
        # correlate assets
        asset = get_correct_release_asset(
            rel.get_assets(), "i686-pc-windows-msvc.zip", ".tar.gz"
        )
        asset64 = get_correct_release_asset(
            rel.get_assets(), "x86_64-pc-windows-msvc.zip", ".tar.gz"
        )

        if asset is None or asset64 is None:
            logger.warn(
                "Versioned release missing required assets, therefore, ineligible for packaging, skipping."
            )
            continue

        # download and hash
        url = asset.browser_download_url
        fname = asset.name
        abort_on_nonzero(subprocess.call(
            ["wget", url, "--output-document", fname]))
        chksum = checksum.get_for_file(fname, "sha512")
        artifact_i686 = "hyperfine-x86.exe"
        with zipfile.ZipFile(fname) as zf:
            for member in zf.infolist():
                if ".exe" in member.filename:
                    with open(artifact_i686, "wb") as f:
                        f.write(zf.read(member))
        abort_on_nonzero(subprocess.call(["rrr", fname]))

        url64 = asset64.browser_download_url
        fname64 = asset64.name
        abort_on_nonzero(subprocess.call(
            ["wget", url64, "--output-document", fname64]))
        chksum64 = checksum.get_for_file(fname64, "sha512")
        artifact_amd64 = "hyperfine.exe"
        with zipfile.ZipFile(fname64) as zf64:
            for member in zf64.infolist():
                if ".exe" in member.filename:
                    with open(artifact_amd64, "wb") as f:
                        f.write(zf64.read(member))
                elif ".ps1" in member.filename:
                    with open("autocompletions.ps1", "wb") as f:
                        f.write(zf64.read(member))
        abort_on_nonzero(subprocess.call(["rrr", fname64]))

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
            "checksum64": chksum64,
            "fname64": fname64,
            "url64": url64,
            "notes": relnotes,
        }

        # template and pack
        tmpdir = tempfile.mkdtemp()
        find_and_replace_templates_new("hyperfine", tmpdir, d)
        os.mkdir(Path(tmpdir) / "tools/x64")
        os.mkdir(Path(tmpdir) / "tools/x86")
        os.rename(artifact_i686, os.path.join(
            tmpdir, "tools/x86", artifact_amd64))
        os.rename(artifact_amd64, os.path.join(
            tmpdir, "tools/x64", artifact_amd64))
        os.rename(
            "autocompletions.ps1", os.path.join(
                tmpdir, "tools/", "autocompletions.ps1")
        )

        abort_on_nonzero(
            subprocess.call(
                ["choco", "pack", Path(tmpdir) / "hyperfine.nuspec"])
        )


if __name__ == "__main__":
    main()
