import json
import logging
import os
import subprocess
import tempfile
import urllib.request
from pathlib import Path

import checksum
from jenkinsapi.jenkins import Jenkins

from common.common import (TempDir, abort_on_nonzero,
                           find_and_replace_templates_new,
                           get_correct_release_artifact)
from common.events import on_each_git_tag


def main():
    logger = logging.getLogger("neochat.install Meta Releases")
    logger.setLevel(logging.DEBUG)

    for tag in on_each_git_tag("neochat.install", "KDE/neochat"):
        # get the last good build from the release channel
        J = Jenkins("https://binary-factory.kde.org")
        build_id = J["NeoChat_Release_win64"].get_last_good_buildnumber()
        artifacts = J["NeoChat_Release_win64"].get_build(build_id).get_artifact_dict()
        artifact = get_correct_release_artifact(artifacts.values(), ".appx", "upload")

        if artifact is None:
            logger.warn(
                "Versioned release missing require assets, therefore, ineligible for packaging, skipping."
            )
            continue

        # download and hash
        dl_url = artifact.url
        fname = artifact.filename
        urllib.request.urlretrieve(dl_url, fname)
        chksum = checksum.get_for_file(fname, "sha512")

        # retrieve and format release notes
        req = urllib.request.urlopen("https://flathub.org/api/v1/apps/org.kde.neochat")
        info = json.loads(req.read().decode(req.info().get_param("charset") or "utf-8"))
        relnotes = (
            (info["currentReleaseDescription"] or "")
            .replace("<p>", "# ")
            .replace("</p>", "\n")
            .replace("<ul>", "")
            .replace("<li>", "  - ")
            .replace("</li>", "\n")
            .replace("</ul>", "")
        )

        version = tag.name.replace("v", "")
        gittag = tag.name

        d = dict(
            version=version,
            tag=gittag,
            checksum=chksum,
            fname=fname,
            url=dl_url,
            notes=relnotes,
        )

        # template and package
        with TempDir() as tmpdir:
            find_and_replace_templates_new("neochat.install", tmpdir, d)
            os.rename(fname, os.path.join(tmpdir, "tools", fname))
            abort_on_nonzero(
                subprocess.call(
                    ["choco", "pack", Path(tmpdir) / "neochat.install.nuspec"]
                )
            )


if __name__ == "__main__":
    main()
