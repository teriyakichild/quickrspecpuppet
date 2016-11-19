# quickrspecpuppet

Python CLI that allows you to quickly create basic rspec tests for your puppet modules

## Get Started

Install `quickrspecpuppet` using one of the following:

    $ pip install quickrspecpuppet
    $ python setup.py install

Run `quickrspecpuppet` in the root directory of your puppet module:

    $ quickrspecpuppet

## Usage

Quickly create basic rspec tests for your puppet modules

```
Usage:
  quickrspecpuppet [ --directory=DIRECTORY ] [ --force ] [ --verbose ]
  quickrspecpuppet (-h | --help)

Options:
  -d, --directory=DIRECTORY Base directory of puppet module [default: os.cwd]
  -f, --force               Overwrite tests if they exist
  -v, --verbose             Enable verbose logging
  -h, --help                Show this screen.
```

## Packaging

Building an RPM:
```
make rpms
```
