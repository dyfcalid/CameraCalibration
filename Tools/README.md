
  
### undistort.py
> 根据相机内参和畸变向量对原始图像进行去畸变操作  

# Tools  
> 标定过程可能会用到的一些小工具

## undistort.py  
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