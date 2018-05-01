# cmpdirs
Verifies that all files contained within one directory tree are also part of a second directory tree.

## Build project

```bash
# Clone project
git clone https://github.com/seko24/cmpdirs.git

# Install all dependencies (including development dependencies) into new virtual environment:
pipenv install --dev

# Activate the virtual environment
pipenv shell

# Run the script
cmpdirs --help
```

## Build executable

```bash
pipenv run pyinstaller cmpdirs.spec
dist/cmpdirs testA/ testB/
```
