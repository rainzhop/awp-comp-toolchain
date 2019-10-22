from config import *
from inputs import *
import numpy as np
from scipy import interpolate
from scipy.interpolate import griddata
import struct


NO_LAYER = 9
NO_LON = 360
NO_LAT = 180


# 按坐标加载crust1.0数据
def load_crust1(NO_LAT, NO_LON, NO_LAYER, CRUST1_0_DIR = "./crust1.0/"):
    # 单位 bnds(km)
    data_vp = np.loadtxt(CRUST1_0_DIR + 'crust1.vp').reshape([NO_LAT, NO_LON, NO_LAYER])
    data_vs = np.loadtxt(CRUST1_0_DIR + 'crust1.vs').reshape([NO_LAT, NO_LON, NO_LAYER])
    data_rho = np.loadtxt(CRUST1_0_DIR + 'crust1.rho').reshape([NO_LAT, NO_LON, NO_LAYER])
    data_bnds = np.loadtxt(CRUST1_0_DIR + 'crust1.bnds').reshape([NO_LAT, NO_LON, NO_LAYER])
    return data_vp, data_vs, data_rho, data_bnds


def extend_lalo(lat1, lat2, lon1, lon2):
    # 外扩范围，使小数部分规整到0.5的整数倍
    lat1 = int(lat1 + 1) + 0.5
    lon1 = int(lon1 - 1) + 0.5
    lat2 = int(lat2 - 1) + 0.5
    lon2 = int(lon2 + 1) + 0.5
    print([lat1, lat2, lon1, lon2])
    return [lat1, lat2, lon1, lon2]

def lalo_to_idx(lat1, lat2, lon1, lon2):
    # 转换成crust1.0数据中的对应坐标
    ilat1 = int(90. - lat1 + 1)
    ilon1 = int(180. + lon1 + 1)
    ilat2 = int(90. - lat2 + 1)
    ilon2 = int(180. + lon2 + 1)
    print([ilat1, ilat2, ilon1, ilon2])
    return [ilat1, ilat2, ilon1, ilon2]


# 提取crust1.0中指定区域的数据
def extract_crust1(data_vp, data_vs, data_rho, data_bnds, ilat1, ilat2, ilon1, ilon2):
    tgt_bnds = data_bnds[ilat1-1:ilat2, ilon1-1:ilon2, :]
    tgt_vp = data_vp[ilat1-1:ilat2, ilon1-1:ilon2, :]
    tgt_vs = data_vs[ilat1-1:ilat2, ilon1-1:ilon2, :]
    tgt_rho = data_rho[ilat1-1:ilat2, ilon1-1:ilon2, :]
    return tgt_vp, tgt_vs, tgt_rho, tgt_bnds


def interp_crust1(tgt_vp, tgt_vs, tgt_rho, tgt_bnds, xlati, ylong, zdepth, ilat1, ilat2, ilon1, ilon2):
    # 邻层取二值平均，计算出各层中间位置
    tgt_dep = (tgt_bnds[:, :, 1:] + tgt_bnds[:, :, :-1]) / 2  # (km)

    # highest: 区域内最高海拔, lowest: 区域内最低海拔
    highest = int(tgt_bnds[:, :, 0].max() * 1000)
    lowest = int(tgt_bnds[:, :, -1].min() * 1000)

    # 层(0:7) --> 深度(hightet:lowest)(m)    z轴: 非线性-->线性
    x_dim, y_dim = tgt_dep.shape[:2]
    
    # z轴范围
    #z_orig = np.dstack([tgt_dep[:, :, :] * 1000,  # 水0 冰1 沉积层234 地壳657
    #                    (lowest - 5000) * np.ones([x_dim, y_dim, 1])  # 莫霍面以下(地幔)8
    #                    ])  # (m)
    #z_range = np.linspace(highest, lowest, zdepth)  # 线性分布的纵向深度值
    
    # 排除水层(0)冰层(1)等层，取th及以下介质
    th = 2
    highest = int(tgt_bnds[:,:,th].max() * 1000) # th层深度
    z_orig = np.dstack([# tgt_bnds[:, :, th] * 1000, # th层
                       tgt_dep[:, :, th::] * 1000,  # th层后，不包含th层
                       (lowest - 5000) * np.ones([x_dim, y_dim, 1])  # 莫霍面以下(地幔)8
                       ])  # (m)
    z_orig_bnds = np.dstack([# tgt_bnds[:, :, th] * 1000, # th层
                       tgt_bnds[:, :, th+1::] * 1000,  # th层后，不包含th层
                       (lowest - 5000) * np.ones([x_dim, y_dim, 1])  # 莫霍面以下(地幔)8
                       ])  # (m)

    z_range = np.linspace(0, lowest, zdepth)  # 线性分布的纵向深度值，***从海平面向下***
    tgt_vp = tgt_vp[:,:,th::]
    tgt_vs = tgt_vs[:,:,th::]
    tgt_rho = tgt_rho[:,:,th::]

    # 纵向插值
    tgt_vp_fullz = np.zeros([*z_orig.shape[:2], zdepth])
    tgt_vs_fullz = np.zeros([*z_orig.shape[:2], zdepth])
    tgt_rho_fullz = np.zeros([*z_orig.shape[:2], zdepth])
    for ii in range(0, x_dim):
        for jj in range(0, y_dim):
            #print("x:%d, y:%d", ii, jj)
            #print("z_orig: ", z_orig[ii, jj])
            # 解决interpolate.PchipInterpolator(x, y)中x必须为单调递增的问题，插值后需再进行反序恢复原顺序
            x = z_orig[ii, jj][::-1]  # 反序，变为由深到浅
            xx = z_orig_bnds[ii, jj][::-1]  # 反序，变为由深到浅
            air_water_bnd = x[-1]
            repeat_idx = np.where(np.diff(xx) == 0)[0]
            x = np.delete(x, repeat_idx)
            if x[-1] < 0: x[-1] = 0 # ***地表最低设为海平面***

            # vp
            y = tgt_vp[ii, jj][::-1]  # 反序，变为由深到浅
            y = np.delete(y, repeat_idx)
            #print(y)
            interpolant = interpolate.PchipInterpolator(x, y)
            tgt_vp_fullz[ii, jj] = interpolant(z_range[::-1])[::-1]  # 反序，恢复为由浅到深

            # vs
            y = tgt_vs[ii, jj][::-1]
            y = np.delete(y, repeat_idx)
            #print(y)
            interpolant = interpolate.PchipInterpolator(x, y)
            tgt_vs_fullz[ii, jj] = interpolant(z_range[::-1])[::-1]

            # rho
            y = tgt_rho[ii, jj][::-1]
            y = np.delete(y, repeat_idx)
            #print(y)
            interpolant = interpolate.PchipInterpolator(x, y)
            tgt_rho_fullz[ii, jj] = interpolant(z_range[::-1])[::-1]

            # 调整，处理空气中的数值和负数值
            for zii in range(len(z_range)):
                # 空气中速度密度设为0
                # if z_range[zii] > air_water_bnd:
                #     tgt_vp_fullz[ii, jj, zii] = 0
                #     tgt_vs_fullz[ii, jj, zii] = 0
                #     tgt_rho_fullz[ii, jj, zii] = 0
                # 速度密度负值改为0
                if tgt_vp_fullz[ii, jj, zii] < 0:
                    print("error: vp <<<<0, idx:", ii, jj)
                    tgt_vp_fullz[ii, jj, zii] = 0
                if tgt_vs_fullz[ii, jj, zii] < 0:
                    print("error: vs <<<<0, idx:", ii, jj)
                    tgt_vs_fullz[ii, jj, zii] = 0
                if tgt_rho_fullz[ii, jj, zii] < 0:
                    print("error: rho<<<<0, idx:", ii, jj)
                    tgt_rho_fullz[ii, jj, zii] = 0
    print('interp on depth success...')

    # 经纬度方向插值
    buff_vp = np.zeros([xlati, ylong, zdepth])
    buff_vs = np.zeros([xlati, ylong, zdepth])
    buff_rho = np.zeros([xlati, ylong, zdepth])

    # 在z平面上2d插值
    xx = np.mgrid[ilat1:ilat2+1:1]
    yy = np.mgrid[ilon1:ilon2+1:1]
    new_xx = np.mgrid[ilat1:ilat2:complex(0, xlati)]
    new_yy = np.mgrid[ilon1:ilon2:complex(0, ylong)]
    for zii in range(len(z_range)):
        fvp = interpolate.interp2d(xx, yy, tgt_vp_fullz[:,:,zii], kind='linear')
        buff_vp[:, :, zii] = fvp(new_xx, new_yy)*1000
        fvs = interpolate.interp2d(xx, yy, tgt_vs_fullz[:, :, zii], kind='linear')
        buff_vs[:, :, zii] = fvs(new_xx, new_yy)*1000
        frho = interpolate.interp2d(xx, yy, tgt_rho_fullz[:, :, zii], kind='linear')
        buff_rho[:, :, zii] = frho(new_xx, new_yy)*1000
        print('interp2d %d/%d done...' %(zii+1, len(z_range)))

    # # griddata插值方法可用，但效率过低
    # # 纵向插值后对应点的坐标
    # xx,yy,zz = np.mgrid[ilat1:ilat2+1:1, ilon1:ilon2+1:1, highest:lowest:complex(0,zdepth)]
    # points = list(zip(xx.reshape([-1]), yy.reshape([-1]), zz.reshape([-1])))
    #
    # # 插值后对应点的坐标
    # x_grid, y_grid, z_grid = np.mgrid[ilat1:ilat2:complex(0, xlati), ilon1:ilon2:complex(0, ylong), highest:lowest:complex(0,zdepth)]
    #
    # # 3维插值，经纬度方向插值
    # buff_vp = griddata(points, tgt_vp_fullz.reshape([-1]), (x_grid, y_grid, z_grid), method='linear')
    # print("buff_vp done...")
    # buff_vs = griddata(points, tgt_vs_fullz.reshape([-1]), (x_grid, y_grid, z_grid), method='linear')
    # print("buff_vs done...")
    # buff_rho = griddata(points, tgt_rho_fullz.reshape([-1]), (x_grid, y_grid, z_grid), method='linear')
    # print("buff_rho done...")

    return buff_vp, buff_vs, buff_rho # 返回插值后vp,vs,rho


def write_mesh(buff_vp, buff_vs, buff_rho):
    f = open(PRE_OUTPUT_DIR+'mesh', 'wb')
    for zz in range(buff_vp.shape[2]):
        for yy in range(buff_vp.shape[1]):
            for xx in range(buff_vp.shape[0]):
                #print('vp: %f, vs:%f, rho:%f'%(buff_vp[xx][yy][zz], buff_vs[xx][yy][zz], buff_rho[xx][yy][zz]))
                bytes = struct.pack('fff', buff_vp[xx][yy][zz], buff_vs[xx][yy][zz], buff_rho[xx][yy][zz])
                f.write(bytes)
        print('write mesh '+str(zz+1)+'/'+str(buff_vp.shape[2]))
    f.close()


def write_coords(lat1, lat2, lon1, lon2, xlati, ylong):
    f = open(PRE_OUTPUT_DIR+'coords', 'w')
    x_coords = np.mgrid[lat1:lat2:complex(0, xlati)]
    y_coords = np.mgrid[lon1:lon2:complex(0, ylong)]
    for y in y_coords:
        for x in x_coords:
            f.write("%.5f %.5f\n" %(y, x))
    f.close()


def genmesh():
    data_vp, data_vs, data_rho, data_bnds = load_crust1(NO_LAT, NO_LON, NO_LAYER, CRUST1_0_DIR)
    print("crust1.0 load success...")
    e_latlon = extend_lalo(lat1, lat2, lon1, lon2)
    i_latlon = lalo_to_idx(*e_latlon)
    tgt_vp, tgt_vs, tgt_rho, tgt_bnds = extract_crust1(data_vp, data_vs, data_rho, data_bnds, *i_latlon)
    print("crust1.0 extract success...")
    buff_vp, buff_vs, buff_rho = interp_crust1(tgt_vp, tgt_vs, tgt_rho, tgt_bnds, xlati, ylong, zdepth, *i_latlon)
    write_mesh(buff_vp, buff_vs, buff_rho)
    write_coords(lat1, lat2, lon1, lon2, xlati, ylong)


if __name__ == "__main__":
    # 划定区域
    genmesh()
