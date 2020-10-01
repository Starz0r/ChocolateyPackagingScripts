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
    with io.open("tokei.ghstate", "a+") as f:
        f.seek(0)  # why I have to do this is unknown
        for _, line in enumerate(f):
            state.append(line)
    f = io.open("tokei.ghstate", "a+")
    # connect to github api
    gh = Github(os.environ['GH_TOKEN'])
    repo = gh.get_repo("xampprocky/tokei")
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
                                              "-i686-pc-windows-msvc.exe",
                                              "linux")
            asset64 = get_correct_release_asset(rel.get_assets(),
                                                "-x86_64-pc-windows-msvc.exe",
                                                "linux")
            if asset is None or asset64 is None:
                print("no compatible releases, skipping...")
                f.write(str(rel.id) + "\n")
                f.flush()
                continue
            url = asset.browser_download_url
            fname = asset.name
            url64 = asset64.browser_download_url
            fname64 = asset64.name
            subprocess.call(["wget", url, "--output-document", fname])
            chksum = checksum.get_for_file(fname, "sha512")
            subprocess.call(["wget", url64, "--output-document", fname64])
            chksum64 = checksum.get_for_file(fname64, "sha512")
            if chksum == chksum64:
                raise "Different File, Same Hash"
            relnotes = ""
            if rel.body is not None:
                relnotes = rel.body.replace("<", "&lt;").replace(
                    ">",
                    "&gt;").replace("&",
                                    "&amp;").replace("\u200b",
                                                     "")  # zero-width space
            version = rel.tag_name.strip("v").replace("a", "-hotfix")
            gittag = rel.tag_name
            tempdir = tempfile.mkdtemp()
            d = dict(version=version,
                     tag=gittag,
                     url=url,
                     checksum=chksum,
                     fname=fname,
                     url64=url64,
                     checksum64=chksum64,
                     fname64=fname64,
                     notes=relnotes)
            find_and_replace_templates_new("tokei", tempdir, d)
            os.rename(fname, os.path.join(tempdir, "tools", fname))
            os.rename(fname64, os.path.join(tempdir, "tools", fname64))
            abort_on_nonzero(
                subprocess.call(
                    ["choco", "pack",
                     Path(tempdir) / "tokei.nuspec"]))
            f.write(str(rel.id) + "\n")
            f.flush()
        else:
            continue

    f.close()


if __name__ == "__main__":
    main()
