#/bin/bash

# Define paths

HYMET=/net/o3/hymet/adeli/
SCRATCH=/scratch/snx3000/adeli/

BASE=$SCRATCH


PROJ=$BASE/project_B/512x512_7Kkmnowind_1km/


SRC=$PROJ/rawfiles/
TAR=$PROJ/postprocessing/composites/

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
	for outfl in lfff0[0-4]*
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
		rm TP*
		
		
		#mv timeseries_TP.nc $tarpath/$mem"_"timeseries_TP.nc



		mv timeseries_TP.nc $mem"_"timeseries_TP.nc
		
		

		#calculate the daysum
		cdo daysum $mem"_"timeseries_TP.nc $mem"_"daysum_TPt2.nc
		#correct for half-hourly output period
		cdo divc,2 $mem"_"daysum_TPt2.nc $mem"_"daysum_TP.nc
		
		rm $mem"_"daysum_TPt2.nc
		

		tarpath=$TAR/$oro/$sm/
		mv * $tarpath
		#echo "clean up"		
		#rm -r ../temp
		#echo $tarpath
		#cd $tarpath



}


set=3

if [ $set -eq 1 ]
	then
	oros='500m_x20y10 500m_x10y20'
	sms='40_20 40_60 40_homo'
fi

if [ $set -eq 2 ]
	then
	oros='500m_x20y20'
	sms='40_20 40_60'
fi

if [ $set -eq 3 ]
	then
	oros='500m_x20y10 500m_x20y20'
	sms='40_20 40_60'
fi

oros='500m_x20y10'
sms='40_homo'



for oro in $oros
do
	for sm in $sms
	do
		experimentpath=$SRC/$oro/$sm/
		seeds=$experimentpath
		#iterate over ensemble members
		echo $experimentpath
		cd $experimentpath
		for mem in seed*
		do
			path=$experimentpath$mem/output/
			cd $path			
			echo "sourcepath is"
			echo $path
			postproc $oro $sm $mem $path 
		done

		tarpath=$TAR/$oro/$sm/
		cd $tarpath
		cdo ensmean seed*daysum_TP.nc ensmean.nc
	done
done
