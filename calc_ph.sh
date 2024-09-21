#!/bin/bash
# calculate the phonon spectrum using VASP and phonopy
DIM="2 2 2"
np=9

phonopy -d --dim="$DIM"
for i in POSCAR-*
do
    nowdir=${i#*-}
    mkdir $nowdir
    cp $i $nowdir/POSCAR
    cp INCAR   $nowdir
    cp KPOINTS $nowdir
    cp POTCAR  $nowdir
    cd $nowdir
    echo " "
    pwd
    mpirun -np $np vasp_std > log.vasp.out # &
    # pid=$!
    # wait $pid
    cd ..
    echo "finish $i calcualtion"
done
phonopy -f 0*/vasprun.xml

