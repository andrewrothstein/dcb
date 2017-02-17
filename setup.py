from setuptools import setup

setup(name='dcb',
      version='0.0.1',
      description='Package for building docker containers',
      url='http://github.com/andrewrothstein/dcb',
      author='Andrew Rothstein',
      author_email='andrew.rothstein@gmail.com',
      license='MIT',
      packages=['dcb'],
      install_requires=['jinja2'],
      include_package_data=True,
      zip_safe=False,
      entry_points={
	'console_scripts': [
	  'dcb = dcb.main:main'
	  ]
	},
)
