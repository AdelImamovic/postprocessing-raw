#!/bin/bash
#
# Postprocessing script for project_A member ensembles
# Inherited from ensmean_time.sh
#
# Difference: not ensmean over days but members with different RNG seeds is given
#
# Given 
# 1.) path to a folder with COSMO output with format lfffddhhmmss.nc
# 2.) a variable of choice (default TOT_PREC)
# 3.) a day range ds and de
#
# for every output from a single day is put into a file $experiment_$variable_d$num.nc
#
# 


BASE=$SCRATCH

shopt -s extglob

proj=$1 #'/project_B2/512x512_7Kkmwind05_new_1km'
sms='60_homo'

# oros='h1000a5_x4_offset_10 h1000a7_x2_offset_10 h250a10_x4_offset_10 h500a10_x2_offset_10'

oros='h4000a14'

#dayrange of interest
ds=0
de=5



for oro in $oros
do
	:

	
	for sm in $sms
	do
		:
		exp='/'$oro'/'$sm
		srcPATH=$BASE$proj'/rawfiles'$exp
		outPATH=$BASE$proj'/postprocessing/composites/ALLVAR_3D/'$exp

		echo $outPATH
        
        for fl in $srcPATH'/'!(*TOT*); do
            continue		
            fl=${fl##*/}
		    echo $fl
		    i=$ds
		    
		    while [ $i -lt $de ]; do
			outvarname=$fl'_temp_d'$i'.nc'
			targetfile=$outPATH'/'$outvarname
			echo $outvarname    
			echo $srcPATH   
			echo $outPATH

			srcfiles=$srcPATH/$fl'/output/lfff0'$i'*'
			targetfile=$outPATH'/'$outvarname
			echo 'srcfiles '$srcfiles
			echo 'targetfile '$targetfile
			cdo mergetime $srcfiles $targetfile    
			let i=i+1
		    done
	    # evaluate only 1 ensemble member
           #break


    	done
	# evaluate only 1 ens member
        cdo ensmean $outPATH'/*temp*' $outPATH'/ensmean_day_3d_d'$ds'd'$de'.nc'
        echo $outPATH/*temp*
        rm $outPATH/*temp*
	done
done




