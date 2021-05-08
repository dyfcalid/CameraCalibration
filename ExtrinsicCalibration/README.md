# Camera Extrinsic Calibration
> 相机外参标定
  
依赖库：opencv、numpy  

使用`extrinsicCalib.py`可以完成相机的**外参标定**，实现**任意两个视图（包含相同标定板）的转换**，生成**单应性变换矩阵**   
  
详细注释包含在`extrinsicCalib.ipynb`中，也可以在Jupyter Notebook中直接运行该代码   
## Background

基于**无人机相机**和**车载环视相机**同时拍摄地面的标定板，进行车载相机的**外参标定**，  
生成车载相机至无人机相机的**单应性变换矩阵**，实现**鸟瞰图**的转换（即将车载相机视角转换至无人机视角）  

## Work Flow    
- 将标定板放置在地面上  
- 由两个固定的不同位置、视角的相机（车载相机和无人机相机）进行拍摄（确保标定板完整）  
- 每次移动标定板得到一组对应图像，重复多次  
- 根据相机各自的内参标定进行图片的去畸变预处理  
- 两个相机的对应图像分别为源图像(img_src)和目标图像(img_dst)  
- 用extrinsicCalib.py生成单应性矩阵，实现转换    
- 无人机尽可能保持不动，依次完成车上各相机的标定（程序可以对图像进行平移和缩放以减小误差） 
  
## Quick Start
### extrinsicCalib.py 
> 相机外参标定  
  
请务必确保输入的**源图像**和**目标图像**已经完成内参标定和**去畸变处理**（参考`intrinsicCalib.py`）  
同时源图像和目标图像的**顺序一一对应**   
```
python extrinsicCalib.py
```
可以通过argparse输入更多参数，使用`-h`或`--help` 查看所有参数信息，请**注意各参数的默认值**
```
python extrinsicCalib.py -h
```

| Argument  | Type | Default   | Help                                              | 
|:----------|:----:|:---------:|:--------------------------------------------------|
| -id       | int  | 1         | Camera ID                                         |
| -path     | str  | ./data/   | Input Video/Image Path                            |
| -fw       | int  | 1280      | Camera Frame Width                                |
| -fh       | int  | 720       | Camera Frame Height                               |
| -bw       | int  | 9         | Chess Board Width (corners number)                |
| -bh       | int  | 6         | Chess Board Height (corners number)               |
| -src      | str  | img_src   | Source Image File Name Prefix (eg.: img_src)      |
| -dst      | str  | img_dst   | Destionation Image File Name Prefix (eg.: img_dst)|
| -size     | int  | 15        | Scaled Chess Board Square Size (image pixel)      |
| -center   | bool | True      | Center Image Manually (Ture/False)                |
| -scale    | bool | True      | Scale Image to Fix Board Size (Ture/False)        |
| -store    | bool | False     | Store Centerd/Scaled Images (Ture/False)          |
   
-----------------------------------------------------------------------------------  
  
程序会将`-path`下的所有包含`-src`和`-dst`内容的图片都读入，按照顺序一一进行转换  
当`-center`和`-scale`都设置为True时，会对目标图像即img_dst进行图像居中和缩放  
  
图像居中时：  
- 可以直接**点击**车辆中心  
- 或者**按住鼠标左键**画**矩形框**框住车辆，自动返回中心点  
- 显示中心点坐标以及(y/n)选项，按y键完成居中，按n键重新选择  
- 确认后会显示居中的图像，ESC关闭  
  
图像缩放时：  
- 程序会首先对目标图像img_dst中提取角点坐标，并计算棋盘的小格子平均尺寸  
- 根据设置的`-size`值（即为最终标定板棋盘格在图中的像素长度，注意此参数与intrinsicCalib.py含义不同）  
计算缩放系数对图像进行缩放，保证所有目标图像的标定板在图中的像素尺寸一致（即无人机的高度一致） 
- 对缩放后的图像进行裁剪或边沿填充  
- 显示缩放后的图像，ESC关闭  
  
每读入一组图像，程序就会进行一次单应性矩阵计算（总数据量不断累加），并显示变换的效果图   

  
`2021.5 ZZH`  

  
  
