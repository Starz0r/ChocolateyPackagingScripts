import subprocess
import os
import xml.etree.ElementTree as XMLeTree
from typing import Dict
import semver
import tempfile
from pathlib import Path
import shutil

from common.common import abort_on_nonzero


def main():
    # get the list of dotnet packages
    f = open("dotnet_list.txt", "r")
    dotnets: Dict[str, str] = {}
    new_dotnets: Dict[str, str] = {}
    for line in f.readlines():
        dotnet = line.split(" ")
        dotnets[dotnet[0]] = dotnet[1].rstrip()
    f.close()

    # check chocolatey to see if any of them are updated
    for pkg, ver in dotnets.items():
        proc = subprocess.run(
            ["choco", "info", "--limit-output", pkg], capture_output=True
        )
        ver_query = proc.stdout.decode().rstrip().split("|")[1]
        if ver != ver_query:
            print("version: " + ver + ", does not equal: " + ver_query)
        new_dotnets[pkg] = ver_query

    # if dotnets == new_dotnets:
    #    return

    # insert to the dependency list
    etree = XMLeTree.parse("src/templates/dotnet-all/dotnet-all.nuspec")

    version = etree.findall(
        ".//{http://schemas.microsoft.com/packaging/2015/06/nuspec.xsd}version"
    )[0]
    new_version = semver.VersionInfo.parse(version.text).bump_patch().__str__()
    version.text = new_version

    dep_tree = etree.findall(
        ".//{http://schemas.microsoft.com/packaging/2015/06/nuspec.xsd}dependencies"
    )[0]
    f = open("dotnet_list_new.txt", "w")
    size = len(new_dotnets)
    i = 0
    for pkg, ver in new_dotnets.items():
        f.write(pkg + " " + ver)
        if i != size - 1:
            f.write("\n")
        i += 1
        dep = XMLeTree.Element("dependency")
        dep.set("id", pkg)
        dep.set("version", ver)
        dep_tree.append(dep)
    f.flush()
    f.close()

    # package the software
    tmpdir = tempfile.mkdtemp()
    p = Path(tmpdir) / "dotnet-all.nuspec"
    f = open(p, "wb+")
    f.write(XMLeTree.tostring(etree.getroot()))
    f.flush()
    f.close()
    abort_on_nonzero(subprocess.run(["choco", "pack", p], capture_output=True))
    shutil.move(Path(tmpdir) / "dotnet-all.nupkg", ".")
    print(subprocess.run(["rrr", tmpdir], capture_output=True))

    # overwrite the old list
    print(subprocess.run(["rrr", "dotnet_list.txt"], capture_output=True))
    os.rename("dotnet_list_new.txt", "dotnet_list.txt")


main()
