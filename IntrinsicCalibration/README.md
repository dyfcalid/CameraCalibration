# Camera Intrinsic Calibration
> 相机内参在线标定
  
Requirement： opencv(>=3.4.2) numpy(>=1.19.2)  
  
使用`intrinsicCalib.py`可以完成相机的**在线标定**和**离线标定**，包含**鱼眼相机**和**普通相机**模型，  
同时支持**相机、视频、图像**三种输入，生成**相机内参**和**畸变向量**，并显示**重投影误差**    
详细注释包含在`intrinsicCalib.ipynb`中，也可以在Jupyter Notebook中直接运行该代码   
可以根据得到的相机内参和畸变向量文件用Tools中的`undistort.py`完成图像去畸变处理  
  

【目录】  
- [Quick Start](#quick-start)
  * [intrinsicCalib.py](#intrinsiccalibpy)
    + 在线标定
    + 离线标定
    + 手动模式
    + 更多设置
- [Calibration Principle](#calibration-principle)
- [Code Detailed Annotation](#code-detailed-annotation)

## Quick Start
### intrinsicCalib.py 
> 相机内参标定  

**连接相机**后并准备好棋盘标定板后，在命令行运行即可（默认相机在线标定）  
```
python intrinsicCalib.py
```
可以通过argparse输入更多参数，使用`-h`或`--help` 查看所有参数信息，请**注意各参数的默认值**
```
python intrinsicCalib.py -h
```

| Argument   | Type | Default   | Help                                             | 备注                             |
|:-----------|:----:|:---------:|:-------------------------------------------------|:---------------------------------|
| -input     | str  | camera    | Input Source: camera/video/image                 | 输入形式 相机/视频/图像           |
| -type      | str  | fisheye   | Camera Type: fisheye/normal                      | 相机类型 鱼眼/普通                |
| -id        | int  | 1         | Camera ID                                        | 相机编号                          |
| -path      | str  | ./data/   | Input Video/Image Path                           | 图片、视频输入路径                |
| -video     | str  | video.mp4 | Input Video File Name (eg.: video.mp4)           | 输入视频文件名(含扩展名)          |
| -image     | str  | img_raw   | Input Image File Name Prefix (eg.: img_raw)      | 输入图像文件名前缀                |
| -mode      | str  | auto      | Image Select Mode: auto/manual                   | 选择自动/手动模式                 |
| -fw        | int  | 1280      | Camera Frame Width                               | 相机分辨率 帧宽度                 |
| -fh        | int  | 1024      | Camera Frame Height                              | 相机分辨率 帧高度                 |
| -bw        | int  | 7         | Chess Board Width (corners number)               | 棋盘宽度 【内角点数】             |
| -bh        | int  | 6         | Chess Board Height (corners number)              | 棋盘高度 【内角点数】             |
| -size      | int  | 10        | Chess Board Square Size (mm)                     | 棋盘格边长 mm                     |
| -num       | int  | 5         | Least Required Calibration Frame Number          | 初始化最小标定图片采样数量        |
| -delay     | int  | 8         | Capture Image Time Interval (frame number)       | 间隔多少帧数采样                  |
| -subpix    | int  | 5         | Corners Subpix Optimization Region               | 角点坐标亚像素优化时的搜索区域大小 |
| -fps       | int  | 20        | Camera Frame per Second (FPS)                    | 相机的帧率                        |
| -fs        | float| 0.5       | Camera Undistort Focal Scale                     | 去畸变时的焦距缩放系数            |
| -ss        | float| 1         | Camera Undistort Size Scale                      | 去畸变时的尺寸缩放系数            |
| -store     | bool | False     | Store Captured Images (Ture/False)               | 是否保存抓取的图像                |
| -store_path| str  | ./data/   | Path to Store Captured Images                    | 保存抓取的图像的路径              |
| -crop      | bool | False     | Crop Input Video/Image to (fw,fh) (Ture/False)   | 是否将输入视频/图像尺寸裁剪至fw fh|
| -resize    | bool | False     | Resize Input Video/Image to (fw,fh) (Ture/False) | 是否将输入视频/图像尺寸缩放至fw fh|
   
-------------------------------------------------------------------------------
   
程序在`CalibMode`中预设了**六种标定模式**，包括相机、视频、图片输入的手动/自动模式  
**相机在线标定**较为简单快速，但为了更高精度，推荐**视频/图片离线标定**  
（如在相机标定模式下将`-store`设置为True，保存采集图像，之后再利用图片手动模式挑选质量较好的清晰图片并去掉未对准角点的图）    
（或者使用相机录制视频，之后再利用视频标定模式离线标定，选取较好的结果）  
下面通过几个示例进行说明：     
   
#### 示例1 (在线标定)      
**此时为鱼眼相机自动在线标定** （默认设置）    
若相机分辨率设置为1280×720，棋盘格**角点数**为6×8，每小格**边长**20mm(也可以不设置保持默认)，未输入参数保持默认值，则键入  
```
python intrinsicCalib.py -fw 1280 -fh 720 -bw 6 -bh 8 -size 20
```  
（默认`-id 1`的相机输入`-input camera`，鱼眼相机模型`-type fisheye`，自动模式`-mode auto`）  
程序正常运行，开启相机并读取图像后，会出现`raw_frame`窗口  
- 将相机对准标定板
- 按下**空格键**开始标定
- 稳定移动相机从多个角度对准棋盘 
  
当相机找到标定板并采集到一定数量的数据后，会出现`undistort_frame`窗口，此时已完成初步标定，生成去畸变图像
- 继续采集数据，程序会不断优化标定结果
- 当去畸变图像稳定后，按**ESC**退出，完成标定
  
标定结果的相机内参矩阵存储在`camera_{id}_K.npy`中，畸变系数向量存储在`camera_{id}_D.npy`中  
其中{id}即为-id的输入参数，**建议每次标定都输入相应相机的ID值**，便于管理和区分数据  
  
该程序运行过程如图所示
![1.png](https://i.loli.net/2021/04/06/OAMVYJqezPcFhjI.png)  
  
为提高标定精度，需要：
- 保证棋盘标定板的平直和准确
- 尽量保证相机稳定，减小晃动和运动模糊
- 选择更多角点数量的标定板
- 保证光照条件
- 多次标定  
  
--------------------------------------------------------------------------------
  
#### 示例2 (离线标定)    
(注：**建议将视频或图像放下./data/下并按默认值命名**，可以省去参数输入便于使用)  
若离线标定，输入为本地视频，文件位于./data/video.mp4，棋盘格角点数为6×8，未输入参数保持默认值，则键入  
```
python intrinsicCalib.py -input video -path ./data/ -video video.mp4 -bw 6 -bh 8
```  
  
若离线标定，输入为本地图片，文件位于./data/下，图片命名为img_raw_xxx.xxx，棋盘格角点数为7×6，未输入参数保持默认值，则键入  
```
python intrinsicCalib.py -input image -path ./data/ -image img_raw -bw 7 -bh 6
```    
**脚本会将输入路径下所有包含该命名前缀的所有图片作为输入**  
读入示例提供的图片，可以看到标定结果和去畸变图像  
![inCalib_result.jpg](https://i.loli.net/2021/06/22/nxOsU1mM4D3kJWS.png)   
  
--------------------------------------------------------------------------------
  
#### 示例3 (手动模式)   
更改`-mode`为**auto**或**manual**切换自动或手动模式  
手动模式下：  
- 当相机输入时，每次按**空格键**捕获当前帧图像作为标定样本
- 当视频输入时，同上
- 当图像输入时，逐一读入图片，按**空格键**确认，其他键丢弃该图片
- 按**ESC**完成并退出标定  
输出界面会显示已捕获的有效图片数量  
例：
```
python intrinsicCalib.py -input image -mode manual -fw 1280 -fh 1024 -bw 7 -bh 6
```    
  
--------------------------------------------------------------------------------  
  
#### 示例4 (更多设置)     
`-fw` `-fh` `-fps` 设置相机的分辨率和帧率时，请**确认相机是否支持该设置**  
`-num` 为标定所需的最少图片数量（仅为初始化标定数量，仍然需要足够数量的有效图片才能得到较好结果），可以根据标定质量调整  
`-size` 为棋盘格边长，这个设置并不重要，不知道实际尺寸时，保持默认即可  
`-subpix` 为角点亚像素优化的搜索区域，根据分辨率和实际棋盘格尺寸调整，分辨率低或者棋盘格在图中较小时应适当调小该值  
`-delay` 配合自动模式下相机或视频输入，设置为x时，即为每隔x帧取样作为输入  
`-store` 当相机或视频输入时，设置为True可以将捕获的图像(检测到角点)储存在./data/路径下，可以利用**图像输入手动模式**再次挑选标定  
`-fs` `-ss` 为去畸变时的新的相机内参的焦距、尺寸缩放系数，可以用以调整视野  
`-crop` 在图像中央裁剪出(fw,fh)的大小作为输入，仅为备用设置，一般不使用  
`-resize` 将输入强制缩放至(fw,fh)大小，注意这样会改变相机内参，仅为备用设置，一般不使用  
  
例：
```
python intrinsicCalib.py  -fw 1280 -fh 720 -bw 6 -bh 8 -num 10 -delay 15 -store True -subpix 3 
```    
  
*对于部分更深入的细节设置可以修改代码*   
  
#### 常见问题  
- linux下推荐使用`cv2.VideoCapture(f"/dev/video{id}")`代替`cv2.VideoCapture(id)`读取相机图片  
- 若相机标定时，去畸变图像出现异常，此时可能计算发散，重投影误差很大，需要ESC退出重新标定，  
一般是由于前几张图像质量不好导致初始化错误而发散，请检查参数设置，保证标定板平直，    
并可以尝试修改`-num` `-delay` `subpix`等值，更换图片顺序等，或者重新采集图像  
- 鱼眼相机模型和普通相机模型不同，尤其是去畸变向量的表达不同，都有各自的opencv函数进行处理    
  
--------------------------------------------------------------------------------  
  
  
## Calibration Principle
> Reference: [OpenCV官方文档](https://docs.opencv.org/3.0.0/db/d58/group__calib3d__fisheye.html)、视觉SLAM十四讲

**鱼眼相机（单目）标定的目的是为了获取相机内参K和畸变系数D，根据这两个参数即可完成图像的去畸变处理**   

【坐标转换关系】：  
![2.png](https://i.loli.net/2021/04/07/4Nwzeag9EZTrDWl.png)

【刚体变换】世界坐标系Pw=(X,Y,Z)和相机坐标系Pc=(x,y,z)的变换可以通过旋转矩阵R和平移向量t实现:    
  
![1](http://latex.codecogs.com/svg.latex?\begin{bmatrix}{x}\\\\{y}\\\\{z}\\\\\end{bmatrix}=R\\cdot\\begin{bmatrix}{X}\\\\{Y}\\\\{Z}\\\\\end{bmatrix}+t)   

用变换矩阵**T=[R|t]** 表示相机的位姿，即：  

![2](http://latex.codecogs.com/svg.latex?\{P_c}=T{P_w})  

对坐标z进行归一化，得到归一化坐标并使用极坐标系r、θ进行表示：  
  
![3](http://latex.codecogs.com/svg.latex?\begin{cases}a=x\setminus{z}\\\\b=y\setminus{z}\\\\r^{2}=a^{2}+b^{2}\\\\\theta=atan(r)\\\\\end{cases})   
  
【去畸变】透镜形状引起的畸变分为径向畸变和切向畸变两种，可以用和距中心距离有关的二次及高次多项式函数进行纠正  
针对鱼眼相机的**畸变，使用k1,k2,k3,k4为系数的θ多项式进行描述，D=(k1,k2,k3,k4)** 即为标定结果之一：  
  
![4](http://latex.codecogs.com/svg.latex?\\theta_{d}=\theta(1+k_{1}\theta^{2}+k_{2}\theta^{4}+k_{3}\theta^{6}+k_{4}\theta^{8}))  
  
相机坐标系点经过去畸变后坐标如下转换，此时Pc=(x',y',1)：  
  
![5](http://latex.codecogs.com/svg.latex?\begin{cases}x^{'}=(\theta_{d}\setminus{r})x\\\\y^{'}=(\theta_{d}\setminus{r})y\\\\\end{cases})  

相机的内参矩阵K表示如下，**相机内参可以通过数学推导得到闭环解**，是标定结果之一：  
  
![6](http://latex.codecogs.com/svg.latex?K=\begin{bmatrix}{f_{x}}&{0}&{c_{x}}\\\\{0}&{f_{y}}&{c_{y}}\\\\{0}&{0}&{1}\\\\\end{bmatrix})  
  
【透视投影】根据相机模型可得像素坐标Puv和相机坐标Pc的关系：  
  
![7](http://latex.codecogs.com/svg.latex?\{P_u_v}=K{P_c}) 
  
经过投影后，最终的像素点坐标为：（其中skew参数α一般为0）  
  
![8](http://latex.codecogs.com/svg.latex?\begin{cases}u=f_{x}(x^{'}+\alpha{y^{'}})+c_{x}\\\\v=f_{y}y^{'}+c_{y}\\\\\end{cases})  
  
**标定过程**：
- 摄像头采集图像（有一定间隔）
- 寻找棋盘角点 (cv2.findChessboardCorners)，得到角点坐标
- 对角点坐标进行亚像素优化 (cv2.cornerSubPix)，参考[亚像素优化原理](https://xueyayang.github.io/pdf_posts/%E4%BA%9A%E5%83%8F%E7%B4%A0%E8%A7%92%E7%82%B9%E7%9A%84%E6%B1%82%E6%B3%95.pdf)
- 估计计算相机内参 (cv2.CALIB_USE_INTRINSIC_GUESS)，参考[张正友标定法原理](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.558.1926&rep=rep1&type=pdf)
- 得到标定结果 (cv2.fisheye.calibrate)，并根据新数据不断优化  
- 根据相机内参和畸变向量得到映射矩阵，计算无畸变和修正转换关系 (cv2.fisheye.initUndistortRectifyMap)
- 重映射实现图像的去畸变处理 (cv2.remap)
*注：具体函数细节可参照openCV官方文档或代码注释*

## Code Detailed Annotation
关于intrinsicCalib.ipynb的**中文详细代码注释**可以参见[intrinsicCalib.ipynb](https://nbviewer.jupyter.org/github/dyfcalid/CameraCalibration/blob/master/IntrinsicCalibration/intrinsicCalib.ipynb)  
  
`2021.6 ZZH`  

[回到顶部](#camera-calibration)

