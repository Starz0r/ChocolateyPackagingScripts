import os
import io
import tempfile
import subprocess
import checksum
from pathlib import Path
from string import Template
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
            url = get_correct_release_asset(rel.get_assets())
            subprocess.call(["wget",
                             url,
                             "--output-document",
                             "rustlsp.exe"])
            chksum = checksum.get_for_file("rustlsp.exe", "sha512")
            os.remove("rustlsp.exe")
            tempdir = tempfile.mkdtemp()
            if "nightly" in rel.title:
                t = rel.published_at
                find_and_replace_templates(tempdir,
                                           "{}.{}.{}-nightly".format(t.year,
                                                                     t.month,
                                                                     t.day),
                                           rel.tag_name,
                                           url,
                                           chksum)
            else:
                find_and_replace_templates(tempdir,
                                           rel.title.replace("-", "."),
                                           rel.tag_name,
                                           url,
                                           chksum)
            abort_on_nonzero(subprocess.call(["choco",
                                              "pack",
                                              Path(tempdir)/"rust-analyzer.nuspec"]))
            f.write(str(rel.id)+"\n")
            f.flush()
        else:
            continue

    f.close()


def get_correct_release_asset(assets):
    for a in assets:
        if "windows" in a.name:
            return a.browser_download_url


def find_and_replace_templates(directory, version, tag, url, checksum):
    os.mkdir(Path(directory)/"tools")
    d = dict(version=version, tag=tag, url=url, checksum=checksum)
    basepath = Path(os.getcwd())/"src/templates/rust-analyzer/"
    templates = [
            "rust-analyzer.nuspec",
            "tools/chocolateyinstall.ps1"]

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
