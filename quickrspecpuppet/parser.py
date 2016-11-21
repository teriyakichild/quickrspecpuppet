import json
import logging
import os
import os.path
import regex

logger = logging.getLogger('quickrspecpuppet')


class ManifestParser(object):

    def __init__(self, directory=None):
        self.classes = []
        if directory is None:
            directory = os.getcwd()
        self._directory = directory
        self._manifests = self.find_manifests()

    def find_manifests(self):
        manifests = []
        for dirpath, dirnames, filenames in os.walk('{0}/{1}'.format(self._directory, 'manifests')):
            for filename in [f for f in filenames if f.endswith(".pp")]:
                manifests.append(os.path.join(dirpath, filename))
        return manifests

    def parse(self):
        # parse the modulefile or metadata.json, if they exist.
        self.dependencies = []
        for name in self.parse_modulefile() + self.parse_metadata():
            self.dependencies.append(PuppetDependency(name))
        # parse each manifest for classname and resources
        for filepath in self._manifests:
            matches = self.search_file(
                filepath, r'class \K[a-zA-Z0-9_:]+(?= [{(])')
            resources = {}
            if any(matches):
                self.class_name = matches[0].split('::')[0]
                resources['classes'] = self.parse_resources('class', filepath)
                resources['files'] = self.parse_resources('file', filepath)
                resources['packages'] = self.parse_resources(
                    'package', filepath)
                self.classes.append(PuppetClass(
                    matches[0], filepath, resources, self._directory))

    def parse_resources(self, resource_type, filepath):
        return self.search_file(filepath, r"{0} {{ ['\"]?\K[a-zA-Z0-9_:\{{\}}\./$]+(?=['\"]?:)".format(resource_type))

    def parse_modulefile(self):
        modulefile_path = '{0}/{1}'.format(self._directory, 'Modulefile')
        if os.path.exists(modulefile_path):
            logger.debug(
                'DEBUG: modulefile {0} exists'.format(modulefile_path))
            return self.search_file(modulefile_path, r"dependency ['\"]?\K[a-zA-Z0-9_/]+(?=['\"]?, )")
        return []

    def parse_metadata(self):
        metadata_path = '{0}/{1}'.format(self._directory, 'metadata.json')
        if os.path.exists(metadata_path):
            logger.debug('DEBUG: metadata {0} exists'.format(metadata_path))
            metadata = json.loads(open(metadata_path, 'r').read())
            return [each['name'] for each in metadata.get('dependencies', [])]
        return []

    def search_file(self, filepath, regex_string):
        matches = [regex.search(regex_string, line)
                   for line in open(filepath)]
        if any(matches):
            matches = [x[0] for x in matches if x is not None]
        else:
            matches = []
        return matches


class PuppetClass(object):

    def __init__(self, name, manifest, resources, base_dir):
        self.base_dir = base_dir
        self.resources = resources
        self.name = name
        self.manifest = manifest
        self.test_filepath = self._generate_test_filepath()

    def _generate_test_filepath(self):
        parts = self.name.split('::')
        parts.pop(0)
        if len(parts) < 1:
            parts = ['init']
        return '{0}/{1}/{2}_spec.rb'.format(self.base_dir, 'spec/classes', '/'.join(parts))


class PuppetDependency(object):

    def __init__(self, name):
        name_parts = name.split('/')
        try:
            self.url = 'git@github.com:{0}/{1}.git'.format(*name_parts)
        except IndexError:
            raise Exception(
                'Invalid format for puppet module name ({0}), should be "owner/repo_name"'.format(name))
        logger.debug('DEBUG: parsed dependency as {0}'.format(self.url))
        self.url = 'git@github.com:{0}/{1}.git'.format(*name.split('/'))
        self.name = name_parts[1]
