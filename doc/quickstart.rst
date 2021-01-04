.. _quickstart:

Quickstart Tutorial
===============

Shifting Spectrum onto Model Wavelength Scale
---------------------------------------------

.. code-block:: python

   lib = smsyn.library.read_hdf(<path to coelho models>,wavlim=[4000,7000])
   hduL = fits.open(<path to spectrum>)
   wav = hduL[2].data
   uflux = hduL[1].data
   flux = hduL[0].data
   flux /= np.percentile(flux,95,axis=1)[:,np.newaxis]
   ref_wav = np.logspace(np.log10(np.min(wav)),np.log10(np.max(wav)),64000)
   ref_flux  = lib.synth(ref_wav,5700,4.5,0.0,1.0,0,)
   flux_shift, uflux_shift = smsyn.inst.hires.shift.shift(wav, flux, uflux, ref_wav, ref_flux)
   spec = smsyn.io.spectrum.Spectrum(ref_wav, flux_shift, uflux_shift, header=dct(name=name,obs=obs))
   spec.to_fits('output/{}_{}.sm.fits'.format(name,obs)) # Save to output

Run SpecMatch Algorithm
-----------------------

.. code-block:: python 

    from smsyn.inst.hires.pipeline import Pipeline
    outfile = 'output/{}_{}.sm.fits'.format(name,obs)
    libfile = '/Users/petigura/Dropbox/fulton_petigura/coelho05_2.hdf'
    pipe = Pipeline(outfile, libfile)
    pipe.grid_search(debug=False)
    pipe.lincomb()

Tests
====================
At the end of `test_hires_pipeline.py`, you should get:

.. code-block:: bash

          teff  logg   fe     vsini  psf     rchisq
    852   5750   5.0  0.0  4.912218    0   9.824765
    1627  5750   5.0  0.0  4.912218    0   9.824765
    1182  5750   3.5  0.0  5.271638    0  11.309809
    1756  5750   3.5  0.0  5.271638    0  11.309809
    1628  5750   4.5  0.0  5.266066    0  11.735292
    853   5750   4.5  0.0  5.266066    0  11.735292
    777   5750   4.5  0.0  5.266066    0  11.735292
    190   5750   4.0  0.0  5.409780    0  11.827457
    2685  5750   4.0  0.0  5.409780    0  11.827457
    573   5750   4.0  0.0  5.409780    0  11.827457
    teff logg fe vsini psf rchisq0 rchisq1
    Linear Combinations: <Spectrum: GANYMEDE, rj76.279, (5200.0-5280.0 Ang)>
    5818 4.57 +0.00 3.94 0.00 79.80 25.51
    Linear Combinations: <Spectrum: GANYMEDE, rj76.279, (5360.0-5440.0 Ang)>
    5753 4.33 +0.00 4.44 0.00 42.52 13.01
    Linear Combinations: <Spectrum: GANYMEDE, rj76.279, (5530.0-5610.0 Ang)>
    5750 4.39 +0.00 4.76 0.00 28.16 7.95
    Linear Combinations: <Spectrum: GANYMEDE, rj76.279, (6100.0-6190.0 Ang)>
    5748 4.30 +0.00 4.92 0.00 20.06 3.50
    Linear Combinations: <Spectrum: GANYMEDE, rj76.279, (6210.0-6260.0 Ang)>
    5750 4.35 +0.00 5.15 0.00 20.10 4.51


