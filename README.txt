=========
 JSTools
=========

'JSTools' is a collection of utilities used by the openlayers
development team for managing javascript.

Install
=======

until jstools is released into pypi, we suggest checking out jstools
and installing using either 'python setup.py install' or 'python
setup.py develop' from within your checkout.


Scripts
=======

jsbuild
-------

merges and compresses files according to a configuration file.
JSbuild will walk each root directory specified in configuration,
index all the files ending with .js and then compile an aggregate
source based on the specification in the config file and the
dependencies declared inside the files themselves.


Usage
~~~~~

jsbuild /path/to/config /path/to/outputdir

Options
+++++++

Options:
  -h, --help            show this help message and exit
  -u, --uncompress      Don't compresses aggregated javascript
  -v, --verbose         print more info
  -o OUTPUT_DIR, --output=OUTPUT_DIR
                        Output directory
  -r RESOURCE_DIR, --resource=RESOURCE_DIR
                        resource base directory (used for interpolation)
  -s SINGLE_FILE, --single=SINGLE_FILE
                        Only create file for this section (see below)

Configuration Format
~~~~~~~~~~~~~~~~~~~~

A config file may have multiple uniquely named output files (ie
multiple sections).

A section is formatted in the following fashion::

[Output.js]
root=path/to/where/files/are
license=path/to/license/for/these/libs
first=        
      3rd/prototype.js
      core/application.js
      core/params.js

last=
     core/api.js

exclude=
      3rd/logger.js
...


The files listed in the `first` section will be forced to load
*before* all other files (in the order listed). The files in `last`
section will be forced to load *after* all the other files (in the
order listed).

The files list in the `exclude` section will not be imported.

The configuration allows for the interpolation of variables defined in
the config file.  '%(resource-dir)s' may be subsituted for the value
of the -r flag.

Lines commented using '#' will be ignored. 


Dependency Syntax
~~~~~~~~~~~~~~~~~

Filemerging uses cues inside the canidate javascript files to
determine dependencies.

Dependencies are specified with a comment of the following format in
the javascript source file:

     // @requires <file path>

  e.g.

    // @requires Geo/DataSource.js


License
~~~~~~~
-- Copyright 2005-2007 MetaCarta, Inc. / OpenLayers project --



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


shrinksafe
----------

not currently supported

Buildout Support
================

see jsbuild/bo.txt

