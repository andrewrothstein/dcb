from setuptools import setup

setup(name='dcb',
      version='0.0.7',
      description='CLI for building Docker containers',
      url='http://github.com/andrewrothstein/dcb',
      author='Andrew Rothstein',
      author_email='andrew.rothstein@gmail.com',
      license='MIT',
      packages=['dcb'],
      install_requires=['jinja2'],
      zip_safe=False,
      entry_points={
	'console_scripts': [
	  'dcb = dcb.main:main'
	  ]
	},
)
