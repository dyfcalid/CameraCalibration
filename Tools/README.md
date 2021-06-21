# Tools  
> 标定过程可能会用到的一些小工具
  
  
## collect.py    
> 控制usb相机采集图像或视频  
  
```
python collect.py
```
可以通过argparse输入更多参数，使用 '-h' 查看所有参数信息  
```
python collect.py -h
```
| Argument   | Type | Default   | Help                                             | 
|:-----------|:----:|:---------:|:-------------------------------------------------|
| -type      | str  | image     | Collect Data Type: image/video                   |
| -id        | int  | 1         | Camera ID                                        |
| -path      | str  | ./data/   | Input Video/Image Path                           |
| -name      | str  | test      | Save Video/Image Name                            |
| -fw        | int  | 1280      | Camera Frame Width                               |
| -fh        | int  | 720       | Camera Frame Height                              |
| -fps       | int  | 25        | Camera Frame per Second (FPS)                    |
  
`-type` 为image时，按下**空格键** 采集图片，此时显示该图像，按**Y**确认，按**N**则丢弃，可以多次采集  
`-type` 为video时，按下**空格键** 开始录制视频，再次按下空格键时停止录制，可以多次录制  
   
**示例**： 采集1号相机1280*1024的图像，则运行
```
python collect.py -type image -id 1 -fw 1280 -fh 1024
```
linux下推荐使用`cv2.VideoCapture(f"/dev/video{id}")`代替`cv2.VideoCapture(id)`读取相机图片  
  
--------------------------------------------------------------------------------  
  
## undistort.py  
> 根据相机内参和畸变向量对原始图像进行去畸变操作  
  
将需要处理的原始图片、标定生成的结果数据(`camera_K.npy`和`camera_D.npy`)放在data文件夹下，或者自行输入相应的路径参数，
在命令行中运行即可
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
| -height    | int   | 1024    | Camera Frame Height                               |
| -load      | bool  | True    | Load New Camera K/D Data (True/False)             |
| -path_read | str   | ./data/ | Original Image Read Path                          |
| -path_save | str   | ./      | Undistortion Image Save Path                      |
| -path_k    | str   | ./data/camera_0_K.npy | Camera K File Path                  |
| -path_d    | str   | ./data/camera_0_D.npy | Camera D File Path                  |
| -focalscale| float | 1       | Camera Undistortion Focal Scale                   |
| -sizescale | float | 1       | Camera Undistortion Size Scale                    |
| -offset_h  | float | 0       | Horizonal Offset of Height                        |
| -offset_v  | float | 0       | Vertical Offset of Height                         |
| -srcformat | str   | jpg     | Source Image Format (jpg/png)                     |
| -dstformat | str   | jpg     | Destination Image Format (jpg/png)                |
| -quality   | int   | 100     | Save Image Quality (jpg:0-100, png:9-0 (low-high))|
| -name      | str   | None    | Save Image Name                                   |

**示例**： 若要对数张`png`原始数据进行处理，加载`新的标定数据`，得到`1280×720`大小的去畸变图像，  
命名为`undist_img`，以`jpg`格式存储，`存储质量设为95`，其他保持默认，则运行以下命令即可
```
 python undistort.py -width 1280 -height 720 -load True -srcformat png -dstformat jpg -name undist_img -quality 95
```
该脚本文件路径下所有符合`-srcformat`格式的图片均会进行去畸变处理并生成新图片
如果只对单张特定图片进行去畸变操作，可以修改代码（已在代码中注释）
  
--------------------------------------------------------------------------------  
  
## decomposeH.py   
> 可以由单应性矩阵H和相机内参K得到旋转矩阵R和平移矩阵T（有多个结果需要筛选）  
  
  
## timeAlign.py   
> 可以将以时间戳命名的图片按时间对准，得到对应的列表  
  
  
## img2vid.py   
> 可以将连续的图片转化为视频  
  