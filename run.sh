#!/bin/bash

env=`python3 inputs.py`
eval $env # eq_id X Y Z DT
mkdir ./results
mkdir ./results/${eq_id}
mkdir ./results/${eq_id}/mesh_source
mkdir ./results/${eq_id}/output_ckp
mkdir ./results/${eq_id}/output_sfc
mkdir ./results/${eq_id}/output_pics
mkdir ./results/${eq_id}/tmp
mkdir ./results/${eq_id}/tmp/eachstep_x_data_fix
mkdir ./results/${eq_id}/tmp/eachstep_y_data_fix
mkdir ./results/${eq_id}/tmp/eachstep_z_data_fix
mkdir ./results/${eq_id}/tmp/conpic_fix

cp inputs.py ./pre-post-process/inputs.py
cd pre-post-process
python3 oncrust1.py
python3 onsource.py
cd ..

sleep 1
echo STARTING `date`
mpirun -n 1 ./awp-odc-os/src/pmcl3d                             \
 -X $X -Y $Y -Z $Z -x 1 -y 1                                    \
 --TMAX $TMAX --DH $DH --DT $DT                                \
 --NSRC 1 --NST 1000                                            \
 --IFAULT 1 --MEDIASTART 2                                      \
 --READ_STEP 101 --WRITE_STEP 1000                              \
 --NSKPX 1 --NSKPY 1 --NTISKP 1                                 \
 -c results/${eq_id}/output_ckp/ckp                             \
 -o results/${eq_id}/output_sfc                                 \
 --INSRC results/${eq_id}/mesh_source/source                    \
 --INVEL results/${eq_id}/mesh_source/mesh
echo STARTING `date`


echo "\n-----------------------------------------------------"
sleep 1
head ./results/${eq_id}/output_ckp/ckp -n 20
echo "-----------------------------------------------------\n"

sleep 1
cd pre-post-process

# gen pics containing velocity without land relief
# python3 onimshow.py

python3 onvisual.py

rm inputs.py
cd ..

FPS=`bc <<< "1/$DT"`
ffmpeg -threads 3 -r $FPS -i ./results/${eq_id}/tmp/conpic_fix/v%5d.png -pix_fmt yuv420p -vcodec libx264  -vf scale=1280:-2 ./results/${eq_id}/${eq_id}.mp4
