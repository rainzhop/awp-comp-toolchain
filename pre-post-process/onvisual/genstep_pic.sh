#./genstep_pic.sh 
#     "./any-folder/awpsfc00502.txt(path-of-src-filename)" 
#     "00502(png-filename)" 
#     0.0Sec 
#     102.5/104.6/26.4/28.25
#     "(png-folder)"

SRC_DATA_FILE=$1
PSFILE="$9/v$2.ps"
echo $PSFILE

INFO_TEXT=$3 # 0.2Sec 传播时刻
REGION=$4
EPIC_CENTER=$5 # 震中位置
TOWNS_FILE=$6
PIC_TITLE=$7

COOR_FILE=$8
DST_FOLDER=$9

#REGION=102.5/104.6/26.4/28.25
#TOWNS_FILE="./towns"
#TOWNS_LONLAT_LIST="103.7250 27.3406 昭通\n103.4258 27.2057 鲁甸"
#TOWNS_NAME_LIST="103.7250 27.3406 昭通\n103.4258 27.2057 鲁甸"
#EPIC_CENTER="103.3 27.1 1000"
#IC_TITLE="模拟"
#PIC_TITLE="2008鲁甸M6.5地震模拟"
#COOR_FILE="../coor.txt"
#DST_FOLDER="../conpic_fix"

LIGHT=85
PROJ=M15
VIEW=160/30

# Velocity绘制
gawk 'NR==FNR{a[FNR]=$1}NR>FNR{print $1,$2, a[FNR]}' $SRC_DATA_FILE $COOR_FILE > f.txt
gmt xyz2grd f.txt -I0.005 -r -R$REGION -Gsfcgrd.grd

gmt grdview EQ_Location.grd -R$REGION -Gsfcgrd.grd -J$PROJ -Jz0.0003 -Cttt.cpt -IEQ_Location_relief.grd -p$VIEW -Bf1a1g1/f1a1g1/f2000a5000wSnEZ -Qi300 -K -V  > $PSFILE

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


# 标题添加
echo 4 4 $PIC_TITLE | gmt pstext -R0/10/0/10 -Jx1i -F+f15p,41 -K -O >>  $PSFILE
echo 1.5 0.4 $INFO_TEXT | gmt pstext -R0/10/0/10 -Jx1i -F+f8p -K -O >>  $PSFILE 
echo 1.5 0.2 中国地震局第二监测中心 | gmt pstext -R0/10/0/10 -Jx1i -F+f10p,41  -O >>  $PSFILE

# 格式转换
gmt psconvert -D$DST_FOLDER -A0.5c -E180 -P -TG $PSFILE

# 现场清理
rm $PSFILE
rm f.txt sfcgrd.grd gmt.history
