# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 14:44:17 2016

@author: adeli
"""
import sys
sys.path.append('/home/adeli/scripts/')
import os
import numpy as np
import re
   
    
def circsym_mean_vec(field):
    """ Circular mean of field field(z',x,y) -> f(z,r)
    
    Paramters
    ----
        fxyz:
        c:
    Returns:
    ----
        frz
    TODO:
    ----
        translate grid so mountain top is staggered - center at 149.5?
    
    """
    U,V,W = field
    nz,nx,ny=U.shape
    c = nx/2.+0.5
    
    Urz=np.zeros((nz,nx/2))
    Wrz=np.copy(Urz)
    x = np.arange(nx)-c
    y = np.arange(ny)-c

    X,Y=np.meshgrid(x,y)
    R=np.sqrt(X**2+Y**2)
    PHI=np.arctan(Y/X)
    Uradial=np.zeros(U.shape)

    for k in range(nz):
        Uradial[k,:]=U[k,:]*np.cos(PHI)+V[k,:]*np.sin(PHI)
        Uradial[k,:,:nx/2]*=-1. #circular symmetry
    
    if 0: # debug
        lev=38
        cf=plt.contourf(Uradial[lev,:],cmap='coolwarm')
        cbar=plt.colorbar(cf)
        assert 0
        
    for k in range(nz):
        levelu = Uradial[k,:,:]
        levelw = W[k,:,:]
        for r in range(nx/2):
                Urz[k,r] = np.mean(levelu[np.logical_and(R>=r*1.,R<r+1.)])
                Wrz[k,r] = np.mean(levelw[np.logical_and(R>=r*1.,R<r+1.)])
                
    return Urz,Wrz
    
    
def circsym_mean_scal(field):
    """ cylindiric mean of a scalar field"""
    nz,nx,ny = field.shape
    frz = np.zeros((nz,nx/2))
    c = nx/2.+0.5
    x = np.arange(nx)-c
    y = np.arange(ny)-c
    X,Y=np.meshgrid(x,y)
    R=np.sqrt(X**2+Y**2)
    for k in range(nz):
        level = field[k,:,:]
        for r in range(nx/2):
            frz[k,r] = np.mean(level[np.logical_and(R>=r*1.,R<r+1.)])
    return frz
    
def circsym_mean_2D(field):
    """ cylindiric mean of a scalar field"""
    nx,ny = field.shape
    frz = np.zeros(nx/2)
    c = nx/2+0.5
    x = np.arange(nx)-c
    y = np.arange(ny)-c
    X,Y=np.meshgrid(x,y)
    R=np.sqrt(X**2+Y**2)
    for r in range(nx/2):
            frz[r] = np.mean(field[np.logical_and(R>=r*1.,R<r+1.)])
    return frz
    
    
    

