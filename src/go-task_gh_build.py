import logging
import subprocess
import checksum
import tempfile
import sys
import os
import zipfile
import tarfile
from pathlib import Path

from common.common import abort_on_nonzero
from common.events import on_new_git_release
from common.common import get_correct_release_asset
from common.common import find_and_replace_templates_new


def main():
    logger = logging.getLogger("Task GitHub Builds")
    logger.setLevel(logging.DEBUG)

    for rel in on_new_git_release("go-task", "go-task/Task"):
        # correlate assets
        is_tar = False

        asset = get_correct_release_asset(
            rel.get_assets(), "windows_386.zip", "linux_386.zip"
        )
        asset64 = get_correct_release_asset(
            rel.get_assets(), "windows_amd64.zip", "linux_amd64.zip"
        )

        if asset is None or asset64 is None:
            is_tar = True
            asset = get_correct_release_asset(
                rel.get_assets(), "Windows_i386.tar.gz", "Linux_i386.tar.gz"
            )
            asset64 = get_correct_release_asset(
                rel.get_assets(), "Windows_x86_64.tar.gz", "Linux_x86_64.tar.gz"
            )

        if asset is None or asset64 is None:
            logger.warn(
                "Versioned release missing required assets, therefore, ineligible for packaging, skipping."
            )
            continue

        # download and hash
        url = asset.browser_download_url
        url64 = asset64.browser_download_url
        archive = asset.name
        archive64 = asset64.name
        abort_on_nonzero(subprocess.call(["wget", url, "--output-document", archive]))
        abort_on_nonzero(
            subprocess.call(["wget", url64, "--output-document", archive64])
        )

        copydir = tempfile.mkdtemp()
        copydir64 = tempfile.mkdtemp()
        if is_tar is False:
            f = zipfile.ZipFile(archive)
            f.extractall(copydir)
            f.close()
            os.remove(archive)

            f64 = zipfile.ZipFile(archive64)
            f64.extractall(copydir64)
            f64.close()
            os.remove(archive64)
        else:
            f = tarfile.open(archive, "r:gz")
            f.extractall(copydir)
            f.close()
            os.remove(archive)

            f64 = tarfile.open(archive64, "r:gz")
            f64.extractall(copydir64)
            f64.close()
            os.remove(archive64)

        i686_artifact_path = os.path.join(copydir, "task.exe")
        amd64_artifact_path = os.path.join(copydir64, "task.exe")

        chksum = checksum.get_for_file(i686_artifact_path, "sha512")
        chksum64 = checksum.get_for_file(amd64_artifact_path, "sha512")
        fname = "task.exe"
        fname64 = fname

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
            url=url,
            url64=url64,
            version=version,
            tag=gittag,
            checksum=chksum,
            fname=fname,
            checksum64=chksum64,
            fname64=fname64,
            notes=relnotes,
        )

        # template and pack
        tmpdir = tempfile.mkdtemp()
        find_and_replace_templates_new("go-task", tmpdir, d)
        # HACK: Python is dumb and won't recursively create directories sometimes, why...
        os.mkdir(Path(tmpdir) / "tools/x86")
        os.mkdir(Path(tmpdir) / "tools/x64")
        os.rename(i686_artifact_path, os.path.join(tmpdir, "tools/x86/", fname))
        os.rename(amd64_artifact_path, os.path.join(tmpdir, "tools/x64/", fname64))
        abort_on_nonzero(
            subprocess.call(["choco", "pack", Path(tmpdir) / "go-task.nuspec"])
        )


if __name__ == "__main__":
    main()
