from .intrinsicCalib import InCalibrator, CalibMode
from .intrinsicCalib import getInCalibArgs, editInCalibArgs

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
    
you can edit parameters in the original file, or

    from intrinsicCalib import getInCalibArgs, editInCalibArgs
    
    InCalibArgs = getInCalibArgs()
    InCalibArgs.INPUT_PATH = './IntrinsicCalibration/data/'
    editInCalibArgs(InCalibArgs)
"""
