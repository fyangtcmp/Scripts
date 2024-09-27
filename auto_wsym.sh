#!/bin/bash
## 默认情况下依次进行所有计算 仅支持vasp.5.4.4
n=16 # number of processes

## convert kpath format from vasp to wann
function kpath_format_v2w() {
    # 先删除KPOINTS前4行无关的内容
    # FS输入分隔符 OFS输出分隔符 默认都是空格
    # ORS结束符 默认为换行符
    sed 1,4d KPATH.in |
        awk 'BEGIN{FS=" ";OFS=" "} \
    {if (NR%3==1) {ORS=" ";print $4,$1,$2,$3;} \
    else if (NR%3==2) {ORS="\n";print $4,$1,$2,$3;}}' >KPATH_wann.in
}

# compare the original band structure and the symmetrized one
cp ../KPATH.in ./ || vaspkit -task 303 >>vaspkit.log
kpath_format_v2w

begin_proj=$(grep -n 'begin projections' wannier90.win)
end_proj=$(grep -n 'end projections' wannier90.win)
sed -n "${begin_proj%%":"*},${end_proj%%":"*}p" wannier90.win >wannsymm.in
{
    echo -e "DFTcode=QE \nSeedName='wannier90' \nUse_POSCAR='POSCAR'"
    grep spinors wannier90.win
    grep MAGMOM INCAR
    echo -e "\nbegin kpath"
    cat "KPATH_wann.in"
    echo "end kpath"
} >>wannsymm.in

mpirun -n "$n" wannsymm.x

echo "
    set encoding iso_8859_1
    set terminal png truecolor enhanced font ', 60' size 1920, 1680
    set output 'wband_ori_symmed.png'
    set key top box opaque
    set border lw 3
    set xlabel 'k'
    set ylabel 'E(k)'
    plot 'bands_ori.dat'    w l lw 3 title 'original', \
         'bands_symmed.dat' w l lw 3 title 'symmed'
    " >wannsymm.gnu
gnuplot wannsymm.gnu
