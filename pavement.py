try:
    from paver.virtual import bootstrap
except :
    # minilib does not support bootstrap
    pass
import os
from paver.easy import *
from paver.easy import task, options, Bunch
from paver.easy import cmdopts #,consume_args
from paver.easy import path, sh, info
from paver.easy import call_task #debug,
from paver.tasks import help, needs
from setuptools import find_packages
from paver.setuputils import setup
from ConfigParser import ConfigParser

version = '0.1'

try:
    description = ''.join([x for x in open('README.txt')])
except IOError:
    description = ""

setup(
    name='JSTools',
    version=version,
    description="assorted python tools for building (packing, aggregating) javascript libraries",
    long_description=description,
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='javascript',
    author='assorted',
    author_email='info@opengeo.org',
    url='http://projects.opengeo.org/jstools',
    license='various/BSDish',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    entry_points="""
    [zc.buildout]
    default=jstools.bo:BuildJS
    buildjs=jstools.bo:BuildJS
    [console_scripts]
    jsbuild=jstools.build:build
    jsmin = jstools.jsmin:minify
    [jstools.jsbuild_command]
    default=jstools.build:default_merge
    [jstools.compressor]
    default=jstools.jsmin:compressor_plugin
    yui=jstools.yuicompressor:compress [yuicompressor]
    """,
    extras_require=dict(yuicompressor="Paver"),
    test_suite='nose.collector',
    tests_require=['nose']
    )

options(virtualenv=Bunch(script_name="install_jstools",
                         packages_to_install=[],
                         paver_command_line="install_jstools"
                         ),
        yui_compressor=Bunch(compressor_version = "2.4.2",
                             zip_name = lambda: "yuicompressor-%s.zip" % options.compressor_version,
                             url = lambda: "http://www.julienlecomte.net/yuicompressor/%s" % \
                             options.zip_name,
                             )
        )

@task
@needs(['get_yuicomp', 'setuptools.command.develop'])
def install_jstools():
    info("All Done")

DEFAULT_CFG = ".jstools.cfg"

@task
def create_jstools_userconfig():
    current_dir = path.getcwd()
    jst_conf = current_dir / DEFAULT_CFG
    if not jst_conf.exists():
        info("Creating %s" %jst_conf)
        jst_conf.touch()
        # @@ create conf with defaults here??

def set_yui_version(conf, version, yui_dir):
    parser = ConfigParser()
    parser.read(conf)
    section = "yui_compressor"
    if not parser.has_section(section):
        parser.add_section(section)
    jars = (yui_dir / "lib").glob("*.jar")
    cp = ":".join(jars)
    parser.set(section, "classpath", cp)
    parser.set(section, "jarpath", (yui_dir / "build").glob("*.jar")[0])
    parser.write(conf.open("w+"))


@task
@needs(['create_jstools_userconfig'])
@cmdopts([("compressor_version=", "v", "compressor version to download"),
          ("set_as_default", "", "set this version as default for local configuration"),
          ("overwrite", 'o', "overwrite old version")])
def get_yuicomp():
    current_dir = path.getcwd()
    lib_dir = current_dir / "lib" 
    if not lib_dir.exists():
        lib_dir.mkdir()
    yui_dir = lib_dir / ("yuicompressor-%s" % options.compressor_version)
    jst_conf = current_dir / DEFAULT_CFG

    if getattr(options, "overwrite", False) and yui_dir.exists():
        sh("rm -rf %s" %yui_dir)
    
    if not yui_dir.exists():
        zip_file = lib_dir / options.zip_name
        lib_dir.chdir()
        if not zip_file.exists():
            info("Downloading %s", options.url)
            sh("curl -O %s" % options.url)
        sh("unzip %s" % options.zip_name)
        set_yui_version(jst_conf, options.compressor_version, yui_dir)
        current_dir.chdir()
        return True

    info("yui compressor already downloaded")
    
    if options.set_as_default:
        set_yui_version(jst_conf, options.compressor_version, yui_dir)




