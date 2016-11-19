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
{% for resource in resources['classes'] %}    it { should contain_class('{{ resource }}') }\n{% endfor %}
{% for resource in resources['files'] %}    it { should contain_file('{{ resource }}') }\n{% endfor %}
  end
end
""")

class TestWriter(object):
    def __init__(self, classes):
        self.classes = classes

    def write(self, force=False):
        if force:
            flags = os.O_CREAT | os.O_RDWR | os.O_TRUNC 
        else:
            flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        for each in self.classes:
            print os.path.basename(each.test_filepath)
	    if not os.path.exists(os.path.dirname(each.test_filepath)):
		os.makedirs(os.path.dirname(each.test_filepath))
	    try:
                file_handle = os.open(each.test_filepath, flags)
	    except OSError as e:
		if e.errno == errno.EEXIST:  # Failed as the file already exists.
                    logger.warn('Warning: test file already exists. Use force option to overwrite existing tests')
		    pass
		else:  # Something unexpected went wrong so reraise the exception.
		    raise
	    else:  # No exception, so the file must have been created successfully.
		with os.fdopen(file_handle, 'w') as file_obj:
		    # Using `os.fdopen` converts the handle to an object that acts like a
		    # regular Python file object, and the `with` context manager means the
		    # file will be automatically closed when we're done with it.
		    file_obj.write(
                        spec_template.render(
	                    resources=each.resources,
                            name=each.name
                        )
                    )
