# Surround Camera Bird Eye View Generator
> 生成车载环视相机拼接鸟瞰图  
  

## surroundBEV.py
输入**前后左右**四张原始相机图像，生成**鸟瞰图**
包括**直接拼接和融合拼接**，并可以进行**亮度平衡和白平衡**
  
将四个相机的K、D、H参数文件以及原始相机图片分别存在data下的四个文件里（如默认文件所示）  
在命令行中运行 
```
python surroundBEV.py
```
可以通过argparse输入更多参数，使用`-h`或`--help` 查看所有参数信息，请**注意各参数的默认值**
```
python surroundBEV.py -h
```
| Argument   | Type | Default   | Help                                             | 备注                    |
|:-----------|:----:|:---------:|:-------------------------------------------------|:----------------------- |
| -fw        | int  | 1280      | Camera Frame Width                               | 相机原始图像宽度        |
| -fh        | int  | 1024      | Camera Frame Height                              | 相机原始图像高度        |
| -bw        | int  | 1000      | Chess Board Width (corners number)               | 最终鸟瞰图宽度          |
| -bh        | int  | 1000      | Chess Board Height (corners number)              | 最终鸟瞰图宽度          |
| -cw        | int  | 250       | Camera Frame Width                               | 车辆图片宽度            |
| -ch        | int  | 400       | Camera Frame Height                              | 车辆图片高度            |
| -fs        | float| 1         | Camera Undistort Focal Scale                     | 去畸变时的焦距缩放系数  |
| -ss        | float| 2         | Camera Undistort Size Scale                      | 去畸变时的尺寸缩放系数  |
| -blend  | bool  | False   | Blend BEV Image (Ture/False)                    | 鸟瞰图拼接是否采用图像融合  |
| -balance| bool | False   | Balance BEV Image (Ture/False)                 | 鸟瞰图拼接是否采用图像平衡  |

**注意**：上述参数设置及对应文件**仅针对于示例**的环视图像拼接，若要用于自己的相机等，请依次完成**内外参标定**各步骤，得到对应文件进行替换  
**请确保这里的所有参数设置都与内外参标定和去畸变时一致！**  (尤其是去畸变系数)  
车辆图片可以自行更换，调整为合适的尺寸大小并同步更改args中的参数`-cw` `-ch`   
  
通过设置`-blend`和`-balance`参数为(True/False)可以启用图像融合和图像亮度色彩平衡操作，  
或者在初始化BevGenerator类时，直接传入参数，如
```
bev = BevGenerator(blend=True, balance=True)
```

对于实时环视鸟瞰图生成，推荐调用**BevGenerator类**实现，实时读入前后左右四个相机图像并传入函数得到鸟瞰图
```
from surroundBEV import BevGenerator

bev = BevGenerator()                                # 初始化环视鸟瞰生成器
surround = bev(front,back,left,right)               # 输入前后左右四张原始相机图像 得到拼接后的鸟瞰图
```
  
------------------------------------------------------------------------------------------------------  
  
拼接时使用**预设的MASK**，根据中间车辆图片的尺寸计算  
直接拼接时，取车辆图片四个角与鸟瞰图四个角连线得到对应的mask,  
融合拼接时，则取更大的区域使得各mask之间有重叠部分，在重叠区域内根据距离两个mask的距离计算权重  
如下图所示（以前视图mask为例）：  
![mask.jpg](https://i.loli.net/2021/06/22/Sm6wlYzqTxZahpg.png)
  
**拼接结果**：  
![surround.jpg](https://i.loli.net/2021/06/22/2JRw31FszrDgxZK.png)  

`2021.6 ZZH`  
  
