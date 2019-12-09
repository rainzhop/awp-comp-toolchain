# 针对awp-odc-os的前后处理软件

## 主要功能

* 震源格式化
* 地壳格式化
* 制作模拟动画 

完成针对awp-odc-os的前后处理。

## 项目状态

项目处于非常原始的阶段。由于对地震学知识的缺乏，在上述三个功能的实现中都存在大量错误。比如对crust1.0模型的插值过分随意，对震源信息的使用很不充分甚至存在错误等。

## 项目目标

期望形成一个工具链，结合awp-odc-os，在输入从[CMT](https://www.globalcmt.org/)获取的震源数据后，可自动完成模拟和传播动画制作。

## 备忘

awp-odc需要mpi+cuda环境。

目前在ubuntu 18.04上测试通过，使用mpich，nv驱动418，cuda版本10.0。


