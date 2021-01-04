#!/usr/bin/env python 
import os
from argparse import ArgumentParser
from smsyn.inst.hires.pipeline import Pipeline, grid_search, lincomb
from smsyn import DATA_DIR

if __name__=="__main__":
    psr = ArgumentParser() 
    psr.add_argument('libfile',type=str)
    args = psr.parse_args()
    outfile = os.path.join(DATA_DIR,'GANYMEDE_rj76.279.sm.fits')
    pipe = Pipeline(outfile, args.libfile)
    grid_search(pipe, debug=False)
    lincomb(pipe)
