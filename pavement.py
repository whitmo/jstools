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
from paver.easy import call_task
from setuptools import find_packages
from paver.setuputils import setup
from ConfigParser import ConfigParser
from paver import setuputils

setuputils.install_distutils_tasks()
version = '0.2.2'

try:
    description = ''.join([x for x in open('README.rst')])
except IOError:
    description = ""

setup(
    name='JSTools',
    version=version,
    description="assorted python tools for building (packing, aggregating) javascript libraries",
    long_description=description,
    classifiers=["Development Status :: 3 - Alpha",
                 "Programming Language :: JavaScript",
                 "Topic :: Software Development :: Build Tools",
                 "License :: OSI Approved :: BSD License"
                 ], 
    keywords='javascript',
    author='assorted',
    author_email='jstools@googlegroups.com',
    url='https://github.com/camptocamp/jstools',
    license='various/BSDish',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=True,
    entry_points="""
    [zc.buildout]
    default=jstools.bo:BuildJS
    buildjs=jstools.bo:BuildJS
    [console_scripts]
    jsbuild=jstools.build:build
    jsmin = jstools.jsmin:minify
    jst = jstools.jst:run
    [jstools.jsbuild_command]
    default=jstools.build:default_merge
    [jstools.compressor]
    default=jstools.jsmin:compressor_plugin
    yui=jstools.yuicompressor:compress [yuicompressor]
    [jstools.docs]
    default=jstools.jst [sphinx]
    [paste.app_factory]
    main=jstools.proxy:make_proxy [proxy]
    """,
    extras_require=dict(yuicompressor=["Paver"],
                        sphinx=['Jinja2'],
                        proxy=['WSGIProxy']),
    
    test_suite='nose.collector',
    tests_require=['nose']
    )

options(virtualenv=Bunch(script_name="install_jstools",
                         packages_to_install=['nose', 'setuptools_git'], # packages for testing and packaging
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
@needs(['get_yuicomp','setuputils.command.test'])
def test():
    info("Tests are done")

## # paver egg_info -RDb "" sdist bdist_egg register upload
## @task
## @needs(['setuputils.command.egg_info'])
## def pypi_release(options):
##     """
##     Point release of jstools into pypi
##     """
##     tasks = ('distutils.command.sdist',
##              'setuputils.command.bdist_egg',
##              'distutils.command.register',
##              'distutils.command.upload')

##     for task in tasks:
##         try:
##             call_task(task)
##         except :
##             import pdb, sys; pdb.post_mortem(sys.exc_info()[2])
    
##     info("jstools released")

@task
@needs(['create_jstools_userconfig'])
@cmdopts([("compressor_version=", "v", "compressor version to download"),
          ("set_as_default", "y", "set this version as default for local configuration"),
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
    
    if getattr(options, 'set_as_default', None):
        set_yui_version(jst_conf, options.compressor_version, yui_dir)




