gmt set FONT_ANNOT_PRIMARY   4p,Helvetica,black
gmt set FONT_ANNOT_SECONDARY 5p,Helvetica,black
gmt set FONT_LABEL           5p,Helvetica,black
gmt set FONT_TITLE           14p,Helvetica,black

REGION=$1
LIGHT=85

# 网格文件准备
gmt makecpt -Cpolar_bluegrayred -T-0.03/0.03 >ttt.cpt
gmt grdcut landform_china.grd -GEQ_Location.grd -R$REGION
gmt grdgradient EQ_Location.grd -A$LIGHT -GEQ_Location_relief.grd -Ne0.5 -V

