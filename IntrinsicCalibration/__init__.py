from .intrinsicCalib import InCalibrator, CalibMode

"""
Intrinsic Calibration

Instructions:
    from intrinsicCalib import InCalibrator
    
    calibrator = InCalibrator(camera_type)
    for img in images:
        result = calibrator(img)
or
    from intrinsicCalib import InCalibrator, CalibMode

    calibrator = InCalibrator(camera_type)
    calib = CalibMode(calibrator, input_type, mode)
    result = calib()
    
You can edit parameters in the original file, or
    args = InCalibrator.get_args()
    args.INPUT_PATH = './IntrinsicCalibration/data/'
    calibrator = InCalibrator(camera_type)
"""
