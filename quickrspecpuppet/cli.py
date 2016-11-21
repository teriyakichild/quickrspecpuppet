"""Quickly create basic rspec tests for your puppet modules

Usage:
  quickrspecpuppet [ --directory=DIRECTORY ] [ --force ] [ --verbose ]
  quickrspecpuppet (-h | --help)

Options:
  -d, --directory=DIRECTORY Base directory of puppet module [default: os.cwd]
  -f, --force               Overwrite tests if they exist
  -v, --verbose             Enable verbose logging
  -h, --help                Show this screen.

"""
import logging
from quickrspecpuppet import __version__
from quickrspecpuppet.parser import ManifestParser
from quickrspecpuppet.writer import TestWriter

from docopt import docopt


def main():
    # instanstiate logger
    logger = logging.getLogger('quickrspecpuppet')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    # Parse command line arguments
    arguments = docopt(__doc__, version=__version__)

    if arguments['--verbose']:
        logger.info('Setting log level to DEBUG')
        logger.setLevel(logging.DEBUG)

    parser = ManifestParser(directory=arguments['--directory'])
    parser.parse()

    writer = TestWriter(parser)
    writer.force = arguments['--force']
    writer.write_tests()
    writer.write_fixtures()

if __name__ == '__main__':
    main()
