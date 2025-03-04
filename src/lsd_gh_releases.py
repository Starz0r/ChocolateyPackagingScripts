import io
import os
import subprocess
import zipfile
from pathlib import Path

import checksum
from github import Github

from common.common import (
    TempDir,
    abort_on_nonzero,
    find_and_replace_templates_new,
    get_correct_release_asset,
)


def main():
    # initalize state array
    state = []
    with io.open("lsd.ghstate", "a+") as f:
        f.seek(0)  # why I have to do this is unknown
        for _, line in enumerate(f):
            state.append(line)
    f = io.open("lsd.ghstate", "a+")
    # connect to github api
    gh = Github(os.environ["GH_TOKEN"])
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
            asset = get_correct_release_asset(
                rel.get_assets(), "i686-pc-windows-msvc", None
            )
            asset64 = get_correct_release_asset(
                rel.get_assets(), "x86_64-pc-windows-msvc", None
            )
            if asset is None or asset64 is None:
                print("no compatible releases, skipping...")
                f.write(str(rel.id) + "\n")
                f.flush()
                continue
            print(rel.id)
            url = asset.browser_download_url
            fname = asset.name
            url64 = asset64.browser_download_url
            fname64 = asset64.name
            subprocess.call(["wget", url, "--output-document", fname])
            chksum = checksum.get_for_file(fname, "sha512")
            subprocess.call(["wget", url64, "--output-document", fname64])
            chksum64 = checksum.get_for_file(fname64, "sha512")
            relnotes = (
                rel.body.replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("&", "&amp;")
                .replace("\u200b", "")
            )  # zero-width space
            version = rel.tag_name.replace("v", "")
            gittag = rel.tag_name
            d = dict(
                version=version,
                tag=gittag,
                url=url,
                checksum=chksum,
                fname=fname,
                url64=url64,
                checksum64=chksum64,
                fname64=fname64,
                notes=relnotes,
            )
            with TempDir() as tempdir:
                find_and_replace_templates_new("lsd", tempdir, d)
                os.mkdir(Path(tempdir) / "tools/x64")
                os.mkdir(Path(tempdir) / "tools/x86")
                with zipfile.ZipFile(fname) as zf:
                    zf.extractall(os.path.join(tempdir, "tools/x86"))
                with zipfile.ZipFile(fname64) as zf64:
                    zf64.extractall(os.path.join(tempdir, "tools/x64"))
                abort_on_nonzero(subprocess.call(["rrr", fname]))
                abort_on_nonzero(subprocess.call(["rrr", fname64]))
                abort_on_nonzero(
                    subprocess.call(["choco", "pack", Path(tempdir) / "lsd.nuspec"])
                )
            f.write(str(rel.id) + "\n")
            f.flush()
        else:
            continue

    f.close()


if __name__ == "__main__":
    main()
