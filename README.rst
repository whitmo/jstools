=========
 JSTools
=========

 'JSTools' is a collection of utilities for managing JavaScript libraries.

Install
=======

 Until jstools is released into pypi, we suggest checking out jstools
 and installing using either 'python setup.py install' or 'python
 setup.py develop' from within your checkout.

Requirements
------------

 Should be python 2.4 friendly, tested most on python 2.5

Easy Install
------------

 $ easy_install jstools

 This will put the following scripts in '/your/python/distribution/bin'::

 $ bin/jsbuild
 $ bin/jsmin

 Depending on your system, this action may require sudo.


Environment Install
-------------------

 'jstools' includes a script to create a contained python
 environment. This script also automatically downloads the yui
 compressor and puts it in a place jstools can find it.

 This script will turn a folder of your choice into a python
 environment [#]_ with the jstools scripts installed in a directory
 called 'bin'::

   $ easy_install -b ./ -e jstools
   $ python jstools/install_jstools ./jsdir

 This makes 'jsdir' jstools enabled with it's own 'bin'. source the
 script 'bin/activate', and now jsbuild and jsmin are on your path::

   $ cd jsdir
   $ . bin/activate


Other Distribution Options
--------------------------

 You can download jstools in whatever flavor your prefer::

  $ wget http://github.com/whitmo/jstools/tarball/master
  $ svn co http://svn.opengeo.org/jstools/trunk/ # not currently working
  $ git clone git://github.com/whitmo/jstools.git


Scripts
=======

jsbuild
-------

 Merges and compresses files according to a configuration file.
 jsbuild will walk each root directory specified in configuration,
 index all the files ending with .js and then compile an aggregate
 source based on the specification in the config file and the
 dependencies declared inside the files themselves.


Usage
~~~~~

jsbuild <config_file> [options]



Options
+++++++

Usage: jsbuild [options] filename1.cfg [filename2.cfg...]

Options:
  -h, --help
      show this help message and exit

  -u, --uncompress
      Don't compresses aggregated javascript. jsbuild defaults to
      applying 'jsmin' to all output.

  -v, --verbose
      print more info

  -o OUTPUT_DIR, --output=OUTPUT_DIR
     Output directory for files jsbuild creates

  -r RESOURCE_DIR, --resource=RESOURCE_DIR
     base directory for resource files (for interpolation)

  -j SINGLE_FILE, --just=SINGLE_FILE
     *New in 1.1*: Only create file for this section

  -s CONCAT, --single-file-build=CONCAT
     *New in 1.1*. Create a single file of all of possible output

  -c COMPRESSOR, --compressor=COMPRESSOR
     *New in 1.1*. Specify compressor plugin to use in form
     {specifier}:{'arguments_string'}.


Configuration Format
~~~~~~~~~~~~~~~~~~~~

A config file may have multiple uniquely named output files (ie
multiple sections).

A section is formatted in the following fashion::

 [Output.js]
 root=
      path/to/where/files/are
      other/path/to/where/files/are

 license=path/to/license/for/these/libs

 first=        
      3rd/prototype.js
      core/application.js
      core/params.js

 last=
     core/api.js

 exclude=
      3rd/logger.js
 #...


The files listed in the `first` section will be forced to load
*before* all other files (in the order listed). The files in `last`
section will be forced to load *after* all the other files (in the
order listed).

The files list in the `exclude` section will not be imported.

The configuration allows for the interpolation of variables defined in
the config file.  '%(resource-dir)s' may be subsituted for the value
of the -r flag.

Lines commented using '#' will be ignored. 

If an `include` section is defined, jsbuild will only build listed
files from this section and theirs dependencies, else all files from
`root` section will be built.


Dependency Syntax
~~~~~~~~~~~~~~~~~

File merging uses cues inside the candidate javascript files to
determine dependencies.  Two types of dependencies are specified 
with two different comment formats within source files.

To specify that a target files must be included before a given 
source file, include a comment of the following format:

     // @requires <file path>

  e.g.

    // @requires Geo/DataSource.js

To specify that a target file must be included at any place
in the merged build - before or after a given source file - 
include a comment in the source file of the following format:

    // @include <file path>

  e.g.

    // @include Geo/DataSource.js

Note that the "exclude" list in a configuration file will 
override dependencies specified by the @requires and @include
comment directives described above.

jsmin
-----

Compresses an input stream of javascript to an output stream


Usage
~~~~~

jsmin < cat some.js > some-compressed.js


License
~~~~~~~
-- The Software shall be used for Good, not Evil. --

see file for complete copyright


License
=======

Mixed. same as OpenLayers unless otherwhise noted


Buildout Support
================

see jstools/bo.txt


Run Tests
=========

 in the src dir in an environment w/ yuicomp installed::
  
  $ easy_install nose
  $ paver get_yuicomp
  $ cd test 
  $ nosetests {options}

 or most simply::

  $ python setup.py test
 

Credits
=======

jstools started as a collection of build scripts as part of the
OpenLayers Project[#]_.

Whit Morriss (whit at opengeo.org) repackaged these scripts as jstools
and Tim Schaub (tschaub at opengeo.org) did extensive reworking of tsort.


.. [#] See 'virtualenv <http://pypi.python.org/pypi/virtualenv>'_ for
       more information about the python environment.  You may activate
       and deactivate this environment to add the installed scripts to
       your path, localize python package installs and other niceties
       ala::

        $ source bin/activate
        $ deactivate

.. [#] `OpenLayers Homepage <http://www.openlayers.org>`_ and `the
       original scripts <http://svn.openlayers.org/trunk/openlayers/tools/>`_

