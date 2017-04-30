"""Top-level fitting and polishing routines

"""
import numpy as np
import pandas as pd
import lmfit
import smsyn.io.spectrum
import smsyn.library
import smsyn.match
import smsyn.io.fits

def wav_exclude_to_wavmask(wav, wav_exclude):
    wavmask = np.zeros_like(wav).astype(bool) # Default: no points masked
    nwav_exclude = len(wav_exclude)
    for i in range(nwav_exclude):
        wav_min, wav_max = wav_exclude[i]
        wavmask[(wav_min < wav) & (wav < wav_max)] = True
    return wavmask

def grid_search(spec, libfile, wav_exclude, param_table, idx_coarse, idx_fine):
    """
    Args:
        spec0 (smsyn.spectrum.Spectrum): the spectrum
        libfile (str): path to library hdf5 file. 
        wav_exclude (list): define wavlengths to exclude from fit
            e.g. [[5018, 5019.5],[5027.5, 5028.5]] 
        param_table (pandas.DataFrame): table of grid values to search over
        idx_coarse (list): the indecies of `param_table` to use in the initial
            coarse search
        idx_fine (list): the indecies of `param_table` useable for the fine 
            search.
    """
    wavlim = spec.wav[0],spec.wav[-1]
    lib = smsyn.library.read_hdf(libfile,wavlim=wavlim)
    wavmask = wav_exclude_to_wavmask(spec.wav, wav_exclude)
    match = smsyn.match.Match(
        spec, lib, wavmask, cont_method='spline-dd', rot_method='rot'
    )
    
    # First do a coarse grid search
    print "performing coarse grid search"
    param_table_coarse = grid_search_loop(match, param_table.ix[idx_coarse])

    # For the fine grid search, 
    print "performing fine grid search"
    top = param_table_coarse.sort_values(by='rchisq').head(10) 
    tab = param_table.ix[idx_fine]
    tab = tab.drop(idx_coarse)

    param_table_fine = tab[
         tab.teff.between(top.teff.min(),top.teff.max()) & 
        tab.logg.between(top.logg.min(),top.logg.max()) & 
        tab.fe.between(top.fe.min(),top.fe.max()) 
    ]
    param_table_fine = grid_search_loop(match, param_table_fine)
    param_table = pd.concat([param_table_coarse, param_table_fine])

    cols = 'teff logg fe vsini  psf rchisq'.split()
    print param_table[cols].sort_values(by='rchisq').head(10) 

    return param_table

def grid_search_loop(match, param_table0):
    """Grid Search

    Perform grid search using starting values listed in a parameter table.

    Args:
        match (smsyn.match.Match): `Match` object.
        param_table0 (pandas DataFrame): Table defining the parameters to search
            over.

    Returns:
        pandas DataFrame: results of the grid search with the input parameters
            and the following columns added: `logprob` log likelihood, `chisq`
            chi-squared, and `rchisq` reduced chisq, `niter` number of 
            iterations
    """
    nrows = len(param_table0)
    param_keys = param_table0.columns    
    param_table = param_table0.copy()
    for col in 'chisq rchisq logprob nfev'.split():
        param_table[col] = np.nan
    params = lmfit.Parameters()
    for key in param_keys:
        params.add(key)
        params[key].vary=False

    nodes = smsyn.match.spline_nodes(match.spec.wav[0],match.spec.wav[-1])
    smsyn.match.add_spline_nodes(params, nodes, vary=False)
    params['vsini'].vary = True
    params['vsini'].min = 0.2
    
    print_grid_search()
    counter=0
    for i, row in param_table.iterrows():
        for key in param_keys:
            params[key].set(row[key])
        params['vsini'].min = 0.5
        mini = lmfit.minimize(match.nresid, params, method='leastsq',xtol=1e-3)
        for key in mini.var_names:
            param_table.loc[i, key] = mini.params[key].value
        param_table.loc[i,'chisq'] = mini.chisqr
        param_table.loc[i,'rchisq'] = mini.redchi
        param_table.loc[i,'nfev'] = mini.nfev

        nresid = match.masked_nresid( mini.params )
        logprob = -0.5 * np.sum(nresid**2) 
        param_table.loc[i,'logprob'] = logprob
        d = dict(param_table.loc[i])
        d['counter'] = counter 
        d['nrows'] = nrows
        print_grid_search(d)
        counter+=1
    return param_table

def print_grid_search(*args):
    if len(args)==0:
        print "        {:4s}  {:4s} {:3s}  {:4s}   {:8s} {:4s}".format(
            'teff','logg','fe','vsini','rchisq','nfev'
        )
    if len(args)==1:
        d = args[0]
        print "{counter:3d}/{nrows:3d} {teff:4.0f} {logg:4.1f} {fe:+2.1f} {vsini:6.1f}  {rchisq:8.2f} {nfev:4.0f}".format(**d)

def lincomb(spec, libfile, wav_exclude, param_table):
    """
    """
    ntop = len(param_table)
    wavlim = spec.wav[0],spec.wav[-1]
    lib = smsyn.library.read_hdf(libfile,wavlim=wavlim)
    wavmask = wav_exclude_to_wavmask(spec.wav, wav_exclude)
    match = smsyn.match.Match(spec, lib, wavmask, cont_method='spline-dd',rot_method='rot')
    model_indecies = np.array(param_table.model_index.astype(int))
    match = smsyn.match.MatchLincomb(
        spec, lib, wavmask, model_indecies, cont_method='spline-dd',
        rot_method='rot'
    )
    params = lmfit.Parameters()
    nodes = smsyn.match.spline_nodes(
        spec.wav[0],spec.wav[-1], angstroms_per_node=10
    )
    smsyn.match.add_spline_nodes(params, nodes, vary=False)
    smsyn.match.add_model_weights(params, ntop, min=0.01)
    params.add('vsini',value=5)
    params.add('psf',value=1.0, vary=False)

    def rchisq(params):
        nresid = match.masked_nresid(params)
        return np.sum(nresid**2) / len(nresid)

    out = lmfit.minimize(match.masked_nresid, params)
    nresid = match.masked_nresid(params)

    #print lmfit.fit_report(out)
    mw = smsyn.match.get_model_weights(out.params)
    mw = np.array(mw)
    mw /= mw.sum()

    params_out = lib.model_table.iloc[model_indecies]
    params_out = params_out['teff logg fe'.split()]
    params_out = pd.DataFrame((params_out.T * mw).T.sum()).T
    params_out['vsini'] = out.params['vsini'].value
    params_out['psf'] = out.params['psf'].value
    params_out['rchisq0'] = rchisq(params)
    params_out['rchisq1'] = rchisq(out.params)
    return params_out

def polish(match, params0, angstrom_per_node=20, objective_method='nresid'):
    """Polish parameters
    
    Given a list of match object, polish the parameters segment by segment

    Args:
        match (smsyn.match.Match): Match objects.
        params0 (lmfit.Parameters): lmfit.Parameters object with initial guesses
        angstrom_per_node (float): approximate separation between continuum and
            spline nodes. Number of nodes will be rounded to nearest integer.
        objective_method (string): name of objective function. Must be a method
            of the Match object {'chi2med','nresid'}

    Returns
        dict: with following keys:
            - result
            - model
            - wav
            - resid
            - objective
    """
    params = lmfit.Parameters()
    for name in params0.keys():
        params.add(name)
        params[name].value = params0[name].value
        params[name].vary = params0[name].vary
        params[name].min = params0[name].min
        params[name].max = params0[name].max

    params['vsini'].min = 0
    params['psf'].vary =False

    wavlim = match.spec['wav'][[0,-1]]
    node_wav = smsyn.match.spline_nodes(
        wavlim[0], wavlim[1], angstroms_per_node=angstrom_per_node,
    )

    for _node_wav in node_wav:
        key = 'sp%d' % _node_wav
        params.add(key)
        params[key].value = 1.0

    objective = getattr(match,objective_method)
    def iter_cb(params, iter, resid):
        pass
    out = lmfit.minimize(
        objective, params, method='leastsq', iter_cb=iter_cb
    )
    resid = match.resid(out.params)
    out.params.pretty_print()
    medresid = np.median(resid)
    resid -= medresid
    d = dict(
        result=out, model=match.model(out.params), 
        wav=match.spec.wav, resid=resid, 
        objective=objective(out.params)
    )

    return d
