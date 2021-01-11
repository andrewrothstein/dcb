from setuptools import setup, find_packages

setup(name='dcb',
      version='0.0.18',
      description='CLI for building, tagging, and publishing Docker containers',
      url='http://github.com/andrewrothstein/dcb',
      author='Andrew Rothstein',
      author_email='andrew.rothstein@gmail.com',
      license='MIT',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      package_data={"dcb": ["snippets/*"]},
      python_requires='>=3.5',
      install_requires=['jinja2'],
      tests_require=['nose2'],
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'dcb = dcb.main:main'
          ]
      },
      )
