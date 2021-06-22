# Camera Calibration
> 集合了相机标定相关的多个脚本工具，便于完成完整的车载环视相机标定流程  
> 各代码文件均可单独使用，此外也提供了外部接口以供调用  
  
![](https://img.shields.io/badge/Language-python-blue.svg) 　
![](https://img.shields.io/badge/Requirement-openCV-brightgreen) 　
![License](https://img.shields.io/badge/License-GPL-orange.svg)

## DEMO
![DEMO](demo.gif)

## Quick Start
克隆该仓库，运行main.py查看简单示例结果  
确保已经安装好**opencv(>=3.4.2)** 以及**numpy(>=1.19.2)** 
```
git clone https://github.com/dyfcalid/CameraCalibration.git
cd ./CameraCalibration
python main.py
```  
  
## File Tree  
> 项目结构预览  
```
│  main.py                    // 主程序
│
├─ExtrinsicCalibration
│  │  extrinsicCalib.ipynb    // 外参标定代码(含注释)
│  │  extrinsicCalib.py       // 外参标定python代码
│  │  README.md               // 外参标定文档
│  │  __init__.py             // init文件，API说明
│  │
│  └─data                     // 外参标定数据文件夹
│
├─IntrinsicCalibration
│  │  intrinsicCalib.ipynb    // 内参标定代码(含注释)
│  │  intrinsicCalib.py       // 内参标定python代码
│  │  README.md               // 内参标定文档
│  │  __init__.py             // init文件，API说明
│  │
│  └─data                     // 内参标定数据文件夹
│
├─SurroundBirdEyeView
│  │  surroundBEV.ipynb       // 环视鸟瞰代码(含注释)
│  │  surroundBEV.py          // 环视鸟瞰python代码
│  │  README.md               // 环视鸟瞰文档
│  │  __init__.py             // init文件，API说明
│  │
│  └─data                     // 环视鸟瞰参数文件夹
│     ├─front                 // 存放前相机K、D、H参数文件
│     ├─back                  // 存放后相机K、D、H参数文件
│     ├─left                  // 存放左相机K、D、H参数文件
│     └─right                 // 存放右相机K、D、H参数文件
│
└─Tools                       // 一些相关的标定工具
    │  collect.py             // 图像采集
    │  undistort.py           // 图像去畸变
    └─data                    // 数据文件夹

```

  
## Camera Intrinsic Calibration 
> 相机内参标定   
  
`intrinsicCalib.py`  [查看文档](./IntrinsicCalibration/README.md/)  
包括相机的**在线标定**和**离线标定**，包含**鱼眼相机**和**普通相机**模型，  
并支持**相机、视频、图像**三种输入，生成相机内参和畸变向量   

- 可以直接运行python文件，并通过argparse输入更多参数，argparse参数表详见文档
```
python intrinsicCalib.py
```  

- 此外，提供`InCalibrator`类供调用，使用说明如下，具体示例见**main.py**  
```
from intrinsicCalib import InCalibrator

calibrator = InCalibrator(camera_type)              # 初始化内参标定器
for img in images:
    result = calibrator(img)                        # 每次读入一张原始图片 更新标定结果
undist_img = calibrator.undistort(raw_frame)        # 使用undistort方法得到去畸变图像
```
或者调用`CalibMode`类，使用预设好的标定模式，各模式详见文档  
```
from intrinsicCalib import InCalibrator, CalibMode

calibrator = InCalibrator(camera_type)              # 初始化内参标定器
calib = CalibMode(calibrator, input_type, mode)     # 选择标定模式
result = calib()                                    # 开始标定
```
可以直接修改原文件中的各参数，或使用`get_args()`方法获取参数并修改
```
args = InCalibrator.get_args()                      # 获取args参数
args.INPUT_PATH = './IntrinsicCalibration/data/'    # 修改args参数
calibrator = InCalibrator(camera_type)              # 初始化内参标定器
```  

示例结果：  
<img src="https://i.loli.net/2021/06/22/nxOsU1mM4D3kJWS.png" width="750" height="200" alt="inCalib_result.jpg"/>  
<img src="https://i.loli.net/2021/06/22/iVETOUIMqCRHDYr.png" width="750" height="300" alt="inCalib_image.jpg"/>  
  
  
## Camera Extrinsic Calibration  
> 相机外参标定   

`extrinsicCalib.py`  [查看文档](./ExtrinsicCalibration/README.md/)    
完成相机的**外参标定**，实现**任意两个视图（包含相同标定板）的转换**，生成**单应性变换矩阵**  
如：基于**无人机相机**和**车载环视相机**同时拍摄地面的标定板，进行车载相机的外参标定，  
生成车载相机至无人机相机的单应性变换矩阵，实现**鸟瞰图**的转换（即将车载相机视角转换至无人机视角）    
  
- 可以直接运行python文件，并通过argparse输入更多参数，argparse参数表详见文档
```
python extrinsicCalib.py
```  
  
- 此外，提供`ExCalibrator`类供调用，使用说明如下，具体示例见**main.py**  
```
from extrinsicCalib import ExCalibrator

exCalib = ExCalibrator()                            # 初始化外参标定器
homography = exCalib(src_raw, dst_raw)              # 输入对应的两张去畸变图像 得到单应性矩阵
src_warp = exCalib.warp()                           # 使用warp方法得到原始图像的变换结果
```    
可以直接修改原文件中的各参数，或使用`get_args()`方法获取参数并修改  
```
args = ExCalibrator.get_args()                      # 获取args参数
args.INPUT_PATH = './ExtrinsicCalibration/data/'    # 修改args参数
exCalib = ExCalibrator()                            # 初始化外参标定器
```    
  
示例结果：   
![exCalib_result.jpg](https://i.loli.net/2021/06/22/5fMmcxTuZ2aIUyN.png)   
  
  
## Surround Camera Bird Eye View  
> 环视相机鸟瞰拼接图生成  
  
`surroundBEV.py`  [查看文档](./SurroundBirdEyeView/README.md/)    
输入前后左右四张**原始相机图像**，生成**鸟瞰图**  
包括**直接拼接**和**融合拼接**，并可以进行**亮度平衡和白平衡**   
  
- 可以直接运行python文件，并通过argparse输入更多参数，argparse参数表详见文档
```
python surroundBEV.py
```  
  
- 此外，提供`BevGenerator`类供调用，使用说明如下，具体示例见**main.py**  
```
from surroundBEV import BevGenerator

bev = BevGenerator()                                # 初始化环视鸟瞰生成器
surround = bev(front,back,left,right)               # 输入前后左右四张原始相机图像 得到拼接后的鸟瞰图
```    
上面生成的是直接拼接的结果，能够保证**实时性**，此外也可以使用融合和平衡，但速度较慢，如
```
bev = BevGenerator(blend=True, balance=True)        # 使用图像融合以及平衡
surround = bev(front,back,left,right,car)           # 可以加入车辆图片
```
可以直接修改原文件中的各参数，或使用`get_args()`方法获取参数并修改  
```
args = BevGenerator.get_args()                      # 获取环视鸟瞰args参数
args.CAR_WIDTH = 200
args.CAR_HEIGHT = 350                               # 修改为新的参数
bev = BevGenerator()                                # 初始化环视鸟瞰生成器
```    
  
示例结果：    
<div align=center><img src="https://i.loli.net/2021/06/22/fOwPsTYkCFeo8dW.png" width="740" height="170" alt="camera.jpg"/></div>  
<div align=center><img src="https://i.loli.net/2021/06/22/HeKJVBm2vEINy4z.png" width="360" height="400" alt="bev.jpg"/></div>   
   
   
## Other Tools  
用`collect.py`可以开启相机完成图像或视频的**数据采集**  
用`undistort.py`可以批量完成图像的**去畸变处理**   
用`decomposeH.py`可以由单应性矩阵H和相机内参K得到**旋转矩阵R和平移矩阵T** （有多个结果需要筛选）   
用`timeAlign.py`可以将以**时间戳**命名的图片按时间**对准**，得到对应的列表   
用`img2vid.py`可以将图片转化为视频  
     
## License  
[GPL-3.0 License](LICENSE)  
  
  
*`Copyright (c) 2021 ZZH`*  
  
  
