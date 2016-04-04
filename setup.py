from setuptools import setup, find_packages

setup(
  name='cltk_capitains_corpora_converter',
  version="0.0.1",
  description='CLTK Converter for Capitains Guidelines Repository',
  url='http://github.com/cltk/capitains_corpora_converter',
  author='Thibault Clerice',
  author_email='leponteineptique@gmail.com',
  license='MIT',
  packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
  install_requires=[
    "MyCapytain>=0.1.3",
    "gitpython==1.0.2"
  ],
  entry_points={
      'console_scripts': ['capitains-cltk-converter=cltk_capitains_corpora_converter:cmd'],
  },
  test_suite="tests"
)