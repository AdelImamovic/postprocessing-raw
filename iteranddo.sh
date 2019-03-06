#!/bin/bash
# simple script consists of two functions:
# iter and do
#
#
#
# iter changes dir to the leafs of a folder tree
#
#
#
# do applies a function to the data inside the leafs
#
#
#
#
#



# Define some paths


basepath=$SCRATCH/project_jesus/

#define node names to consider
exps='1024x1024_16km_dcparam_turlen400
1024x1024_16km_dcparam_turlen400_slip
1024x1024_16km_turlen400
1024x1024_16km_turlen400_slip'
oros='h1000a40'
sms='40_homo 60_homo'





postproc() {
    # cdo cmds
    outpath=$1
    pppath=$2

    echo "working on..."
    echo $outpath
    
    
    cdo cat $outpath/lfff0[0-4]* $outpath/output.nc


    if [ ! -d $pppath ];then 
        mkdir -p $pppath
    fi
   
    mv $outpath/output.nc $pppath
    ls $pppath

}

#ram_turlen400


iter() {
    for exp in $exps
    do
        for oro in $oros
        do
            for sm in $sms
            do 
                rawpath=$basepath/$exp/rawfiles/$oro/$sm/               
                pppath=$basepath/$exp/postprocessing/composites/ALLVAR_3D/$oro/$sm/
                for seed in $rawpath/* 
                do
                        outpath=$seed/output
                        # check if sufficient files are there
                        n_out="$(ls $outpath | wc -l)"
                        
                        if [ $n_out -ne 241 ]
                        then
                            echo $n_out
                            echo "skipped"
                            echo $outpath 
                            continue
                        fi
                        
                        postproc $outpath $pppath & 
                done
            
            done
        done
    done
}

iter
