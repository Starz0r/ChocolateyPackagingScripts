import os
import io
import tempfile
import subprocess
import checksum
from pathlib import Path
from string import Template

from common.common import find_and_replace_templates
from common.common import find_and_replace_templates_new
from common.common import abort_on_nonzero
from common.common import get_correct_release_asset

from github import Github


def main():
    # initalize state array
    state = []
    with io.open("lsd.ghstate", "a+") as f:
        f.seek(0)  # why I have to do this is unknown
        for _, line in enumerate(f):
            state.append(line)
    f = io.open("lsd.ghstate", "a+")
    # connect to github api
    gh = Github(os.environ['GH_TOKEN'])
    repo = gh.get_repo("peltoche/lsd")
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
                                              "i686-pc-windows-msvc", None)
            asset64 = get_correct_release_asset(rel.get_assets(),
                                                "x86_64-pc-windows-msvc", None)
            altasset = get_correct_release_asset(rel.get_assets(),
                                                 "i686-pc-windows-gnu", None)
            altasset64 = get_correct_release_asset(rel.get_assets(),
                                                   "x86_64-pc-windows-gnu",
                                                   None)
            if asset is None or asset64 is None or altasset is None or altasset64 is None:
                print("no compatible releases, skipping...")
                f.write(str(rel.id) + "\n")
                f.flush()
                continue
            print(rel.id)
            tempdir = tempfile.mkdtemp()
            url = asset.browser_download_url
            fname = asset.name
            url64 = asset64.browser_download_url
            fname64 = asset64.name
            alturl = altasset.browser_download_url
            altfname = altasset.name
            alturl64 = altasset64.browser_download_url
            altfname64 = altasset64.name
            subprocess.call(["wget", url, "--output-document", fname])
            chksum = checksum.get_for_file(fname, "sha512")
            subprocess.call(["wget", url64, "--output-document", fname64])
            chksum64 = checksum.get_for_file(fname64, "sha512")
            subprocess.call(["wget", alturl, "--output-document", altfname])
            altchksum = checksum.get_for_file(altfname, "sha512")
            subprocess.call(
                ["wget", alturl64, "--output-document", altfname64])
            altchksum64 = checksum.get_for_file(altfname64, "sha512")
            relnotes = rel.body.replace("<", "&lt;").replace(
                ">", "&gt;").replace("&",
                                     "&amp;").replace("\u200b",
                                                      "")  # zero-width space
            version = rel.tag_name.replace("v", "")
            gittag = rel.tag_name
            d = dict(version=version,
                     tag=gittag,
                     url=url,
                     checksum=chksum,
                     fname=fname,
                     url64=url64,
                     checksum64=chksum64,
                     fname64=fname64,
                     alturl=alturl,
                     altchecksum=altchksum,
                     altfname=altfname,
                     alturl64=alturl64,
                     altchecksum64=altchksum64,
                     altfname64=altfname64,
                     notes=relnotes)
            find_and_replace_templates_new("lsd", tempdir, d)
            os.rename(fname, os.path.join(tempdir, "tools", fname))
            os.rename(fname64, os.path.join(tempdir, "tools", fname64))
            os.rename(altfname, os.path.join(tempdir, "tools", altfname))
            os.rename(altfname64, os.path.join(tempdir, "tools", altfname64))
            abort_on_nonzero(
                subprocess.call(
                    ["choco", "pack",
                     Path(tempdir) / "lsd.nuspec"]))
            f.write(str(rel.id) + "\n")
            f.flush()
        else:
            continue

    f.close()


if __name__ == "__main__":
    main()
