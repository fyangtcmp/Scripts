#!/bin/bash
# calculate thermal properties with the quasi harmonic approximation 
# using VASP, phonopy and calc_ph.sh

# scale=(0.98 0.985 0.99 0.995 1 1.005 1.01 1.015 1.02)
scale=(1.00 1.01)

for i in ${scale[@]}
do
    mkdir ./$i
    cp ./POSCAR  ./$i
    cp ./INCAR   ./$i
    cp ./KPOINTS ./$i
    cp ./POTCAR  ./$i
    cp ./calc_ph.sh ./$i

    cd ./$i
    sed -i '2c '$i'' POSCAR
    bash ./calc_ph.sh
    cd ..
done

