#!/bin/bash
rm -r HR_DATA
mkdir HR_DATA
for Ui in {5..24}
do
    U=`echo "scale=1; $Ui/10" | bc`
    wdir="U=${U}"
    cp -f wannier90.win $wdir
    cd $wdir
    echo -e "\n start U=${U}"
    /home/soft/wannier90-3.1.0/wannier90.x wannier90 &
    pid=$!
    wait $pid
    mkdir ../HR_DATA/$wdir
    cp wannier90_hr.dat ../HR_DATA/$wdir/
    cd ..
    echo -e " finish U=${U} \n"
done

