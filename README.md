# Camera Calibration
> 集合了相机标定相关的多个脚本工具  

## File Tree  
> 项目结构预览  
```
CameraCalibration  
│  homography.py             // 单应性变换
│  undistort.py              // 图像去畸变
│  README.md                 // 总目录文档
│    
├─ExtrinsicCalibration  
│  │  extrinsicCalib.ipynb   // 外参标定代码（含注释）
│  │  extrinsicCalib.py      // 外参标定脚本
│  │  README.md              // 外参标定文档
│  │    
│  └─data                    // 外参标定数据文件夹
└─IntrinsicCalibration  
    │  intrinsicCalib.ipynb  // 内参标定代码（含注释）
    │  intrinsicCalib.py     // 内参标定脚本
    │  Readme.md             // 内参标定文档
    │    
    └─data                   // 内参标定数据文件夹
```  
  
## Camera Intrinsic Calibration [已完成]
> 相机内参标定   

包括相机的**在线标定**和**离线标定**，包含**鱼眼相机**和普通相机模型，  
并支持**相机、视频、图像**三种输入，生成相机内参和畸变向量   
  
## Camera Extrinsic Calibration
> 相机外参标定   

基于**无人机**拍摄，实现车载相机的外参标定，生成车载相机至无人机相机的**单应性变换矩阵**，实现**鸟瞰图**的转换  
  
## Surround View Image Stitching / BEV
施工中...  
  
## Other Tools  
用`undistort.py`可以批量完成图像的**去畸变处理**   
用`homography.py`可以批量完成图像的**单应性变换**，得到鸟瞰图  
   
    
`2021.5 ZZH`  