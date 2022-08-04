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
    logger = logging.getLogger("ccls GitHub Builds")
    logger.setLevel(logging.DEBUG)

    for rel in on_new_git_release("ccls", "MaskRay/ccls"):
        gittag = rel.tag_name

        # run the builder
        workdir = tempfile.mkdtemp()
        subprocess.run(
            [
                "pwsh",
                "-noprofile",
                "-File",
                os.path.abspath("./src/ccls_builder.ps1"),
                workdir,
                gittag,
            ],
            capture_output=True,
            shell=True,
            cwd=workdir,
        )
        amd64_artifact_path = workdir + "/ccls/build/Release/ccls.exe"

        tmpdir = tempfile.mkdtemp()
        chksum = checksum.get_for_file(amd64_artifact_path, "sha512")
        final_artifact_name = "ccls.exe"

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
        d = dict(
            version=version,
            tag=gittag,
            checksum=chksum,
            fname=final_artifact_name,
            notes=relnotes,
        )

        # template and pack
        find_and_replace_templates_new("ccls", tmpdir, d)
        # HACK: Python is dumb and won't recursively create directories sometimes, why...
        os.mkdir(Path(tmpdir) / "tools/x64")
        os.rename(
            amd64_artifact_path, os.path.join(tmpdir, "tools/x64/", final_artifact_name)
        )
        abort_on_nonzero(
            subprocess.call(["choco", "pack", Path(tmpdir) / "ccls.nuspec"])
        )


if __name__ == "__main__":
    main()
