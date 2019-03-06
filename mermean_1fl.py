""" Quick'n'dirty script to calculate ymean of Channel experiments."""


from netCDF4 import Dataset
import numpy as np
import os

nh = 3

if __name__ == '__main__': 
    
    #define staggered,unstaggered and 2D vars    
    ustagvars = ['U','T','P','QV','QC','QI','QR','QS','QG']
    stagvars = ['HHL','W','EFLUX','HFLUX']
    D2vars = ['CAPE_ML','CIN_ML','LCL_ML','HPBL','TOT_PREC','CAPE_MU','CIN_MU','CAPE_CON','TQC']
    Ztypelist = {'ustag': ustagvars,'stag':stagvars,'2D':D2vars}
    
    # define dimensions for the grid variable types
    dimlist = {
            'ustag': ('t','Z','X'),
            'stag':('t','Z1','X'),
            '2D': ('t','X')
            }

    # identify COSMO output data
    BASE = '/scratch/snx3000/adeli/project_C/'
    G7W0 = '1024x128_7Kkm_nowind_1km'
    G7W05 = '1024x128_7Kkm_wind05_new_1km'
    G7W1 = '1024x128_7Kkm_wind_1km'
    G7W2 = '1024x128_7Kkm_wind2_new_1km'
    
    G6W0 = '1024x128_6Kkm_nowind_1km'
    G6W05 = '1024x128_6Kkm_wind05_new_1km'
    G6W1 = '1024x128_6Kkm_wind_1km'

    G6W1_T285 = '1024x128_6Kkm_wind_T285_1km'
    G6W1_T290 = '1024x128_6Kkm_wind_T290_1km'
    G6W1_T300 = '1024x128_6Kkm_wind_T300_1km'


    G7W1_T285 = '1024x128_7Kkm_wind_T285_1km'
    G7W1_T290 = '1024x128_7Kkm_wind_T290_1km'
    G7W1_T300 = '1024x128_7Kkm_wind_T300_1km'




    G7U1 = '1024x128_7Kkm_U1_1km'
    G7U5 = '1024x128_7Kkm_U5_1km'
    G7U10 = '1024x128_7Kkm_U10_1km'


    WEXPs = [G7W0,G7W05,G7W1,G7W2,G6W0,G6W05,G6W1,G7U1,G7U5,G7U10]
    #WEXPs = [G6W0,G6W05,G6W1]
    WEXPs = [G7U1,G7U5,G7U10]
    WEXPs = [G6W1_T285,G6W1_T290,G6W1_T300,G7W1_T285,G7W1_T290,G7W1_T300]
    
    OEXPs = ['h0a0_2D','h1000a20_2D'] 
    SMEXPs = ['40_homo','60_homo','80_homo']
    WEXPs = [G7W1_T285,G7W1_T290,G7W1_T300]
  



    for WEXP in WEXPs:
        for OEXP in OEXPs:
            for SMEXP in SMEXPs:

                if 1: # for texperiments:
                    texp = WEXP[19:23]
                    print WEXP
                    SMEXP = SMEXP+'_'+texp

                    print SMEXP
                    
                seedls=filter(lambda x: x.startswith('seed'),os.listdir(BASE+WEXP+'/rawfiles/'+OEXP+'/'+SMEXP+'/'))
                #print WEXP,OEXP,SMEXP
                print seedls
                for seedn in seedls[:1]:
                    SRCPATH = BASE+WEXP+'/rawfiles/'+OEXP+'/'+SMEXP+'/'+seedn+'/output/'
                    TARPATH = BASE+WEXP+'/postprocessing/composites/ALLVAR_3D/'+OEXP+'/'+SMEXP+'/'
                    datalist = filter(lambda x: x.startswith('lfff'),os.listdir(SRCPATH))
                    datalist.sort() # sort by time
                  

                    # too little data?
                    if len(datalist)!=241:
                        continue
                     
                    # create and prepare new data set
                    newdatan = seedn+'ymean.nc'
                    try:
                        print WEXP, OEXP,SMEXP  
                        newdata = Dataset(TARPATH+newdatan,'w')
                       
                    except IOError:
                        print TARPATH
                        print "Not exist"
                        continue

                    # copy dimensions
                    newdata.createDimension('t')
                    newdata.createDimension('X',1024)
                    newdata.createDimension('Z',50) # unstaggered grid
                    newdata.createDimension('Z1',51) # staggered grid
                    i = 0
                    for datan in datalist[:]:
                        data = Dataset(SRCPATH+datan)
                        print i 
                        # iterate over Ztypes: 
                        for varzt in Ztypelist:
                            dims = dimlist[varzt]
                            for varn in Ztypelist[varzt]:
                                # print varn,varzt,i

                                # UGLY selection of grid extraction
                                if varzt=='2D':
                                    vardata = data.variables[varn][:,nh:-nh,nh:-nh]
                                    yaxidx = 1
                                else:
                                    vardata = data.variables[varn][:,:,nh:-nh,nh:-nh]
                                    yaxidx = 2

                                # Create Variable at first time only
                                if i==0:
                                    varz = newdata.createVariable(varn,float,dims)
                                else:
                                    varz = newdata.variables[varn]

                                # Calculate ymean and save
                                varz[i,:] = np.mean(vardata[:],axis=yaxidx)
                        data.close()
                        # increment output time step        
                        i+=1
                        # quick check for debugging
                        if i==242:
                            break
                    newdata.close()



