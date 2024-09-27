#!/bin/bash
## 默认情况下依次进行所有计算 仅支持vasp.5.4.4
n=16 # number of processes
redo=false
run_scf=true
run_band=true
run_wann=true
run_wsym=true

## options
parameters=$(getopt -o n: -l redo, -n "$0" -- "$@")
eval set -- "$parameters" # 将$parameters设置为位置参数
while true; do            # 循环解析实际上是选项参数的位置参数
    case "$1" in
    -n)
        if [[ $2 -gt 0 ]]; then
            n="$2"
            shift 2
        else
            echo "Error: -n option can only accept positive integers"
            exit
        fi
        ;;
    --redo)
        redo=true
        shift 1
        ;;
    --)
        shift 1
        break
        ;; # 开始解析非选项类型的参数，break后，它们都保留在$@中
    *)
        echo "Error: getopt wrong"
        exit
        ;;
    esac
done

## 在至少传入一个参数的情况下进入手动模式
if [[ $# -gt 0 ]]; then
    run_scf=false # 先将默认值都关闭
    run_band=false
    run_wann=false
    run_wsym=false
    for i in "$@"; do # 然后打开手动指定的计算项目
        case "$i" in
        "scf")
            run_scf=true
            ;;
        "band")
            run_band=true
            ;;
        "wann")
            run_wann=true
            ;;
        "wsym")
            run_wsym=true
            ;;
        *)
            echo "Error: $i unrecognized, must be in {scf, band, wann, wsym}"
            exit
            ;;
        esac
    done
fi

## debug infomations
# echo "task parameters:"
# echo "  redo  = $redo"
# echo "  run_scf  = $run_scf"
# echo "  run_band = $run_band"
# echo "  run_wann = $run_wann"
# echo "  run_wsym = $run_wsym"
# echo " "

## check the campatibility of the number of processes and the NCORE tag in INCAR file
function check_vasp_mpi() {
    tmp=$(grep NCORE INCAR)
    ncore=${tmp#=}
    mod=$((n % ncore)) # $/${} is unnecessary on arithmetic variables
    if [[ $mod -gt 0 ]]; then
        echo "Error: -n option is wrongly set, please check the NCORE tag in INCAR file"
        exit
    fi
}

## whether to redo calculations
function check_dir_status() {
    dirname="$1"
    if [[ -d "$dirname" ]]; then
        if $redo; then
            rm -r "$dirname"
        else
            return 1 # 1=false, 0=true
        fi
    fi
}

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

## generate a template of wannier90.win
function gen_win_template() {
    echo "Do not find wannier90.win file, we will generate a template."
    echo "Please modify it and redo the calculations. Now we will exit..."
    echo "
    num_wann     =
    num_bands    =
    exclude_bands=

    begin projections

    end projections

    dis_win_min  =
    dis_froz_min =
    dis_froz_max =
    dis_win_max  =

    iprint=2
    dis_num_iter=200
    num_print_cycles=200
    num_iter=0

    write_hr=.true.
    guiding_centres=.true.
    write_xyz=.true.
    translate_home_cell=.false.
    use_ws_distance=.false.
    " >wannier90.win_temp
    exit
}


## main
if $run_scf && check_dir_status scf; then
    check_vasp_mpi
    mkdir scf
    cd scf || exit
    cp ../INCAR ./ || exit
    cp ../POSCAR ./ || exit
    cp ../KPOINTS ./ || vaspkit -task 102 -kpr 0.04 >>vaspkit.log
    cp ../POTCAR ./ || vaspkit -task 103 >>vaspkit.log
    mpirun -n "$n" vasp_ncl >>log
    echo "scf calculation done"
    cd ..
fi

if $run_band && check_dir_status band; then
    check_vasp_mpi
    cp -r scf band
    cd band || exit 21
    echo 'ICHARG=11' >>INCAR
    cp ../KPATH.in ./ || vaspkit -task 303 >>vaspkit.log
    cp KPATH.in KPOINTS
    mpirun -n "$n" vasp_ncl >>log
    echo "band calculation done"
    cd ..
fi

if $run_wann && check_dir_status wann; then
    cp -r scf wann
    cp ./wannier90.win ./wann || gen_win_template
    cd wann || exit

    cp ../KPATH.in ./ || vaspkit -task 303 >>vaspkit.log
    kpath_format_v2w

    echo -e "ICHARG=11 \nISYM=-1 \nLWANNIER90=.TRUE." >>INCAR
    sed -i "/NCORE/ c\NCORE = 1" INCAR
    mpirun -n "$n" vasp_ncl >>log
    mpirun -n "$n" wannier90.x wannier90
    echo "vasp2wannier90 calculation done"
    cd ..
fi

if $run_wsym; then
    if $run_wann; then # 如果单独调用wsym 认为当前文件夹已经是'wann'
        cd wann || exit
    fi

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
    echo "wannsymm calculation done"

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

    if $run_wann; then
        cd ..
    fi
fi
