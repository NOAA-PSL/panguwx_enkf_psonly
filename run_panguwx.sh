#!/bin/sh
#SBATCH -q urgent
#SBATCH -t 01:00:00
#SBATCH -A gsd-fv3-dev
#SBATCH -N 20  
#SBATCH --ntasks-per-node=80
#SBATCH -p hercules
#SBATCH -J run_panguwx
#SBATCH -e run_panguwx.out
#SBATCH -o run_panguwx.out

#datapath=/work2/noaa/gsienkf/whitaker/panguwx_enkf_psonly
#analdate=2021083000
#analdatep1=2021083006
#datapath2=/work2/noaa/gsienkf/whitaker/panguwx_enkf_psonly/${analdate}
#datapathp1=/work2/noaa/gsienkf/whitaker/panguwx_enkf_psonly/${analdatep1}
#nanals=80
#scriptsdir=$PWD
#corespernode=$SLURM_CPUS_ON_NODE
#NODES=$SLURM_NNODES
#FHMIN=3
#FHMAX=9
#FHOUT=3

runspernode=`expr $nanals \/ $NODES`
coresperrun=`expr $corespernode \/ $runspernode`
export OMP_NUM_THREADS=$coresperrun

/bin/rm -f ${datapathp1}/sfg*mem* ${datapathp1}/sfg*ensmean
/bin/rm -f ${datapathp1}/bfg*mem* ${datapathp1}/bfg*ensmean

nanal=1
while [ $nanal -le $nanals ]; do
srun -N 1 -n 1 -c $coresperrun --ntasks-per-node=$runspernode --cpu-bind=cores /work/noaa/gsienkf/whitaker/miniconda3/bin/python ${scriptsdir}/run_panguwx2.py $datapath2 $datapathp1 $analdate $nanal &
nanal=$((nanal+1))
done
wait

nanal=1
anyfilemissing='no'
while [ $nanal -le $nanals ]; do
    export charnanal="mem`printf %03i $nanal`"
    fhr=$FHMIN
    outfiles=""
    while [ $fhr -le $FHMAX ]; do
       charhr="fhr`printf %02i $fhr`"
       outfiles="${outfiles} ${datapath}/${analdatep1}/sfg_${analdatep1}_${charhr}_${charnanal} ${datapath}/${analdatep1}/bfg_${analdatep1}_${charhr}_${charnanal}"
       fhr=$((fhr+FHOUT))
    done
    filemissing='no'
    for outfile in $outfiles; do
      ls -l $outfile
      if [ ! -s $outfile ]; then 
        echo "${outfile} is missing"
        filemissing='yes'
        anyfilemissing='yes'
      else
        echo "${outfile} is OK"
      fi
    done 
    nanal=$((nanal+1))
done

if [ $anyfilemissing == 'yes' ]; then
    echo "there are output files missing!"
    exit 1
else
    echo "all output files seem OK"
    date
    exit 0
fi
