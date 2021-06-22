from .extrinsicCalib import ExCalibrator

"""
Extrinsic Calibration

Instructions:
    from extrinsicCalib import ExCalibrator

    exCalib = ExCalibrator()
    homography = exCalib(src_raw, dst_raw)
    src_warp = exCalib.warp()
    
You can edit parameters in the original file, or
    args = ExCalibrator.get_args()
    args.INPUT_PATH = './ExtrinsicCalibration/data/'
    exCalib = ExCalibrator()
"""

