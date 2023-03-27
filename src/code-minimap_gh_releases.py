import logging
import subprocess
import tempfile
import os
import zipfile
import checksum
from pathlib import Path

from common.common import abort_on_nonzero
from common.events import on_new_git_release
from common.common import get_correct_release_asset
from common.common import find_and_replace_templates_new


def main() -> int:
    logger = logging.getLogger("code-minimap GitHub Releases")
    logger.setLevel(logging.DEBUG)

    for rel in on_new_git_release("code-minimap", "wfxr/code-minimap"):
        # correlate assets
        asset = get_correct_release_asset(
            rel.get_assets(), "x86_64-pc-windows-msvc.zip", ".tar.gz"
        )

        if asset is None:
            logger.warn(
                "Versioned release missing required assets, therefore, ineligible for packaging, skipping."
            )
            continue

        # download and hash
        url = asset.browser_download_url
        fname = asset.name
        abort_on_nonzero(subprocess.call(["wget", url, "--output-document", fname]))

        # extract executable and autocompletions
        with zipfile.ZipFile(fname) as zf:
            for member in zf.infolist():
                if ".exe" in member.filename:
                    with open("code-minimap.exe", "wb") as f:
                        f.write(zf.read(member))
                elif ".ps1" in member.filename:
                    with open("autocompletions.ps1", "wb") as f:
                        f.write(zf.read(member))
        os.remove(fname)

        fname = "code-minimap.exe"
        fname2 = "autocompletions.ps1"
        chksum = checksum.get_for_file(fname, "sha512")

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
        version = rel.tag_name.replace("v", "").replace("rc.1", "rc1")
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
        find_and_replace_templates_new("code-minimap", tmpdir, d)
        # HACK: Python is dumb and won't recursively create directories sometimes, why...
        os.mkdir(Path(tmpdir) / "tools/x64")
        os.rename(fname, os.path.join(tmpdir, "tools/x64/", fname))
        os.rename(fname2, os.path.join(tmpdir, "tools/", fname2))
        abort_on_nonzero(
            subprocess.call(["choco", "pack", Path(tmpdir) / "code-minimap.nuspec"])
        )

    return 0


if __name__ == "__main__":
    main()
