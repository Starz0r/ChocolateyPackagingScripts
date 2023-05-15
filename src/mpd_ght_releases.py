import logging
import os
import subprocess
import tempfile
import urllib.request
from pathlib import Path

import checksum

from common.common import abort_on_nonzero, find_and_replace_templates_new
from common.events import on_each_git_tag


def main():
    logger = logging.getLogger("mpd Releases")
    logger.setLevel(logging.DEBUG)

    for tag in on_each_git_tag("mpd", "MusicPlayerDaemon/MPD"):
        gittag = tag.name
        version = gittag.replace("v", "")

        # download and hash
        fname = "mpd.exe"
        dl_url = f"https://www.musicpd.org/download/win32/{version}/{fname}"
        urllib.request.urlretrieve(dl_url, fname)
        chksum = checksum.get_for_file(fname, "sha512")

        # retrieve and format release notes
        req = urllib.request.urlopen(
            f"https://raw.githubusercontent.com/MusicPlayerDaemon/MPD/{gittag}/NEWS"
        )
        news = req.read().decode(req.info().get_param("charset") or "utf-8")
        relnotes = news.split("\n\n")[0]

        d = {
            "version": version,
            "tag": gittag,
            "checksum": chksum,
            "fname": fname,
            "url": dl_url,
            "notes": relnotes,
        }

        # template and package
        tmpdir = tempfile.mkdtemp()
        find_and_replace_templates_new("mpd", tmpdir, d)
        os.mkdir(os.path.join(tmpdir, "tools/x64"))
        os.rename(fname, os.path.join(tmpdir, "tools/x64", fname))
        abort_on_nonzero(
            subprocess.call(["choco", "pack", Path(tmpdir) / "mpd.nuspec"])
        )


if __name__ == "__main__":
    main()
