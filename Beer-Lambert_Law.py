import numpy as np
import matplotlib.pyplot as plt
import scipy as sci

#The molar absorptivity (molabs) of common shielding materials. Calculated from mass attenuation * molar mass
#Check the units. The code can't take any values above 0.05
molabs_Pb = 5.549 * 207
dens_Pb = 11.348
molabs_W = 1.581 * 183
dens_W = 19.254
molabs_Fe = 0.1964 * 56
dens_Fe = 7.874


def absorption(conc,path,molabs):
    return conc * path * molabs

def intensity(conc,path,molabs,intensity_init):
    absorption_val = absorption(conc,path,molabs)
    return intensity_init / (10 ** absorption_val)

intensity_test = intensity(dens_Pb,5e-3,molabs_Pb,10e-15)
print(intensity_test)