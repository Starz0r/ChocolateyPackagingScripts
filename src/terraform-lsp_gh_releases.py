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
    pkgname = "terraform-lsp"
    # initalize state array
    state = []
    with io.open(pkgname + ".ghstate", "a+") as f:
        f.seek(0)  # why I have to do this is unknown
        for _, line in enumerate(f):
            state.append(line)
    f = io.open(pkgname + ".ghstate", "a+")
    # connect to github api
    gh = Github(os.environ['GH_TOKEN'])
    repo = gh.get_repo("juliosueiras/terraform-lsp")
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
                rel.get_assets(), "windows_amd64", None)
            if asset is None:
                continue
            url = asset.browser_download_url
            subprocess.call(["wget", url, "--output-document", "tflsp.tar.gz"])
            chksum = checksum.get_for_file("tflsp.tar.gz", "sha512")
            os.remove("tflsp.tar.gz")
            tempdir = tempfile.mkdtemp()
            print(tempdir)
            fname = asset.name
            relnotes = rel.body
            if rel.body is None:
                relnotes = ""
            else:
                relnotes = relnotes.replace("<", "&lt;").replace(">", "&gt;").replace(
                    "&", "&amp;").replace("\u200b", "")  # zero-width space
            find_and_replace_templates(pkgname, tempdir,
                                       rel.title.replace(
                                           "v", ""), rel.tag_name,
                                       url, chksum, fname, None,
                                       None, None,
                                       relnotes)
            abort_on_nonzero(
                subprocess.call(
                    ["choco", "pack",
                     Path(tempdir) / (pkgname + ".nuspec")]))
            f.write(str(rel.id) + "\n")
            f.flush()
        else:
            continue

    f.close()


if __name__ == "__main__":
    main()
