# Convert Teffs to B-V colours, or vice-versa
# using the sekiguchi and fukugita conversion.

import numpy as np
import matplotlib.pyplot as pl
from error_propagator import propagate

plotpar = {'axes.labelsize': 20,
           'text.fontsize': 20,
           'legend.fontsize': 15,
           'xtick.labelsize': 18,
           'ytick.labelsize': 18,
           'text.usetex': True}
pl.rcParams.update(plotpar)

def bv2teff(bv, logg, feh):
    # best fit parameters
    c = [3.929883, -0.360726, 0.168806, -0.048300]
    f = [0.025761, 0.004537]
    g1 = 0.007367
    h1 = -0.01069
    return c[0] + c[1]*bv + c[2]*bv**2 + c[3]*bv**3 + \
            f[0]*feh + f[1]*feh**2 + g1*logg + h1*bv*logg

def teff2bv(teff, logg, feh, teff_err, logg_err, feh_err, error=False):

    # best fit parameters
    t = [-813.3175, 684.4585, -189.923, 17.40875]
    t_err = [42.5, 34.3, 9.23, 0.827]
    f = [1.2136, 0.0209]
    f_err = [0.038, 0.0006]
    d1 = -0.294
    d1_err = 0.010
    g1 = -1.166
    g1_err = 0.028
    e1 = 0.3125
    e1_err = 0.0076

    if error==False:
        return t[0] + t[1]*np.log10(teff) + t[2]*(np.log10(teff))**2 + \
                t[3]*(np.log10(teff))**3 + f[0]*feh + f[1]*feh**2 \
                + d1*feh*np.log10(teff) + g1*logg + e1*logg*np.log10(teff)

    # partial derivatives
    dfdT = ( (np.log10(10))**2*(t[1]+d1*feh+e1*logg) + t[2]*np.log10(100) + 3*t[3]*(np.log10(teff))**2 )/(teff*(np.log10(10)**3))
    dfdF = f[0] + 2*f[1]*feh + d1*np.log10(teff)
    dfdG = g1 + e1*np.log10(teff)
    dfdt0 = 1.
    dfdt1 = np.log10(teff)
    dfdt2 = (np.log10(teff))**2
    dfdt3 = (np.log10(teff))**3
    dfdf0 = feh
    dfdf1 = feh**2
    dfdd1 = feh*np.log10(teff)
    dfdg1 = logg
    dfde1 = logg*np.log10(teff)

    pds = np.array([dfdT, dfdF, dfdG, dfdt0, dfdt1, dfdt2, dfdt3, dfdf0, dfdf1, dfdd1, dfdg1, dfde1])
    vs = np.zeros((len(teff), len(pds)))
    vs[:,0], vs[:,1], vs[:,2] = teff, feh, logg
    o = np.ones_like(teff)
    vs[:,3], vs[:,4], vs[:,5], vs[:,6], vs[:,7], vs[:,8], vs[:,9], vs[:,10], vs[:,11] = o*t[0], o*t[1], o*t[2], o*t[3], o*f[0], o*f[1], o*d1, o*g1, o*e1
    errs = np.zeros((len(teff), len(pds)))
    errs[:,0], errs[:,1], errs[:,2] = teff_err, feh_err, logg_err
    errs[:,0], errs[:,4], errs[:,5], errs[:,6], errs[:,7], errs[:,8], errs[:,9], errs[:,10], errs[:,11] = o*t_err[0], o*t_err[1], o*t_err[2], o*t_err[3], \
            o*f_err[0], o*f_err[1], o*d1_err, o*g1_err, o*e1_err
    error = propagate(pds, vs, errs)

    return t[0] + t[1]*np.log10(teff) + t[2]*(np.log10(teff))**2 + \
            t[3]*(np.log10(teff))**3 + f[0]*feh + f[1]*feh**2 \
            + d1*feh*np.log10(teff) + g1*logg + e1*logg*np.log10(teff), error

if __name__ == "__main__":
    # load data
    data = np.genfromtxt('/Users/angusr/Python/Gyro/data/data.txt').T
    teff = data[3]
    logg = data[10]
    feh = data[5]

    bv = teff2bv(teff, logg, feh)

#     print np.polyfit(teff[teff>0], bv[np.isfinite(bv)], 1)

    saveas = np.ndarray((len(data[0]), 2)).T
    saveas[0,:] = data[0]
    saveas[1,:] = bv

    np.savetxt("/Users/angusr/Python/Gyro/data/colours.txt", saveas)

    pl.clf()
    pl.plot(teff, bv, 'k.')
    pl.savefig("/Users/angusr/Python/Gyro/plots/teff_bv")

    pl.clf()
    logt = np.log10(teff[teff>0])
    logc = np.log10(bv[teff>0])
    pl.plot(logc, logt, 'k.')
    plv = np.polyfit(logc, logt, 1)
    print 'logt = ', plv[0], 'logc + ', plv[1]
    plt = np.polyval(plv, logc)
    pl.xlabel('$\log(B-V)$')
    pl.ylabel('$\log(T_{eff})$')
#     pl.plot(logc, plt, 'r-')
    pl.savefig('logt_vs_logc')
