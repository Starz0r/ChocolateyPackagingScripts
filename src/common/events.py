from typing import Generator
from github import Github
from github.GitRelease import GitRelease
from github.Tag import Tag

import os
import io

gh = Github(os.environ['GH_TOKEN'])

def on_new_git_release(pkg: str, repo_name: str) -> Generator[GitRelease, None, None]:
    # initalize state array
    state = []
    with io.open(pkg + ".ghstate", "a+") as f:
        f.seek(0)  # why I have to do this is unknown
        for _, line in enumerate(f):
            state.append(line)
    f = io.open(pkg + ".ghstate", "a+")

    # connect to github api
    repo = gh.get_repo(repo_name)

    # collect unpushed git releases
    for rel in repo.get_releases():
        pushed = False
        for i in range(len(state)):
            if str(state[i]).replace("\n", "") == str(rel.id):
                pushed = True
                break
            else:
                continue
        if pushed is False:
            yield rel
            f.write(str(rel.id) + "\n")
            f.flush()

def on_each_git_tag(pkg: str, repo_name: str) -> Generator[Tag, None, None]:
     # initalize state array
    state = []
    with io.open(pkg + ".ghtstate", "a+") as f:
        f.seek(0)  # why I have to do this is unknown
        for _, line in enumerate(f):
            state.append(line)
    f = io.open(pkg + ".ghtstate", "a+")

    # connect to github api
    repo = gh.get_repo(repo_name)

    # collect unpushed git tags
    for tag in repo.get_tags():
        pushed = False
        for i in range(len(state)):
            if str(state[i]).replace("\n", "") == str(tag.name):
                pushed = True
                break
            else:
                continue
        if pushed is False:
            yield tag
            f.write(str(tag.name) + '\n')
            f.flush()
