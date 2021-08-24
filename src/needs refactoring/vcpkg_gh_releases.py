import os
import io
import tempfile
import subprocess
from pathlib import Path
from string import Template
from github import Github


def main():
    # initalize state array
    state = []
    with io.open("vcpkg.ghstate", "a+") as f:
        f.seek(0) # why I have to do this is unknown
        for _, line in enumerate(f):
            state.append(line)
    f = io.open("vcpkg.ghstate", "a+")
    # connect to github api 
    gh = Github(os.environ['GH_TOKEN'])
    vcpkg = gh.get_repo("microsoft/vcpkg")
    for rel in vcpkg.get_releases():
        pushed = False
        for i in range(len(state)):
            if str(state[i]).replace("\n", "") == str(rel.id):
                pushed = True
                break
            else:
                continue
        if not pushed:
            tempdir = tempfile.mkdtemp()
            find_and_replace_templates(tempdir, rel.title, rel.tag_name)
            abort_on_nonzero(subprocess.call(["choco", "pack", Path(tempdir)/"vcpkg.nuspec"]))
            f.write(str(rel.id)+"\n")
            f.flush()
        else:
            continue

    f.close()


def find_and_replace_templates(directory, version, tag):
    os.mkdir(Path(directory)/"tools")
    d = dict(version=version, tag=tag)
    basepath = Path(os.getcwd())/"src/templates/vcpkg/"
    templates = [
            "vcpkg.nuspec",
            "tools/chocolateyinstall.ps1",
            "tools/chocolateyuninstall.ps1"]

    for template in templates:
        with io.open(basepath/template, "r") as f:
            contents = f.read()
            temp = Template(contents).safe_substitute(d)
            f = io.open(Path(directory)/template, "a+")
            f.write(temp)
            f.close()
    return


def abort_on_nonzero(retcode):
    if (retcode != 0):
        os.exit(retcode)


if __name__ == "__main__":
    main()
