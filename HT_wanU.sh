#!/bin/bash
mkdir HR_DATA
for Ui in {5..24}
do
    U=`echo "scale=1; $Ui/10" | bc`
    wdir="U=${U}"
    mkdir $wdir
    cp POSCAR  $wdir
    cp KPOINTS $wdir
    cp POTCAR  $wdir
    cp INCAR   $wdir
    cp wannier90.win $wdir
    cd $wdir
    (echo "LDAUU= ${U} 0 0 0 0") >> INCAR
    echo -e "\n start U=${U}"
    mpirun -np 4 vasp_ncl_w3 &
    pid=$!
    wait $pid
    (echo "ICHARG=11";echo "LWANNIER90=.TRUE.";echo "NBANDS=108") >> INCAR 
    mpirun -np 4 vasp_ncl_w3 &
    pid=$!
    wait $pid
    /home/soft/wannier90-3.1.0/wannier90.x wannier90 &
    pid=$!
    wait $pid
    mkdir ../HR_DATA/$wdir
    cp wannier90_hr.dat ../HR_DATA/$wdir/
    cd ..
    echo -e " finish U=${U} \n"
done

