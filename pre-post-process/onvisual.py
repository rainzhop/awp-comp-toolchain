#! /usr/bin/python3

from inputs import *
from config import *
import numpy as np
import os

left_top = (lon1, lat1)
right_bottom = (lon2, lat2)

nx = xt
ny = yt
zt = write_step

basedir = path_input
path_output_x = os.path.join(path_tmp, 'eachstep_x_data_fix')
path_output_y = os.path.join(path_tmp, 'eachstep_y_data_fix')
path_output_z = os.path.join(path_tmp, 'eachstep_z_data_fix')
output_filename_prefix = 'awpoutput'
coor_filename = os.path.abspath(os.path.join(path_tmp, 'coor.txt'))

x_filename_prefix = input_filename_prefix
y_filename_prefix = input_filename_prefix
z_filename_prefix = input_filename_prefix
filename_suffixes = input_filename_suffix

pgv_data_path = os.path.join(path_tmp, 'pgv_vxy.txt')
pga_data_path = os.path.join(path_tmp, 'pga.txt')
# minmax_data_filename = 'awpSfcVelMinMax_fix.txt'

# for gen_con_pics
path_src_x = os.path.abspath(path_output_x)
path_src_y = os.path.abspath(path_output_y)
path_src_z = os.path.abspath(path_output_z)
path_genstep_sh = os.path.abspath('./onvisual/genstep_pic.sh')
path_prepare_sh = os.path.abspath('./onvisual/gmt_prepare.sh')
output_dir = os.path.abspath(os.path.join(path_tmp, 'conpic_fix'))

REGION = "%.2f/%.2f/%.2f/%.2f" %(lon1, lon2, lat2, lat1)
TOWNS_FILE = os.path.abspath('../towns')
EPIC_CENTER = "%f %f 1000" %(HypocenterLong, HypocenterLati) #, HypocenterDepth)
PIC_TITLE = PIC_TITLE
COOR_FILE = coor_filename


def meshgrid_to_lonlat(left_top, right_bottom, nx, ny, x, y):
    x += 1
    y += 1
    lon1, lat1 = left_top
    lon2, lat2 = right_bottom
    p_lon = lon1 + abs(lon2 - lon1) / nx * x
    p_lat = lat1 - abs(lat2 - lat1) / ny * y
    return p_lon, p_lat


def gen_coor_txt(left_top, right_bottom, nx, ny):
    f = open(coor_filename, 'w')
    for j in range(ny):
        content = ''
        for i in range(nx):
            l1, l2 = meshgrid_to_lonlat(left_top, right_bottom, nx, ny, i, j)
            content = content + '%f %f\n' % (l1, l2)
        f.write(content)
        print('Lati:%d, %f, %f\n' % (i, l1, l2))
    f.close()


def chk_file_exist(filename):
    if not os.path.exists(filename):
        print('Error: %s not exists...' % filename)
        exit()
    else:
        return True


def get_v(f, off, nx, ny):
    surf_t = np.fromfile(f.name, dtype=np.float32, count=nx * ny, offset=off)
    surf_t = np.array(surf_t)
    surf_v = surf_t.reshape(nx, ny)
    surf_v = surf_v.T
    return surf_v


class VMinMax:
    def __init__(self):
        self.vx_min = 0
        self.vx_max = 0
        self.vy_min = 0
        self.vy_max = 0
        self.vxy_min = 0
        self.vxy_max = 0
        self.vz_min = 0
        self.vz_max = 0

    def get_vx_minmax(self, v):
        v_min = v.min()
        self.vx_min = v_min if v_min < self.vx_min else self.vx_min
        v_max = v.max()
        self.vx_max = v_max if v_max > self.vx_max else self.vx_max

    def get_vy_minmax(self, v):
        v_min = v.min()
        self.vy_min = v_min if v_min < self.vy_min else self.vy_min
        v_max = v.max()
        self.vy_max = v_max if v_max > self.vy_max else self.vy_max

    def get_vxy_minmax(self, v):
        v_min = v.min()
        self.vxy_min = v_min if v_min < self.vxy_min else self.vxy_min
        v_max = v.max()
        self.vxy_max = v_max if v_max > self.vxy_max else self.vxy_max

    def get_vz_minmax(self, v):
        v_min = v.min()
        self.vz_min = v_min if v_min < self.vz_min else self.vz_min
        v_max = v.max()
        self.vz_max = v_max if v_max > self.vz_max else self.vz_max


def gen_eachstep_data():
    pgv_vxy = np.zeros([nx, ny])
    pga = np.zeros([nx, ny])
    tmpMat = np.zeros([nx, ny, 2]) #用于临时存放连续两步的vxy数据
    last_vxy = np.zeros([nx, ny])

    cur_step = 0
    for suffix in filename_suffixes:
        x_filename = os.path.join(basedir, x_filename_prefix + suffix)
        chk_file_exist(x_filename)
        y_filename = os.path.join(basedir, y_filename_prefix+suffix)
        chk_file_exist(y_filename)
        # z_filename = os.path.join(basedir, z_filename_prefix+suffix)
        # chk_file_exist(z_filename)

        fx = open(x_filename, 'rb')
        fy = open(y_filename, 'rb')
        # fz = open(z_filename, 'rb')
        vmm = VMinMax()
        for z in range(0, write_step, n_ti_skp):
            cur_step += n_ti_skp

            offset = nx * ny * z * 4
            surf_vx = get_v(fx, offset, nx, ny)
            surf_vy = get_v(fy, offset, nx, ny)
            surf_vxy = np.sqrt(surf_vx**2 + surf_vy**2)
            # surf_vz = get_v(fz, offset, nx, ny)

            # vmm.get_vx_minmax(surf_vx)
            # vmm.get_vy_minmax(surf_vy)
            # vmm.get_vxy_minmax(surf_vxy)
            # vmm.get_vz_minmax(surf_vz)

            if cur_step == n_ti_skp:
                pgv_vxy = surf_vxy
            else:
                tmpMat[:, :, 0] = pgv_vxy
                tmpMat[:, :, 1] = surf_vxy
                pgv_vxy = np.amax(tmpMat, axis=2)
                
                curr_a = surf_vxy - last_vxy
                if cur_step == n_ti_skp*2:
                    pga = curr_a
                else:
                    tmpMat[:, :, 0] = pga
                    tmpMat[:, :, 1] = curr_a
                    pga = np.amax(tmpMat, axis=2)
            last_vxy = surf_vxy

            print('cur_step = %d' % cur_step)
            eachstep_data_filename = os.path.join(path_output_x, 'awpsfc%05d.txt' % (cur_step))
            with open(eachstep_data_filename, 'w') as f:
                for vx in surf_vx.flat:
                    f.write(str(vx) + '\n')
            # eachstep_data_filename = os.path.join(path_output_z, 'awpsfc%05d.txt' % (cur_step))
            # with open(eachstep_data_filename, 'w') as f:
            #    for vz in surf_vz.flat:
            #        f.write(str(vz) + '\n')
        fx.close()
        fy.close()
        # fz.close()

    with open(pgv_data_path, 'w') as f:
       for v in pgv_vxy.flat:
           f.write(str(v) + '\n')

    with open(pga_data_path, 'w') as f:
       for v in pga.flat:
           f.write(str(v) + '\n')

    # with open(minmax_data_filename, 'w') as f:
    #    f.write('# Vx Min: %0.5f\n# Vx Max: %0.5f\n' %(vmm.vx_min, vmm.vx_max))
    #    f.write('# Vy Min: %0.5f\n# Vy Max: %0.5f\n' %(vmm.vy_min, vmm.vy_max))
    #    f.write('# Vz Min: %0.5f\n# Vz Max: %0.5f\n' %(vmm.vz_min, vmm.vz_max))
    #    f.write('# Vxy Min: %0.5f\n# Vxy Max: %0.5f\n' %(vmm.vxy_min, vmm.vxy_max))

    print('Done.')


def chk_file_exist(filename):
    if not os.path.exists(filename):
        print('Error: %s not exists...' % filename)
        exit()
    else:
        return True


def gmt_prepare():
    cmd = 'sh %s %s' % (path_prepare_sh, REGION)
    os.system(cmd)


def gen_conpic():
    for i_step in range(start_step + 1, stop_step + 1, 1):
        src_filename = os.path.join(path_src_x, 'awpsfc%05d.txt' % i_step)
        chk_file_exist(src_filename)

        cmd = 'sh %s "%s" %05d %.1fSec "%s" "%s" "%s" "%s" "%s" "%s"' \
              % (path_genstep_sh,  # $0  绘图脚本文件
                 src_filename,  # $1  源数据文件
                 i_step,  # $2  图片文件名称
                 i_step * dt,  # $3  模拟传播时刻
                 REGION,  # $4  绘图区域
                 EPIC_CENTER,  # $5  震中位置
                 TOWNS_FILE,  # $6  城镇文件
                 PIC_TITLE,  # $8  绘图标题
                 COOR_FILE,  # $9  坐标文件
                 output_dir  # $10 绘图输出目录
                 )
        print(cmd)
        status = os.system(cmd)
        if status != 0:
            print('Step:%5d occur error.' % i_step)
            exit()

        print('%5d' % (i_step))


if __name__ == "__main__":
    gen_coor_txt(left_top, right_bottom, nx, ny)
    gen_eachstep_data()
    os.chdir('./onvisual')
    gmt_prepare()
    gen_conpic()
    os.system("sh ./clean.sh")
