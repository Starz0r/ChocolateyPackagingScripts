import os
import io
import tempfile
import subprocess
import checksum
from pathlib import Path
from string import Template

from common.common import find_and_replace_templates
from common.common import abort_on_nonzero
from common.common import get_correct_release_asset

from github import Github


def main():
    # initalize state array
    state = []
    with io.open("alacritty.portable.ghstate", "a+") as f:
        f.seek(0)  # why I have to do this is unknown
        for _, line in enumerate(f):
            state.append(line)
    f = io.open("alacritty.portable.ghstate", "a+")
    # connect to github api 
    gh = Github(os.environ['GH_TOKEN'])
    alacritty = gh.get_repo("alacritty/alacritty")
    for rel in alacritty.get_releases():
        pushed = False
        for i in range(len(state)):
            if str(state[i]).replace("\n", "") == str(rel.id):
                pushed = True
                break
            else:
                continue
        if not pushed:
            asset = get_correct_release_asset(rel.get_assets(),
                                              "windows-portable",
                                              None)
            if asset == None:
                print("no compatible releases, skipping...")
                f.write(str(rel.id)+"\n")
                f.flush()
                continue 
            url = asset.browser_download_url
            fname = asset.name
            subprocess.call(["wget",
                             url,
                             "--output-document",
                             "alacritty.zip"])
            chksum = checksum.get_for_file("alacritty.zip", "sha512")
            os.remove("alacritty.zip")
            tempdir = tempfile.mkdtemp()
            find_and_replace_templates("alacritty.portable",
                                       tempdir,
                                       rel.tag_name.replace("v", ""),
                                       rel.tag_name,
                                       url,
                                       chksum,
                                       fname,
                                       None,
                                       None,
                                       None,
                                       rel.body.replace("<", "&lt;")
                                               .replace(">", "&gt;")
                                               .replace("&", "&amp;")
                                               .replace("\u200b", "")) # zero-width space
            abort_on_nonzero(subprocess.call(["choco",
                                              "pack",
                                              Path(tempdir)/"alacritty.portable.nuspec"]))
            f.write(str(rel.id)+"\n")
            f.flush()
        else:
            continue

    f.close()


if __name__ == "__main__":
    main()
