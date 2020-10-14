from github import Github
from github.GitRelease import GitRelease

import os
import io


def on_new_git_release(pkg: str, repo_name: str) -> GitRelease:
    # initalize state array
    state = []
    with io.open(pkg + ".ghstate", "a+") as f:
        f.seek(0)  # why I have to do this is unknown
        for _, line in enumerate(f):
            state.append(line)
    f = io.open(pkg + ".ghstate", "a+")

    # connect to github api
    gh = Github(os.environ['GH_TOKEN'])
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
