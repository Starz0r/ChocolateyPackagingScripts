import logging
import subprocess
import checksum
import tempfile
import sys
import os
import zipfile
from pathlib import Path

from common.common import abort_on_nonzero
from common.events import on_new_git_release
from common.common import get_correct_release_asset
from common.common import find_and_replace_templates_new


def main():
    logger = logging.getLogger("Crinkler GitHub Builds")
    logger.setLevel(logging.DEBUG)

    for rel in on_new_git_release("crinkler", "runestubbe/Crinkler"):
        # correlate assets
        asset = get_correct_release_asset(rel.get_assets(), ".zip", None)

        if asset is None:
            logger.warn(
                "Versioned release missing required assets, therefore, ineligible for packaging, skipping."
            )
            continue

        # download and hash
        url = asset.browser_download_url
        fname = asset.name
        abort_on_nonzero(subprocess.call(["wget", url, "--output-document", fname]))

        copydir = tempfile.mkdtemp()
        f = zipfile.ZipFile(fname)
        i686_artifact_path = ""
        amd64_artifact_path = ""
        for name in f.namelist():
            if name.__contains__("Win32") and name.__contains__(".exe"):
                i686_artifact_path = copydir.__str__() + "/" + name
            if name.__contains__("Win64") and name.__contains__(".exe"):
                amd64_artifact_path = copydir.__str__() + "/" + name
            if i686_artifact_path is None or amd64_artifact_path is None:
                logger.critical("Artifacts could not be found in the archive.")
                sys.exit(-1)
        f.extractall(copydir)
        f.close()
        os.remove(fname)

        tmpdir = tempfile.mkdtemp()
        chksum = checksum.get_for_file(i686_artifact_path, "sha512")
        chksum64 = checksum.get_for_file(amd64_artifact_path, "sha512")
        fname = "Crinkler.exe"
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
            version=version,
            tag=gittag,
            checksum=chksum,
            fname=fname,
            checksum64=chksum64,
            fname64=fname64,
            notes=relnotes,
        )

        # template and pack
        find_and_replace_templates_new("crinkler", tmpdir, d)
        # HACK: Python is dumb and won't recursively create directories sometimes, why...
        os.mkdir(Path(tmpdir) / "tools/x86")
        os.mkdir(Path(tmpdir) / "tools/x64")
        os.rename(i686_artifact_path, os.path.join(tmpdir, "tools/x86/", fname))
        os.rename(amd64_artifact_path, os.path.join(tmpdir, "tools/x64/", fname64))
        abort_on_nonzero(
            subprocess.call(["choco", "pack", Path(tmpdir) / "crinkler.nuspec"])
        )


if __name__ == "__main__":
    main()
