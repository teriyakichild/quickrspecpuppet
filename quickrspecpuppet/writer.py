import errno
import logging
import os
import os.path

from jinja2 import Template

logger = logging.getLogger('quickrspecpuppet')

spec_template = Template("""require 'spec_helper'
describe '{{ name }}' do
  before(:each) do
    # We can mock hiera the same way we mock any other function
    MockFunction.new('pwsafe_lookup') { |f|
      # Sets up some mock data in hiera
      f.stubs(:call).with(anything()).returns('password')
    }
  end
  context 'using defaults in prod tier' do
    let :facts do
    {
      :kernel                    => 'Linux',
      :memorysizeinbytes         => 2048000000,
      :osfamily                  => 'RedHat',
      :operatingsystem           => 'CentOS',
      :operatingsystemrelease    => '6',
      :operatingsystemmajrelease => '6',
      :tier                      => 'prod'
    }
    end
    it { is_expected.to compile }

{% for resource in resources['classes'] %}    it { is_expected.to contain_class('{{ resource }}') }\n{% endfor %}
{% for resource in resources['files'] %}    it { is_expected.to contain_file('{{ resource }}') }\n{% endfor %}
{% for resource in resources['packages'] %}    it { is_expected.to contain_package('{{ resource }}') }\n{% endfor %}
  end
end
""")

fixtures_template = Template("""fixtures:
  repositories:
{% for module in git_modules %}    {{ module.name }}: "{{ module.url }}"\n{% endfor %}
  symlinks:
    {{ module_name }}: "#{source_dir}"
""")


class TestWriter(object):

    def __init__(self, parser):
        self.classes = parser.classes
        self.dependencies = parser.dependencies
        self.fixtures_path = '{0}/{1}'.format(
            parser._directory, '/.fixtures.yml')
        self.class_name = parser.class_name
        self.force = False

    def write_tests(self):
        for each in self.classes:
            logger.info('Writing {0}'.format(
                os.path.basename(each.test_filepath)))
            if not os.path.exists(os.path.dirname(each.test_filepath)):
                os.makedirs(os.path.dirname(each.test_filepath))
            template_args = {'resources': each.resources, 'name': each.name}
            self.write(each.test_filepath, spec_template, template_args)

    def write_fixtures(self):
        template_args = {'git_modules': self.dependencies,
                         'module_name': self.class_name}
        self.write(self.fixtures_path, fixtures_template, template_args)

    def write(self, filepath, template, template_args):
        if self.force:
            flags = os.O_CREAT | os.O_RDWR | os.O_TRUNC
        else:
            flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        try:
            file_handle = os.open(filepath, flags)
        except OSError as e:
            if e.errno == errno.EEXIST:  # Failed as the file already exists.
                logger.warn(
                    'Warning: {0} already exists. Use force option to overwrite existing files'.format(filepath))
                pass
            else:  # Something unexpected went wrong so reraise the exception.
                raise
        else:  # No exception, so the file must have been created successfully.
            with os.fdopen(file_handle, 'w') as file_obj:
                # Using `os.fdopen` converts the handle to an object that acts like a
                # regular Python file object, and the `with` context manager means the
                # file will be automatically closed when we're done with it.
                file_obj.write(template.render(**template_args))
