from .extrinsicCalib import ExCalibrator

"""
Extrinsic Calibration

Instructions:
    from extrinsicCalib import ExCalibrator

    exCalib = ExCalibrator()
    homography = exCalib(src_raw, dst_raw)
    src_warp = exCalib.warp()
"""
