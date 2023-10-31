import os
import io
import tempfile
import subprocess
import checksum
import requests
from pathlib import Path

from common.common import find_and_replace_templates
from common.common import abort_on_nonzero


def main():
    pkgname = "flutter"
    # initalize state array
    state = []
    with io.open(pkgname+".gasstate", "a+") as f:
        f.seek(0)  # why I have to do this is unknown
        for _, line in enumerate(f):
            state.append(line)
    f = io.open(pkgname+".gasstate", "a+")
    # connect to github api
    req = requests.get(
        "https://storage.googleapis.com/flutter_infra_release/releases/releases_windows.json")
    repo = req.json()
    for rel in repo["releases"]:
        pushed = False
        for i in range(len(state)):
            if str(state[i]).replace("\n", "") == str(rel["hash"]):
                pushed = True
                break
            else:
                continue
        if not pushed:
            url = "https://storage.googleapis.com/flutter_infra_release/releases/" + \
                rel["archive"]
            chksum = rel["sha256"]
            tempdir = tempfile.mkdtemp()
            version = rel["version"].replace("v", "")
            if "-dev" in version:
                version = version.replace("-dev", "")
            if "-beta" in version:
                version = version.replace("-beta", "")
            if "-stable" in version:
                version = version.replace("-stable", "")
            find_and_replace_templates(pkgname,
                                       tempdir,
                                       version,
                                       rel["version"].replace("v", "").replace("-de", "-dev"),
                                       url,
                                       chksum,
                                       None,
                                       None,
                                       None,
                                       None,
                                       None)
            abort_on_nonzero(subprocess.call(["choco",
                                              "pack",
                                              Path(tempdir)/(pkgname+".nuspec")]))
            f.write(str(rel["hash"])+"\n")
            f.flush()
        else:
            continue

    f.close()


if __name__ == "__main__":
    main()