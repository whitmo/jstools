=========
 JSTools
=========

'JSTools' is a collection of utilities for managing JavaScript libraries.

Install
=======

Until jstools is released into pypi, we suggest checking out jstools
and installing using either 'python setup.py install' or 'python
setup.py develop' from within your checkout.


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

Options:
  -h [--help]            show this help message and exit
  -u [--uncompress]      Don't compresses aggregated javascript
  -v [--verbose]         print more info
  -o [--output=] OUTPUT_DIR
                         Output directory
  -r [--resource=] RESOURCE_DIR
                         resource base directory (used for interpolation)
  -s [--single=] SECTION
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


Buildout Support
================

see jsbuild/bo.txt

