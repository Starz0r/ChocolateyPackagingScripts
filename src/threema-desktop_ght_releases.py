import os
import subprocess
import tempfile
import urllib.request
from pathlib import Path
from typing import Final

import checksum
import structlog
from github.Tag import Tag

from common.common import (abort_on_nonzero, dl_file,
                           find_and_replace_templates_new)
from common.events import on_each_git_tag

LOGGER: Final[structlog.stdlib.BoundLogger] = structlog.getLogger()


def on_tag(tag: Tag):
    LOGGER.info(f"New version of threema-desktop found!: {tag}")
    gittag = tag.name
    version = gittag.replace("v", "")

    # download and hash
    fname = f"Threema-{gittag}.exe"
    dl_url = f"https://releases.threema.ch/web-electron/v1/release/Threema-Latest.exe"
    dl_file(dl_url, fname)
    chksum = checksum.get_for_file(fname, "sha512")

    d = {
        "version": version,
        "tag": gittag,
        "checksum": chksum,
        "fname": fname,
        "url": dl_url,
    }

    # template and package
    tmpdir = tempfile.mkdtemp()
    find_and_replace_templates_new("threema-desktop", tmpdir, d)
    os.rename(fname, os.path.join(tmpdir, "tools/", fname))
    abort_on_nonzero(subprocess.call(
        ["choco", "pack", Path(tmpdir) / "threema-desktop.nuspec"]))


def main():
    for tag in on_each_git_tag("threema-desktop", "threema-ch/threema-web-electron"):
        on_tag(tag)


if __name__ == "__main__":
    main()
