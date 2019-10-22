from config import *
from inputs import *
import numpy as np
import array
from matplotlib import pyplot as plt
import os


s = 1 # ?

# find Max Min
def find_maxmin():
    max_a = 0.0
    min_a = 0.0
    for suffix in input_filename_suffix:
        file_full_path = path_input + input_filename_prefix + suffix
        f = open(file_full_path, 'rb')
        a = array.array('f')
        a.fromfile(f, int(os.path.getsize(f.name)/4))
        f.close()

        tmax_a = np.max(a)
        tmin_a = np.min(a)
        print("File:%s, Data count:%d, Max:%f, Min:%f" % (file_full_path, len(a), tmax_a, tmin_a))
        if tmax_a > max_a: max_a = tmax_a
        if tmin_a < min_a: min_a = tmin_a

    max_a = max_a * s
    min_a = min_a * s
    print('Total Max:%f, Min:%f' %(max_a, min_a))
    return max_a, min_a


# find extreme value
def find_extreme_value(max_a, min_a):
    extreme_value = 0
    if np.sign(max_a) != np.sign(min_a):
        if max_a > abs(min_a):
            extreme_value = max_a
        else:
            extreme_value = abs(min_a)
    else:
        if abs(max_a) > abs(min_a):
            extreme_value = abs(max_a)
        else:
            extream_value = abs(min_a)
    return extreme_value


# Generate Pics
def gen_pics(max_a, min_a, extreme_value):
    cur_step = 0
    for suffix in input_filename_suffix:
        file_full_path = path_input + input_filename_prefix + suffix
        f = open(file_full_path, 'rb')
        print('Processing File: %s' %file_full_path)
        print('cur_step')

        origin = -1
        for z in range(write_step):
            cur_step = cur_step + 1
            if cur_step >= start_step and cur_step <= stop_step and np.mod(z, n_ti_skp) == 0:
                offset = xt*yt*z*4
                f.seek(offset)
                surf = array.array('f')
                surf.fromfile(f, xt*yt) # todo 确认fromfile与f.seek是否可行
                surf_v = np.reshape(surf, [xt, yt])
                max_val = np.max(np.abs(surf_v))

                print(cur_step)

                # 画图，输出到文件
                plt.figure()
                plt.imshow(surf_v)
                t = 'TimeStep: %05d, t=%.2fs, max=%.3fcm/s' %(cur_step, dt * cur_step, max_val * 100)
                plt.title(t, position = [140, 20])
                plt.axis('equal')
                plt.axis('tight')

                if np.sign(max_a) != np.sign(min_a):
                    plt.clim(-extreme_value, extreme_value)
                else:
                    plt.clim(min_a, max_a)
                plt.colorbar()

                pic_name = path_output + output_filename_prefix + 'dyn_%05d' %cur_step
                plt.savefig(pic_name + '.png')
                plt.close()
        print()
        f.close()

    print('Done.')


def genpics():
    max_a, min_a = find_maxmin()
    extreme_value = find_extreme_value(max_a, min_a)
    gen_pics(max_a, min_a, extreme_value)

if __name__ == '__main__':
    #find_maxmin()
    genpics()
