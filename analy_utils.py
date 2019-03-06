# -*- coding: utf-8 -*-
from netCDF4 import Dataset
import numpy as np
import os
halo=3

vcoordvec = [22000.0, 21000.0, 20028.6, 19085.4, 18170.0, 17282.1, 16421.4, 15587.5,
        14780.0, 13998.6, 13242.9, 12512.5, 11807.1, 11126.4, 10470.0,  9837.5,
        9228.6,  8642.9,  8080.0,  7539.6,  7021.4,  6525.0,  6050.0,  5596.1,
        5162.9,  4750.0,  4357.1,  3983.9,  3630.0,  3295.0,  2978.6,  2680.4,
        2400.0,  2137.1,  1891.4,  1662.5,  1450.0,  1253.6,  1072.9,  907.5,
        757.1,   621.4,   500.0,   392.5,   298.6,   217.9,   150.0,   94.6,
        51.4,    20.0,     0.0]
""" Routine to remove axes: left and top.
    http://matplotlib.org/examples/pylab_examples/spine_placement_demo.html  
"""



def get_vertcoord(hsurf,nz=51):
    "pass surface height, return vertical coordinates"
    ivctype = 2
    vcflat = 6000.
    zz_top = 9999.

    _ks = np.arange(0,nz)
    zak = _ks * 0.
    zbk = _ks * 0.


    kflat = 0
    # Inverse coordinate transfromation to obtain zak and zbk
    for k in _ks:
        if vcoordvec[k] >= vcflat:
            zak[k] = vcoordvec[k]
            zbk[k] = 0.
            kflat = k
        else:
            zak[k] = vcoordvec[k]
            zbk[k] = (vcflat -vcoordvec[k])/vcflat

    # Calcualte hsurf
    vcoordath = zak+zbk*hsurf
    return vcoordath


def HHL_creator(Hm=250.,nx=300,ny=300,nz=51,a=20.,ay=False,surftopo='cos2'):
    """ Port of Fortran code in vgrid_refatm_utils.f90
    HHL gives AGL levels of every grid point.

    Namelist parameters:
    ----
    ivctype = 2,
    zspacing_type = 'vcoordvec', ! sub-type of coordinate spec.
    exp_galchen = 2.6,        ! exponent in the Gal-Chen formula
    vcflat = 6000.0,          ! height, above which coordinate levels become flat [m]
    zz_top = 9999.0,          ! height of model top, if it has to be specified explicitly [m]
    vcoordvec =
    22000.0, 21000.0, 20028.6, 19085.4, 18170.0, 17282.1, 16421.4, 15587.5,
    14780.0, 13998.6, 13242.9, 12512.5, 11807.1, 11126.4, 10470.0,  9837.5,
     9228.6,  8642.9,  8080.0,  7539.6,  7021.4,  6525.0,  6050.0,  5596.1,
     5162.9,  4750.0,  4357.1,  3983.9,  3630.0,  3295.0,  2978.6,  2680.4,
     2400.0,  2137.1,  1891.4,  1662.5,  1450.0,  1253.6,  1072.9,  907.5,
      757.1,   621.4,   500.0,   392.5,   298.6,   217.9,   150.0,   94.6,
       51.4,    20.0,     0.0]
    ----
    Original code:    
    CASE ( 2, 3 )
    ! Height-based hybrid vertical coordinate on input
    ! Vertical grid specified in terms of hhl
    ! here hhl depends only on the zak, zbk and vcflat

    IF     (vc_type%ivctype == 2) THEN
      ! "standard" coordinate with zak, zbk

      ! Calculate the inverse coordinate transformation, i.e. the zak's and zbk's
      vc_type%kflat = 0
      DO k = 1, ke+1
        IF( vc_type%vert_coord(k) >= vc_type%vcflat ) THEN
          zak(k) = vc_type%vert_coord(k)
          zbk(k) = 0.0_ireals
          vc_type%kflat = k
        ELSE
          zak(k) = vc_type%vert_coord(k)
          zbk(k) = (vc_type%vcflat - vc_type%vert_coord(k))/ vc_type%vcflat
        ENDIF
      ENDDO

      IF (lnew_hhl) THEN
        ! Compute the height of the model half-levels
        hhl(:,:,ke+1) = hsurf(:,:) 
        DO  k = 1, ke
          hhl(:,:,k) = zak(k) + zbk(k)*hhl(:,:,ke+1)
        ENDDO
      ENDIF
    ----      
    Returns:
        HHL field as in COSMO (z',rlon,rlat)
    """
    
    # Namelist constants    
    ivctype = 2
    vcflat = 6000.
    zz_top = 9999.

  
    x = np.arange(1,nx+1)
    y = np.arange(1,ny+1)
    _ks = np.arange(0,nz)
    zak = _ks * 0.
    zbk = _ks * 0.

    HHL = np.zeros((nz,nx,ny))
    
    X,Y = np.meshgrid(x,y)
    c = nx/2.+0.5
    R2=(X-c)**2+(Y-c)**2
    hsurf=np.zeros(R2.shape)
    
    
    if surftopo=='gauss':
        #hsurf = Hm*(2**(-(R2)/(a**2)))  #symmetric Gaussian
        if not ay: ay = a
        hsurf = Hm*(2.**(-((X-c)/a)**2-((Y-c)/ay)**2))
    if surftopo=='bell':
        hsurf = Hm/(1+(R2)/(a**2)) 
    if surftopo=='bell1.5':
        hsurf = Hm/(1+(R2)/(a**2))**1.5     
    if surftopo=='cos2':
        hsurf = Hm*np.cos(np.pi/4.*(R2)/(a**2))**2
        hsurf[R2>2*a**2] = 0.
        
    #hsurf[np.where(hsurf < 0.001)] = 0.
    HHL[-1,:,:] = hsurf    

    kflat = 0
    # Inverse coordinate transfromation to obtain zak and zbk
    for k in _ks:
        if vcoordvec[k] >= vcflat:
            zak[k] = vcoordvec[k]
            zbk[k] = 0.
            kflat = k
        else:
            zak[k] = vcoordvec[k]
            zbk[k] = (vcflat -vcoordvec[k])/vcflat

    # Calcualte HHL
    for k in range(nz-1):
        HHL[k,:,:] = zak[k]+zbk[k]*HHL[-1,:,:]

    print kflat
    return HHL  
    


   
    

