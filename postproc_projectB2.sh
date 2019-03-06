#/bin/bash

# Define paths

HYMET=/net/o3/hymet/adeli/
# defined in .bashrc SCRATCH=/scratch/snx3000/adeli/

BASE=$SCRATCH

PROJ=$BASE/project_B2/512x512_7KkmU5_1km/
PROJ=$1
SRC=$PROJ/rawfiles/
TAR=$PROJ/postprocessing/composites/TOT_PREC/

# define postprocessing function




postproc () {
	# enters a COSMO output folder ~/output/ with lfff00 format
	# extracts TOT_PREC into single netcdf file
	# merges time
	# moves to postproc folder

	oro=$1
	sm=$2
	mem=$3
	if [ -d temp ]; then rm -r temp; fi
	mkdir temp
	# extract the relevant variable TOT_PREC
	for outfl in lfff0*
	do
        	echo $outfl

		echo $oro/$sm/$mem 
		#extract variables
		echo "extract TOT_PREC"
		ncks -v TOT_PREC $outfl temp/TP_$outfl
		#merge time slices into a signle file
	done	
		cd temp	
		echo "merge"
		cdo mergetime TP_lfff0[!5]* timeseries_TP.nc
		#remove time slices
		tarpath=$TAR/$oro/$sm/

		mv timeseries_TP.nc $tarpath/$mem"_"timeseries_TP.nc

        
		echo "clean up"		
		#rm -r ../temp

		cd $tarpath
		#mv timeseries_TP.nc $mem"_"timeseries_TP.nc
		
		echo $tarpath

		#calculate the daysum
		cdo daysum $mem"_"timeseries_TP.nc $mem"_"daysum_TPt2.nc
		#correct for half-hourly output period
		cdo divc,2 $mem"_"daysum_TPt2.nc $mem"_"daysum_TP.nc
		rm $mem"_"daysum_TPt2.nc

		#NOT NEEDEDcdo timmean $mem"_"daysum_TP.nc $mem"_"daysumdaymean_TP.nc

}

sms='60_homo' 

oros='h1000a14 h2000a14 h3000a14 h4000a14'

#oros='h250a14 h500a14 h750a14 h1000a14 h1500a14'

for oro in $oros
do
	for sm in $sms
	do
		experimentpath=$SRC/$oro/$sm/
		seeds=$experimentpath
		#iterate over ensemble members
		echo $experimentpath
		cd $seeds
		for mem in *
		do
			path=$experimentpath$mem/output/
			cd $path			
			echo "sourcepath is"
			echo $path
			postproc $oro $sm $mem $path
			
		done

		tarpath=$TAR/$oro/$sm/
		cd $tarpath
		cdo ensmean seed*daysum_TP.nc ensmean2.nc


	done
done
