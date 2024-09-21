#!/bin/bash
function scan() {
    local cur_dir work_dir
    local incar en
    work_dir=$1
    cd ${work_dir}
    cur_dir=$(pwd)
    if test -f "OUTCAR"
        then
            incar=${cur_dir##*$start_dir}
            echo -e "$incar\c"
            echo -e ":\c"
            en=$(grep "free  energy" OUTCAR)
            en=(${en// / })
            echo ${en[4]}
    fi

    for dirlist in $(ls ${cur_dir})
    do
        if test -d ${dirlist}
        then
            cd ${dirlist}
            scan ${cur_dir}/${dirlist}
            cd ..
        fi
    done
}

start_dir=$1
scan $start_dir


