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
    BASE = '/scratch/snx1600/adeli/project_smpf/'
    G7U0 = '4096x256_7Kkm_U0_2km'
    G7U5 = '4096x256_7Kkm_U5_2km'
    G7U1 = '4096x256_7Kkm_U1_2km'
    G7U10 = '4096x256_7Kkm_U10_2km'
    G7U20 = '4096x256_7Kkm_U20_2km'

    ch_gauss = 'h1000a20_gauss'
    ch_bell = 'h1000a20_bell'


    WEXPs = [G7U0,G7U1,G7U5,G7U10]
    OEXPs = ['h1000a20_gauss']

    SMEXPs = ['60_30strip_strw128','60_30strip_strw256','60_30strip_strw64','60_60','60_90strip_strw128','60_90strip_strw256','60_90strip_strw64']

    SMEXPs = ['30_30h0a0','60_30h0a0_strip_strw128','60_30h0a0_strip_strw256','60_30h0a0_strip_strw64',
    '60_60h0a0','60_90h0a0_strip_strw128','60_90h0a0_strip_strw256','60_90h0a0_strip_strw64','90_90h0a0']

    SMEXPs = ['30_30h1000a20_gauss','60_60h1000a20_gauss','90_90h1000a20_gauss'] 
    
    for WEXP in WEXPs:
        for OEXP in OEXPs:
            for SMEXP in SMEXPs:
                
                seedn=filter(lambda x: x.startswith('seed'),os.listdir(BASE+WEXP+'/rawfiles/'+OEXP+'/'+SMEXP+'/'))[0]


                SRCPATH = BASE+WEXP+'/rawfiles/'+OEXP+'/'+SMEXP+'/'+seedn+'/output/'
                TARPATH = BASE+WEXP+'/postprocessing/composites/ALLVAR_3D/'+OEXP+'/'+SMEXP+'/'
                print SRCPATH
                print TARPATH
                datalist = filter(lambda x: x.startswith('lfff'),os.listdir(SRCPATH))
                datalist.sort() # sort by time



		# check if simulation produced all the necessary output
		# daint file system check
		if len(datalist)!=241:
			print "***********"
			print SRCPATH
			print "skipped"
			print "***********"
			continue

                 
                # create and prepare new data set
                newdatan = 'ymean.nc'
                try:
                    print os.listdir(SRCPATH)
                    print WEXP, OEXP,SMEXP  
                    newdata = Dataset(TARPATH+newdatan,'w')
                    
                except IOError:
                    print TARPATH
                    print "Not exist"
                    continue



                # copy dimensions
                newdata.createDimension('t')
                newdata.createDimension('X',2048)
                newdata.createDimension('Z',50) # unstaggered grid
                newdata.createDimension('Z1',51) # staggered grid
                
		# create rlon
                
                i = 0
                for datan in datalist[:]:
                    data = Dataset(SRCPATH+datan)
                  
                    # iterate over Ztypes: 
                    for varzt in Ztypelist:
                        dims = dimlist[varzt]
                        for varn in Ztypelist[varzt]:
                            print varn,varzt,i

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



