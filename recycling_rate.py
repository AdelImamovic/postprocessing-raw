#!/usr/bin/python
# -*- coding: UTF-8  -*-
import numpy as np
from netCDF4 import *
import sys,os


try:
  ifilename1h_mean = sys.argv[1]  #Mean water fluxes
  twater_begin = sys.argv[2]
  twater_end   = sys.argv[3]
except:
  print('Problems with Input')
  sys.exit(2)

ncfile1h_mean = Dataset(ifilename1h_mean,mode='r')   #Houerly Means of Water Fluxex, P, latent heatflux
ncfile_twater_begin = Dataset(twater_begin,mode='r') #Total vertically integrated water at beginning
ncfile_twater_end = Dataset(twater_end,mode='r')     #otal vertically integrated water at end

#Region in case not square, else adapt
lonW=196
lonE=292
latS=185
latN=226

#Constants
lh_v=2.501*10**6 #Specific latenent heat of vaporization [ J / kg ] 
r_earth=6371000. #Radius of the Earth [m]

#Distances of Edges, + 1 because staggered
#Je nachdem noch * r_earth * np.radians(dx)
dlon =  lonE - lonW + 1 
dlat =  latN - latS + 1

#Read Data
#--------

#Die Water fluxes sollten an den gestaggerten grid points berechnet werden bei dir ev. egal ? 
TwatfluxUa = ncfile1h_mean.variables["TWATFLXU_A"][0, latS:latN, lonW:lonE] # kg / m / s
TwatfluxVa = ncfile1h_mean.variables["TWATFLXV_A"][0, latS:latN, lonW:lonE] # kg / m / s

#Water Storage
dW  = ncfile_twater_end.variables["TWATER"][0, latS:latN, lonW:lonE] - ncfile_twater_begin.variables["TWATER"][0, latS:latN, lonW:lonE] #kg / m2 -> kg / m / s 
dW = dW.mean() / (3600.* 24. * 92.) #kg / m2 / season(JJA) -> kg / m / s 

#Latent heat Flux
lhfl=ncfile1h_mean.variables["ALHFL_S"][0, latS:latN, lonW:lonE]
ET=lhfl.mean() / lh_v  * (-1) # Latent Heatflux [W/m2] -> Evapotranspiration [ kg / s / m2 ] | (-1) because Flux is defined the other way, maybe change?

#Precipitation
P=ncfile1h_mean.variables["TOT_PREC"][0, latS:latN, lonW:lonE] #+ ncfile1h_mean.variables["TOT_SNOW"][0, latS:latN, lonW:lonE]
P=P.mean() / 3600. # [kg / m / h ] -> [kg / m2 / s] 


#Compute divergence using Gauss'Theorem
#------------------------------------------------

# Fluxes at boundaries
WFlx=TwatfluxUa[ : , 0 ]
EFlx=TwatfluxUa[ : , -1]
SFlx=TwatfluxVa[ 0 , : ]
NFlx=TwatfluxVa[ -1, : ]

# Surface Integral
IN  =   np.maximum(0., WFlx).mean() / dlat - np.minimum(0., EFlx).mean() / dlat + np.maximum(0., SFlx).mean() / dlon - np.minimum(0., NFlx).mean() / dlon
OUT = - np.minimum(0., WFlx).mean() / dlat + np.maximum(0., EFlx).mean() / dlat - np.minimum(0., SFlx).mean() / dlon + np.maximum(0., NFlx).mean() / dlon 

#Split residual equally onto IN and OUT
epsilon  = ET - P + IN - OUT - dW
IN_corr  = IN - epsilon / 2.
OUT_corr = OUT - epsilon / 2.

print('dW  =', "{:.2e}".format(dW))
print('ET  =',"{:.2e}".format(ET))
print('P   =',"{:.2e}".format(P))
print('IN  =',"{:.2e}".format(IN))
print('OUT =',"{:.2e}".format(OUT))
print('INcorr  =', "{:.2e}".format(IN_corr))
print('OUTcorr =',"{:.2e}".format(OUT_corr))

print('epsilon = ', "{:.2e}".format(epsilon))

R= ET / (IN_corr + ET) * 100 #convert to %
print('R = ', R, '%') 

