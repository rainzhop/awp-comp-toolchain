# 地震标识
EQ_ID = '201906171455A'
PIC_TITLE = '2014长宁M5.8地震模拟'

# 震源
# 震中 经度(度)、纬度(度)、深度(km)
HypocenterLong = 104.95
HypocenterLati = 28.38
HypocenterDepth = 12
# 震级 Mw
M0 = 4.89e+24 *pow(10,25-7)
# 震源断层面 走向 71，倾角 81，滑动角 175
strike = 117
dip = 87
rake = -2
# 
Mrr =  3.140*pow(10,25-7)
Mtt =  2.350*pow(10,25-7)
Mpp = -5.490*pow(10,25-7)
Mrt = -0.174*pow(10,25-7)
Mrp =  0.532*pow(10,25-7)
Mtp =  2.900*pow(10,25-7)

# crust1.0提取
# 划定提取区域（左上角及右下角坐标）
# 此处划定了一个200km*200km的区域
# todo 此划定区域与格点尺寸和格点数有关，后续考虑改为自动划定范围
lat1 = 29.23
lon1 = 103.51
lat2 = 27.43
lon2 = 105.56
#lat1 = HypocenterLati + 2 # 29.1
#lon1 = HypocenterLong - 2 # 101.3
#lat2 = HypocenterLati - 2 # 25.1
#lon2 = HypocenterLong + 2 # 105.3
# 经纬+深度方向的格点数
dh = 400 # 格点尺寸0.4km
xlati = 500
ylong = 500
zdepth = 100

Source_TMAX = 40 # Second

# 可视化的输入
start_step = 0
stop_step = 2000
write_step = 1000
n_ti_skp = 1
dt = 0.02 # second
xt = xlati
yt = ylong

if __name__ == "__main__":
    env = "eq_id=%s X=%d Y=%d Z=%d DT=%f DH=%f TMAX=%f\n" % (EQ_ID, xlati, ylong, zdepth, dt, dh, Source_TMAX)
    print(env)
