from setuptools import setup
from sys import path

from quickrspecpuppet import __version__

path.insert(0, '.')

NAME = "quickrspecpuppet"

if __name__ == "__main__":

    with open('requirements.txt') as f:
        requirements = f.read().splitlines()

    setup(
        name=NAME,
        version=__version__,
        author="Tony Rogers",
        author_email="tony.rogers@rackspace.com",
        url="https://github.com/teriyakichild/quickrspecpuppet",
        license='ASLv2',
        packages=[NAME],
        package_dir={NAME: NAME},
        description="quickrspecpuppet - Quickly create basic rspec tests for your puppet modules",

        install_requires=requirements,

        entry_points={
            'console_scripts': ['quickrspecpuppet = quickrspecpuppet.cli:main'],
        }
    )
