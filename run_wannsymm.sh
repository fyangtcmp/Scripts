#!/bin/bash
begin_proj=$(grep -n 'begin projections' wannier90.win)
end_proj=$(grep -n 'end projections' wannier90.win)
sed -n "${begin_proj%%":"*},${end_proj%%":"*}p" wannier90.win >wannsymm.in
{
    echo -e "DFTcode=QE \nSeedName='wannier90' \nUse_POSCAR='POSCAR'"
    grep spinors wannier90.win
    grep MAGMOM INCAR
} >>wannsymm.in
mpirun -n 16 wannsymm.x
