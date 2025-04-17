# git notes

### create, switch, rename, delete, etc.

`git branch <name>` \
creates a new branch

`git checkout <name>`
or
`git switch <name>` \
switches brarnch

`git branch -m <new-name>` \
renames head branch (current branch) \
`git branch -m <old-name> <new-name>` \
renames <old-name> branch 

`git branch -v`\
lists branches with last commit

`git branch -d`\
delete branch

### merge

`git switch <target-branch>`\
`git merge <source-branch>`

### commit difference betwen branches

`git log <branch-1>..<branch-2>` \
shows commits from branch-2 that are not present in branch-1 \
also works with origin/branch
