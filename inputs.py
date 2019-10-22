# 地震标识
EQ_ID = 'ludian'

# 震源
# 震中 经度(度)、纬度(度)、深度(km)
HypocenterLong = 103.3
HypocenterLati = 27.1
HypocenterDepth = 12
# 震级 Mw
M0 = 2.12e+25 *pow(10,25-7)
# 震源断层面 走向 71，倾角 81，滑动角 175
strike = 71
dip = 81
rake = -175
# 
Mrr = -0.020*pow(10,25-7)
Mtt =  1.310*pow(10,25-7)
Mpp = -1.290*pow(10,25-7)
Mrt = -0.055*pow(10,25-7)
Mrp = -0.355*pow(10,25-7)
Mtp = -1.640*pow(10,25-7)

# crust1.0提取
# 划定提取区域（左上角及右下角坐标）
#lat1 = 28.231089
#lon1 = 102.519264
#lat2 = 26.43236
#lon2 = 104.5609
lat1 = HypocenterLati + 2
lon1 = HypocenterLong - 2
lat2 = HypocenterLati - 2
lon2 = HypocenterLong + 2
# 经纬+深度方向的格点数
xlati = 500
ylong = 500
zdepth = 100

# 可视化的输入
input_filename_prefix = 'SX000'
input_filename_suffix = ['1000', '2000']
start_step = 100
stop_step = 2000
write_step = 1000
n_ti_skp = 1
dt = 0.02 # second
xt = xlati
yt = ylong

if __name__ == "__main__":
    env = "eq_id=%s X=%d Y=%d Z=%d DT=%f \n" % (EQ_ID, xlati, ylong, zdepth, dt)
    print(env)
