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
    with io.open("gallery-dl.ghstate", "a+") as f:
        f.seek(0)  # why I have to do this is unknown
        for _, line in enumerate(f):
            state.append(line)
    f = io.open("gallery-dl.ghstate", "a+")
    # connect to github api 
    gh = Github(os.environ['GH_TOKEN'])
    gallerydl = gh.get_repo("mikf/gallery-dl")
    for rel in gallerydl.get_releases():
        pushed = False
        for i in range(len(state)):
            if str(state[i]).replace("\n", "") == str(rel.id):
                pushed = True
                break
            else:
                continue
        if not pushed:
            url, fname = get_correct_release_asset(rel.get_assets())
            if (url is "") and (fname is ""):
                print("no compatible releases, skipping...")
                f.write(str(rel.id)+"\n")
                f.flush()
                continue
            subprocess.call(["wget",
                             url,
                             "--output-document",
                             "gallery-dl.exe"])
            chksum = checksum.get_for_file("gallery-dl.exe", "sha512")
            os.remove("gallery-dl.exe")
            tempdir = tempfile.mkdtemp()
            find_and_replace_templates(tempdir,
                                       rel.tag_name.strip("v")
                                                   .replace("-dev.1", "-dev1"),
                                       rel.tag_name,
                                       url,
                                       chksum,
                                       fname,
                                       rel.body.replace("<", "&lt;")
                                               .replace(">", "&gt;"))
            abort_on_nonzero(subprocess.call(["choco",
                                              "pack",
                                              Path(tempdir)/"gallery-dl.nuspec"]))
            f.write(str(rel.id)+"\n")
            f.flush()
        else:
            continue

    f.close()


def get_correct_release_asset(assets):
    for a in assets:
        if ".exe" in a.name and not ".sig" in a.name:
            return (a.browser_download_url, a.name)
    return ("", "")


def find_and_replace_templates(directory,
                               version,
                               tag,
                               url,
                               checksum,
                               filename,
                               notes):
    os.mkdir(Path(directory)/"tools")
    d = dict(version=version,
             tag=tag,
             url=url,
             checksum=checksum,
             filename=filename,
             notes=notes)
    basepath = Path(os.getcwd())/"src/templates/gallery-dl/"
    templates = [
            "gallery-dl.nuspec",
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
