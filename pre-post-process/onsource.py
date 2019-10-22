from config import *
from inputs import *
import numpy as np
from numpy import sin, cos, exp, pi, sqrt, cross
from numpy.linalg import norm


Source_TMAX = 20 # Second
dt = 0.02
dh = 400

Source_Time_Fun_Type = 1


def dis2mom(strike,dip,rake):
    # function dis2mom(strike,dip,rake)
    # 计算断层面表示的矩张量
    # 输入:
    #     strike: 断层走向(正北顺时针旋转的角度)
    #        dip: 倾角，断层面与水平方向夹角
    #       rake: 滑动角(在断层面上走向计算的逆时针旋转至滑动方向的角度)
    # 所有角度的单位均为度
    # 输出: Mxx=m(1)， Myy=m(2)， Mzz=m(3)，Mxy=m(4)，Mxz=m(5)，Myz=m(6)，为北东下坐标系中表示的矩张量
    con = pi/180.
    s = strike*con
    d = dip*con
    r = rake*con
    m = np.zeros([6])
    m[0] = -sin(s) * sin(s) * sin(r) * sin(2 * d) - sin(2 * s) * cos(r) * sin(d)
    m[1] = -cos(s) * cos(s) * sin(r) * sin(2 * d) + sin(2 * s) * cos(r) * sin(d)
    m[2] = sin(r) * sin(2 * d)
    m[3] = cos(2 * s) * cos(r) * sin(d) + 0.5 * sin(2 * s) * sin(r) * sin(2 * d)
    m[4] = -cos(s) * cos(r) * cos(d) - sin(s) * sin(r) * cos(2 * d)
    m[5] = -sin(s) * cos(r) * cos(d) + cos(s) * sin(r) * cos(2 * d)
    return m


def coord_map_loLa_2_meshgrid_3(dh, long, lati, depth):
    # 经纬度坐标与Mesh Grid坐标转换
    # 本函数中心的一些参数与Yong Zhang提供的2013台湾南投地震相关连
    # 将坐标转换为网络的点坐标
    #
    #  输入: dh 网格间隔大小(unit:m)
    #        Long  经度
    #        lati  纬度
    #        depth Km
    #    所有角度的单位均为度
    # 输出: Mxx=m(1)， Myy=m(2)， Mzz=m(3)，Mxy=m(4)，Mxz=m(5)，Myz=m(6)，为北东下坐标系中表示的矩张量
    HypocenterLong = long
    HypocenterLati = lati

    # 左下角经纬度 点1
    Long1 = lon1
    Lati1 = lat2
    # 左上角经纬度 点2
    Long2 = lon1
    Lati2 = lat1
    # 右上角经纬度 点3
    Long3 = lon2
    Lati3 = lat1
    # 右下角经纬度 点4
    Long4 = lon2
    Lati4 = lat2

    k = np.divide(Lati2 - Lati1, Long2 - Long1)
    ang = np.arctan(k)
    ang = -(pi / 2 - ang)

    h = sqrt((Long2 - Long1)**2 + (Lati2 - Lati1)**2) # 单位应该是度，与后面的计算距离应该是对应的
    w = sqrt((Long3 - Long2)**2 + (Lati3 - Lati2)**2) # 单位应该是度
    x0 = Long1
    y0 = Lati1

    Q1 = np.array([Long1, Lati1, 0])
    Q2 = np.array([Long2, Lati2, 0])
    Q3 = np.array([Long3, Lati3, 0])
    Q4 = np.array([Long4, Lati4, 0])
    P = [HypocenterLong, HypocenterLati,  0]
    # 单位应该是度，与前面的经纬度距离计算应该是对应的
    d1 = norm(cross(Q2 - Q1, P - Q1)) / norm(Q2 - Q1) # 点到直线距离计算 P-点坐标；Q1, Q2线上两点坐标
    d2 = norm(cross(Q3 - Q2, P - Q2)) / norm(Q3 - Q2)
    coordx = int(round(d1 / (w / xlati)))
    coordy = int(round(d2 / (h / ylong)))
    coordz = int(round(depth * 1000 / dh))

    return [coordy, coordx, coordz]


def gensource():
    m = dis2mom(strike, dip, rake)
    Mxx, Myy, Mzz, Mxy, Mxz, Myz = m * M0

    Mxx = Mtt
    Myy = Mpp
    Mzz = Mrr
    Mxz = Mrt
    Myz = -Mrp
    Mxy = -Mtp

    if Source_Time_Fun_Type == 0:
        T = 0.1
        s = np.zeros(int(Source_TMAX / dt))
        for st in range(int(Source_TMAX / dt)):
            tt = dt * st
            s[st] = tt/(T*T)* exp(-tt/T)
    elif Source_Time_Fun_Type == 1:
        t = np.mgrid[0:pi:pi/(Source_TMAX/dt-1)]
        s = sin(t)
    # Gaussian form(x) LiZhao Fre´chet Kernels
    elif Source_Time_Fun_Type == 2:
        t = np.mgrid[0:0.67:0.67/(Source_TMAX/dt-1)]
        c1 = 60
        c2 = 0.65
        s = exp(-c1 * (t - c2/2) * (t - c2/2))

    # 转换经纬度深度 到 网络坐标
    Loc = coord_map_loLa_2_meshgrid_3(dh, HypocenterLong, HypocenterLati, HypocenterDepth)
    x, y, z = Loc # Actual Location: x*dh, y*dh, z*dh

    f = open(PRE_OUTPUT_DIR+'source', 'wb')
    import struct
    # 1st source location(int*3)
    bytes = struct.pack("iii", x,y,z)
    print('x, y, z', x, y, z)
    f.write(bytes)
    # #timestep value(float*6)
    for st in range(len(s)):
        #print(Mxx*s[st], Myy*s[st], Mzz*s[st], Mxz*s[st], Myz*s[st], Mxy*s[st])
        bytes = struct.pack('ffffff', Mxx*s[st], Myy*s[st], Mzz*s[st], Mxz*s[st], Myz*s[st], Mxy*s[st])
        f.write(bytes)
    f.close()


if __name__ == "__main__":
    gensource()


