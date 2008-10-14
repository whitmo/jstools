from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='JSTools',
      version=version,
      description="assorted python tools for building (packing, aggregating) javascript libraries",
      long_description="""   """,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='javascript',
      author='assorted',
      author_email='info@opengeo.org',
      url='',
      license='various',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=["decorator"],
      entry_points="""
      [zc.buildout]
      default=jstools.bo:BuildJS
      buildjs=jstools.bo:BuildJS
      [console_scripts]
      jsbuild=jstools.build:build
      jsmin = jstools.jsmin:minify
      """,
      )
