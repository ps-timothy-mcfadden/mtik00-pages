# mtik00-pages

Development environment for mtik00.github.io

# Develop steps
1.  Set environment: `env.bat`
1.  Create a new post: `np`
1.  Test it: `hugo server --watch --source="site" --bind="localhost"`
1.  Add it: `git add -A`
1.  Commit it: `git ci -am"new content"`
1.  Push it: `git push`
1.  Build it: `fab release`