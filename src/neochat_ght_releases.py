import json
import logging
from pathlib import Path
import subprocess
import tempfile
from jenkinsapi.jenkins import Jenkins
import urllib.request

from common.common import abort_on_nonzero, find_and_replace_templates_new, get_correct_release_artifact
from common.events import on_each_git_tag

def main():
    logger = logging.getLogger("neochat GitHub Tag Releases")
    logger.setLevel(logging.DEBUG)

    for tag in on_each_git_tag("neochat", "KDE/neochat"):
        # get the last good build from the release channel
        J = Jenkins("https://binary-factory.kde.org")
        build_id = J["NeoChat_Release_win64"].get_last_good_buildnumber()
        artifacts = J["NeoChat_Release_win64"].get_build(build_id).get_artifact_dict()
        artifact = get_correct_release_artifact(artifacts.values(), ".appx", "upload")

        if artifact is None:
            logger.warn("Versioned release missing require assets, therefore, ineligible for packaging, skipping.")
            continue

        # retrieve and format release notes
        req = urllib.request.urlopen("https://flathub.org/api/v1/apps/org.kde.neochat")
        info = json.loads(req.read().decode(req.info().get_param("charset") or "utf-8"))
        relnotes = info["currentReleaseDescription"].replace("<p>", "# ").replace("</p>", "\n").replace("<ul>", "").replace("<li>", "  - ").replace("</li>", '\n').replace("</ul>", "")
        
        version = tag.name.replace("v", "")
        gittag = tag.name

        d = dict(version=version, tag=gittag, notes=relnotes)

        # template and package
        tmpdir = tempfile.mkdtemp()
        find_and_replace_templates_new("neochat", tmpdir, d)
        abort_on_nonzero(subprocess.call(["choco", "pack", Path(tmpdir) / "neochat.nuspec"]))


if __name__ == "__main__":
    main()
