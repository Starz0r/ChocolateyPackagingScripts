import os
import io
import tempfile
import subprocess
import checksum
from pathlib import Path

from common.common import find_and_replace_templates
from common.common import abort_on_nonzero
from common.common import get_correct_release_asset

from github import Github


def main():
    pkgname = "TweetDuck"
    # initalize state array
    state = []
    with io.open(pkgname+".install.ghstate", "a+") as f:
        f.seek(0)  # why I have to do this is unknown
        for _, line in enumerate(f):
            state.append(line)
    f = io.open(pkgname+".install.ghstate", "a+")
    # connect to github api
    gh = Github(os.environ['GH_TOKEN'])
    repo = gh.get_repo("chylex/"+pkgname)
    for rel in repo.get_releases():
        pushed = False
        for i in range(len(state)):
            if str(state[i]).replace("\n", "") == str(rel.id):
                pushed = True
                break
            else:
                continue
        if not pushed:
            asset = get_correct_release_asset(rel.get_assets(),
                                              "TweetDuck.exe",
                                              None)
            if asset is None:
                continue
            url = asset.browser_download_url
            subprocess.call(["wget",
                             url,
                             "--output-document",
                             "td.exe"])
            chksum = checksum.get_for_file("td.exe", "sha512")
            os.remove("td.exe")
            tempdir = tempfile.mkdtemp()
            find_and_replace_templates(pkgname+".install",
                                       tempdir,
                                       rel.title.replace("Release ", ""),
                                       rel.tag_name,
                                       url,
                                       chksum,
                                       None,
                                       None,
                                       None,
                                       None,
                                       rel.body.replace("<", "&lt;")
                                               .replace(">", "&gt;")
                                               .replace("&", "&amp;")
                                               .replace("\u200b", "")) # zero-width space
            abort_on_nonzero(subprocess.call(["choco",
                                              "pack",
                                              Path(tempdir)/(pkgname+".install.nuspec")]))
            f.write(str(rel.id)+"\n")
            f.flush()
        else:
            continue

    f.close()


if __name__ == "__main__":
    main()
