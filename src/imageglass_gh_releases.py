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
    with io.open("imageglass.ghstate", "a+") as f:
        f.seek(0)  # why I have to do this is unknown
        for _, line in enumerate(f):
            state.append(line)
    f = io.open("imageglass.ghstate", "a+")
    # connect to github api
    gh = Github(os.environ['GH_TOKEN'])
    imageglass = gh.get_repo("d2phap/imageglass")
    for rel in imageglass.get_releases():
        print(rel.id)
        pushed = False
        for i in range(len(state)):
            if str(state[i]).replace("\n", "") == str(rel.id):
                pushed = True
                break
            else:
                continue
        if not pushed:
            url, fname = get_correct_release_asset_32(rel.get_assets())
            url64, fname64 = get_correct_release_asset_64(rel.get_assets())
            if (url is "") and (fname is ""):
                print("no compatible releases, skipping...")
                f.write(str(rel.id)+"\n")
                f.flush()
                continue
            if (url64 is "") and (fname64 is ""):
                print("no compatible releases, skipping...")
                f.write(str(rel.id)+"\n")
                f.flush()
                continue
            subprocess.call(["wget",
                             url,
                             "--output-document",
                             "imageglass.msi"])
            chksum = checksum.get_for_file("imageglass.msi", "sha512")
            os.remove("imageglass.msi")
            subprocess.call(["wget",
                             url64,
                             "--output-document",
                             "imageglass.msi"])
            chksum64 = checksum.get_for_file("imageglass.msi", "sha512")
            os.remove("imageglass.msi")
            tempdir = tempfile.mkdtemp()
            find_and_replace_templates(tempdir,
                                       rel.tag_name.replace("v", ""),
                                       rel.tag_name,
                                       url,
                                       chksum,
                                       fname,
                                       url64,
                                       chksum64,
                                       fname64,
                                       rel.body.replace("<", "&lt;")
                                               .replace(">", "&gt;"))
            abort_on_nonzero(subprocess.call(["choco",
                                              "pack",
                                              Path(tempdir)/"imageglass.nuspec"]))
            f.write(str(rel.id)+"\n")
            f.flush()
        else:
            continue

    f.close()


def get_correct_release_asset_32(assets):
    for a in assets:
        if "_x86.msi" in a.name:
            return (a.browser_download_url, a.name)
    return ("", "")


def get_correct_release_asset_64(assets):
    for a in assets:
        if "_x64.msi" in a.name:
            return (a.browser_download_url, a.name)
    return ("", "")


def find_and_replace_templates(directory,
                               version,
                               tag,
                               url,
                               checksum,
                               filename,
                               url64,
                               checksum64,
                               filename64,
                               notes):
    os.mkdir(Path(directory)/"tools")
    d = dict(version=version,
             tag=tag,
             url=url,
             checksum=checksum,
             filename=filename,
             url64=url64,
             checksum64=checksum64,
             filename64=filename64,
             notes=notes)
    basepath = Path(os.getcwd())/"src/templates/imageglass/"
    templates = [
        "imageglass.nuspec",
        "tools/chocolateyInstall.ps1"]

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
