.. _installation:

Installation Instructions
===============

1. Install dependencies: `pandas`, `astropy`, on a python2 environment. (See note below). Also, install `lmfit.
2. Download ``specmatch-synth`` from git repo
3. Run ``python setup.py install`` from within the main repo directory
4. Download the Coelho+2005 spectral library (~10Gb) from e.g., `http://specmodels.iag.usp.br/` or from Vizier.
5. Create the coelho.h5 file. If this doesn't exist, you can make it from the raw fits files using `bin/make_library_coelho05.py <path to fits directory> <path to output file> `

Regarding the py2->py3 upgrade
===============

Certain parts of the interpolation routines in `smsyn.match` use deprecated `scipy.interpolate` calls, include to `spleval` (see `https://docs.scipy.org/doc/scipy/reference/release.1.3.0.html?highlight=scipy%20interpolate%20spleval`).  This makes the py2->py3 update a bit harder than just changing the print statements.
