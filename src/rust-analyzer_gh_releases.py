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
    with io.open("rust-analyzer.ghstate", "a+") as f:
        f.seek(0)  # why I have to do this is unknown
        for _, line in enumerate(f):
            state.append(line)
    f = io.open("rust-analyzer.ghstate", "a+")
    # connect to github api
    gh = Github(os.environ['GH_TOKEN'])
    rustlsp = gh.get_repo("rust-analyzer/rust-analyzer")
    for rel in rustlsp.get_releases():
        pushed = False
        for i in range(len(state)):
            if str(state[i]).replace("\n", "") == str(rel.id):
                pushed = True
                break
            else:
                continue
        if not pushed:
            asset = get_correct_release_asset(rel.get_assets(),
                                              "windows",
                                              None)
            if asset is None:
                continue
            url = asset.browser_download_url
            subprocess.call(["wget",
                             url,
                             "--output-document",
                             "rustlsp.exe"])
            chksum = checksum.get_for_file("rustlsp.exe", "sha512")
            os.remove("rustlsp.exe")
            tempdir = tempfile.mkdtemp()
            if "nightly" in rel.title:
                t = rel.published_at
                find_and_replace_templates("rust-analyzer",
                                           tempdir,
                                           "{}.{}.{}-nightly".format(t.year,
                                                                     t.month,
                                                                     t.day),
                                           rel.tag_name,
                                           url,
                                           chksum,
                                           None,
                                           None,
                                           None,
                                           None,
                                           None)
            else:
                find_and_replace_templates("rust-analyzer",
                                           tempdir,
                                           rel.title.replace("-", "."),
                                           rel.tag_name,
                                           url,
                                           chksum,
                                           None,
                                           None,
                                           None,
                                           None,
                                           None)
            abort_on_nonzero(subprocess.call(["choco",
                                              "pack",
                                              Path(tempdir)/"rust-analyzer.nuspec"]))
            f.write(str(rel.id)+"\n")
            f.flush()
        else:
            continue

    f.close()


if __name__ == "__main__":
    main()
