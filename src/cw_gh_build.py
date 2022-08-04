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
    logger = logging.getLogger("cw GitHub Builds")
    logger.setLevel(logging.DEBUG)

    for rel in on_new_git_release("cw", "Freaky/cw"):
        # correlate assets
        code_zipball = rel.zipball_url

        # download and hash
        fname = "cw.zip"
        abort_on_nonzero(
            subprocess.call(["wget", code_zipball, "--output-document", fname])
        )

        builddir = tempfile.mkdtemp()
        f = zipfile.ZipFile(fname)
        in_folder_name = f.namelist()[
            0
        ]  # github tarballs/zipballs have an additional folder in them
        build_root_name = builddir.__str__() + "/" + in_folder_name
        manifest_path = build_root_name + "/Cargo.toml"
        i686_artifact_path = (
            build_root_name + "/target/i686-pc-windows-msvc/release/cw.exe"
        )
        amd64_artifact_path = (
            build_root_name + "/target/x86_64-pc-windows-msvc/release/cw.exe"
        )
        f.extractall(builddir)
        abort_on_nonzero(
            subprocess.call(
                [
                    "cargo",
                    "build",
                    "--target",
                    "x86_64-pc-windows-msvc",
                    "--release",
                    "--manifest-path",
                    manifest_path,
                ]
            )
        )
        abort_on_nonzero(
            subprocess.call(
                [
                    "cargo",
                    "build",
                    "--target",
                    "i686-pc-windows-msvc",
                    "--release",
                    "--manifest-path",
                    manifest_path,
                ]
            )
        )

        tmpdir = tempfile.mkdtemp()
        chksum = checksum.get_for_file(i686_artifact_path, "sha512")
        chksum64 = checksum.get_for_file(amd64_artifact_path, "sha512")
        fname = "cw.exe"
        fname64 = "cw.exe"

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
            notes=relnotes,
        )

        # template and pack
        find_and_replace_templates_new("cw", tmpdir, d)
        # HACK: Python is dumb and won't recursively create directories sometimes, why...
        os.mkdir(Path(tmpdir) / "tools/x86")
        os.mkdir(Path(tmpdir) / "tools/x64")
        os.rename(i686_artifact_path, os.path.join(tmpdir, "tools/x86/", fname))
        os.rename(amd64_artifact_path, os.path.join(tmpdir, "tools/x64/", fname64))
        abort_on_nonzero(subprocess.call(["choco", "pack", Path(tmpdir) / "cw.nuspec"]))


if __name__ == "__main__":
    main()
