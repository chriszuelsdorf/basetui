# Processes

## Updating version

Follow [semver](https://semver.org/); for version x.y.z:
- Breaking changes increment major version number (x)
- New features increment minor version number (y)
- Patches increment patch version number (z)

Before merging breaking changes (i.e. a major release):
- Create a branch for the *current* major release. 
- In that branch, edit the readme in the new branch to reflect that there is a new major release available; describe the breaking changes.

Now that the niceties are out of the way and you've decided the new version number:
- Update it in `basetui/__init__.py`
- Update it in `setup.py`
- Update the changelog

Once it's in waiting, merge the branch to master!
