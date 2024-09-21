#!/bin/bash
# adjust the overall scale of POSCAR
# to give the relations between the unit cell volumes and the total energies.
scale=(0.9984 0.999 1.0 1.001 1.0016)
np=9

for i in ${scale[@]}
do
    mkdir ./$i
    cp ./POSCAR  ./$i
    cp ./INCAR   ./$i
    cp ./KPOINTS ./$i
    cp ./POTCAR  ./$i

    cd ./$i
    sed -i '2c '$i'' POSCAR
    mpirun -np $np vasp_ncl > log.vasp.out
    en=$(grep "free  energy" OUTCAR)
    en=(${en// / }) 
    echo $i ${en[4]}
    cd ..
done

