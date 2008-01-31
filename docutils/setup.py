# By the fires of hades! docutils searches for readers and transforms that are in the same directory
# rather than using the full search path.  Thus it won't find my readers and transforms unless
# I put them directly into the docutils package.  I'll think of a better way to do this later. --Dave

#import sys
#try:
#    from distutils.core import setup
#except ImportError:
#    print 'Error: The "distutils" standard module, which is required for the '
#    print 'installation of Docutils, could not be found.  You may need to '
#    print 'install a package called "python-devel" (or similar) on your '
#    print 'system using your package manager.'
#    sys.exit(1)
#
#setup(name="docutils BEP extensions",
#      version="1.0",
#      description = "scripts to process BitTorrent Enhancement Proposals rst files into html files",
#      author="BitTorrent, Inc.",
#      packages=['docutils_bep'],
#      #package_data={'BTL.canonical': ['metadata.html', 'metadata_example.html', 'metadata_source.html']},
#      #ext_modules=[Extension('cmap_swig', ['BTL/cmap_swig.i'],
#      #    extra_compile_args=compilerArgs, language=lang, swig_opts=swigOpts)],
#      )
