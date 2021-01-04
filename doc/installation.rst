.. _installation:

Installation Instructions
===============

1. Install dependencies: `pandas`, `astropy`
2. Download ``specmatch-synth`` from git repo
3. Run ``python setup.py install`` from within the main repo directory
4. Download the Coelho+2005 spectral library from e.g., `http://specmodels.iag.usp.br/` or from Vizier.
5. Create the coelho.h5 file. If this doesn't exist, you can make it from the raw fits files using `bin/make_library_coelho05.py <path to fits directory> <path to output file> `
