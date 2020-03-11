#! /bin/bash

PSFILE=./pgv_vxy.ps
SRC_DATA_FILE=$1
echo $PSFILE
REGION=$4
EPIC_CENTER=$5 # 震中位置
TOWNS_FILE=$6
COOR_FILE=$9
DST_FOLDER=$3


gmt makecpt -Cgrey -T-200/4000/500 >tt.cpt
gmt psbasemap -R$REGION -JM4i -B1WSen -P -K -X2i -Y3i >$PSFILE
gmt pscoast -J -R -Gc -K -O -V >>$PSFILE
gmt grdimage ../landform_china.grd -Ilandform_china_in.grd -Ctt.cpt   -E400 -J -R -K -O -P >>$PSFILE


# 震中位置绘制
gmt psxy -J -R -Sa0.2c -W1.5p,black,solid -Gyellow -p -K -O >> $PSFILE << EOF
$EPIC_CENTER
EOF

# 城市位置绘制
gmt psxy -J -R -St0.1c -W0.05p,black,solid -Gblack -p -K -O >> $PSFILE << EOF
`gawk '{print $1, $2}' $TOWNS_FILE`
EOF

# 城市名称添加
gmt pstext -J -R -F+f10p,41,black+jTL -D-0.1c/-0.0c -p -K -O >> $PSFILE << EOF
`gawk '{print $1, $2, $3}' $TOWNS_FILE`
EOF


gawk 'NR==FNR{a[FNR]=$1}NR>FNR{print $1,$2, a[FNR]}' $SRC_DATA_FILE $COOR_FILE >f.txt
gmt xyz2grd f.txt -I0.05 -R -Gsfcgrd.grd
echo 'xyz2grd done.'

gmt makecpt -Cpolar_pgv -T0/1.5 -Z >ttt.cpt
gmt grdimage sfcgrd.grd -Cpolar_pgv.cpt  -E400 -t40 -J -R -K -O -P >>$PSFILE
gmt psscale -Dx6.8c/0.5c+w2c/0.2c+mlu+h -Cttt.cpt -B0.3:Velocity:  -O >>$PSFILE
gmt psconvert -A -P -TG $PSFILE

# 现场清理
rm $PSFILE
rm f.txt sfcgrd.grd gmt.history
rm tt.cpt ttt.cpt
