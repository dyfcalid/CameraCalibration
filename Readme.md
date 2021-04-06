# Camera Calibration
> 相机标定和图像去畸变python脚本
  
依赖库：opencv、numpy  

使用`fisheye.py`可以完成鱼眼相机的**快速、实时标定**，生成标定结果  
使用`undistort.py`可以便捷地完成图像的**去畸变处理**  

【目录】  
- [Quick Start](#quick-start)
  * [fisheye.py](#fisheyepy)
  * [undistort.py](#undistortpy)
- [Calibration Principle](#calibration-principle)
- [Code Detailed Annotation](#code-detailed-annotation)

## Quick Start
### fisheye.py 
> 鱼眼相机标定  

连接相机后并准备好棋盘标定板后，在命令行运行即可 
```
python fisheye.py
```
可以通过argparse输入更多参数，使用 '-h' 查看所有参数信息
```
python fisheye.py -h
```

| Argument  | Type | Default | Help                                          | 
|:----------|:----:|:-------:|:----------------------------------------------|
| -id       | int  | 1       | Camera ID                                     |
| -fw       | int  | 1280    | Camera Frame Width                            |
| -fh       | int  | 720     | Camera Frame Height                           |
| -bw       | int  | 6       | Chess Board Width (corners number)            |
| -bh       | int  | 8       | Chess Board Height (corners number)           |
| -square   | int  | 20      | Chess Board Square Size (mm)                  |
| -calibrate| int  | 10      | Required Calibration Frame Number             |
| -delay    | int  | 4       | Find Chessboard Delay (frame number)          |
| -read     | int  | 10      | Max Read Image Failed Criteria (frame number) |

**示例**： 相机分辨率为1280×720，棋盘格**角点数**为9×6，每小格边长10mm，未输入参数保持默认值，键入
```
python fisheye.py -fw 1280 -fh 720 -bw 9 -bh 6 -square 10
```
-------------------------------------------------------------------------------
程序正常运行，开启相机并读取图像后，会出现`raw_frame`窗口
- 将相机对准标定板
- 稳定移动相机从多个角度对准棋盘 

当相机找到标定板并采集到一定数量的数据后，会出现`undistort_frame`窗口，此时已完成初步标定，生成去畸变图像
- 继续采集数据，程序会不断优化标定结果
- 当去畸变图像稳定后，按ESC退出，完成标定

标定结果的相机内参矩阵存储在`camera_K.npy`中，畸变系数向量存储在`camera_D.npy`中

该程序运行过程如图所示
![1.png](https://i.loli.net/2021/04/06/OAMVYJqezPcFhjI.png)

为提高标定精度，需要：
- 保证棋盘标定板的平直和准确
- 尽量保证相机稳定，减小晃动和运动模糊
- 选择更多角点数量的标定板
- 保证光照条件
- 多次标定  

--------------------------------------------------------------------------------

### undistort.py
> 根据相机内参和畸变向量对原始图像进行去畸变操作  

将需要处理的原始图片、标定生成的结果数据(`camera_K.npy`和`camera_D.npy`)放在和该脚本文件**相同路径**下，在命令行中运行即可
```
python undistort.py
```
可以通过argparse输入更多参数，使用 '-h' 查看所有参数信息
```
python undistort.py -h
```
| Argument   | Type  | Default | Help                                              | 
|:-----------|:-----:|:-------:|:--------------------------------------------------|
| -width     | int   | 1280    | Camera Frame Width                                |
| -height    | int   | 720     | Camera Frame Height                               |
| -focal     | float | 340     | Camera Focal                                      |
| -focalscale| float | 1       | Camera Focal Scale                                |
| -offset    | float | 0       | Vertical Offset of Height                         |
| -load      | int   | False   | Load New Camera K/D Data (False/True)             |
| -srcformat | str   | png     | Source Image Format (jpg/png)                     |
| -dstformat | str   | jpg     | Destination Image Format (jpg/png)                |
| -quality   | int   | 90      | Save Image Quality (jpg:0-100, png:9-0 (low-high))|
| -name      | str   | None    | Save Image Name                                   |

**示例**： 若要对数张`png`原始数据进行处理，使用`新的标定数据`，得到`1280×720`大小的去畸变图像，  
命名为`UndistortPic`，以`jpg`格式存储，`存储质量设为95`，其他保持默认，则运行以下命令即可
```
 python undistort.py -width 1280 -height 720 -load True -srcformat png -dstformat jpg -name UndistortPic -quality 95
```
该脚本文件路径下所有符合`-srcformat`格式的图片均会进行去畸变处理并生成新图片

--------------------------------------------------------------------------------

## Calibration Principle
> Reference: [OpenCV官方文档](https://docs.opencv.org/3.0.0/db/d58/group__calib3d__fisheye.html)、视觉SLAM十四讲

世界坐标系和相机坐标系的变换可以通过旋转矩阵R和平移向量t实现，即：  
![1](http://latex.codecogs.com/svg.latex?\begin{bmatrix}{x}\\\\{y}\\\\{z}\\\\\end{bmatrix}=R\\cdot\\begin{bmatrix}{X}\\\\{Y}\\\\{Z}\\\\\end{bmatrix}+t)   
相机的内参矩阵K表示如下，**相机内参可以通过数学推导得到闭环解，是标定结果之一**：  
![2](http://latex.codecogs.com/svg.latex?\begin{bmatrix}{f_{x}}&{0}&{c_{x}}\\\\{0}&{f_{y}}&{c_{y}}\\\\{0}&{0}&{1}\\\\\end{bmatrix})  
用变换矩阵T=[R|t]表示相机的位姿，结合上式像素坐标Pc和世界坐标Pw的关系：    
![3](http://latex.codecogs.com/svg.latex?\{P_c}=KT{P_w})  
对坐标z进行归一化，得到归一化坐标x'和y'，并使用极坐标系r、θ进行表示：  
![4](http://latex.codecogs.com/svg.latex?\begin{cases}x^{'}=x\setminus{z}\\\\y^{'}=y\setminus{z}\\\\r^{2}=x^{'2}+y^{'2}\\\\\theta=atan(r)\\\\\end{cases})  
透镜形状引起的畸变分为径向畸变和切向畸变两种，可以用和距中心距离有关的二次及高次多项式函数进行纠正  
针对鱼眼相机的**畸变，使用k1,k2,k3,k4为系数的θ多项式进行描述，D=(k1,k2,k3,k4)即为标定结果之一**：  
![5](http://latex.codecogs.com/svg.latex?\\theta_{d}=\theta(1+k_{1}\theta^{2}+k_{2}\theta^{4}+k_{3}\theta^{6}+k_{4}\theta^{8}))  
相机坐标系点经过畸变后坐标为：  
![6](http://latex.codecogs.com/svg.latex?\begin{cases}x^{'}=(\theta_{d}\setminus{r})x\\\\y^{'}=(\theta_{d}\setminus{r})y\\\\\end{cases})  
最终的像素点坐标为：  
![6](http://latex.codecogs.com/svg.latex?\begin{cases}u=f_{x}(x^{'}+\alpha{y^{'}})+c_{x}\\\\v=f_{y}yy+c_{y}\\\\\end{cases})  
  
**标定过程**：
- 摄像头采集图像（有一定间隔）
- 寻找棋盘角点 (cv2.findChessboardCorners)，得到角点坐标
- 对角点坐标进行亚像素优化 (cv2.cornerSubPix)，原理参照[亚像素优化原理](https://xueyayang.github.io/pdf_posts/%E4%BA%9A%E5%83%8F%E7%B4%A0%E8%A7%92%E7%82%B9%E7%9A%84%E6%B1%82%E6%B3%95.pdf)
- 估计计算相机内参 (cv2.CALIB_USE_INTRINSIC_GUESS)
- 得到标定结果 (cv2.fisheye.calibrate)，并根据新数据不断优化  
*注：具体函数细节可参照openCV官方文档或代码注释*

## Code Detailed Annotation
关于fisheye.py的**中文详细代码注释**可以参见[fisheye.ipynb](https://nbviewer.jupyter.org/github/dyfcalid/CameraCalibration/blob/master/fisheye.ipynb)  
  
`2021.4 ZZH`
