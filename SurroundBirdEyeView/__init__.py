from .surroundBEV import BevGenerator

"""
Surround Camera Bird Eye View Generator

Instructions:
    from surroundBEV import BevGenerator

    bev = BevGenerator()
    surround = bev(front,back,left,right)  # for real-time use
or
    bev = BevGenerator(blend=True, balance=True)
    surround = bev(front,back,left,right,car)
    
You can edit parameters in the original file, or
    args = BevGenerator.get_args()
    args.CAR_WIDTH = 200
    args.CAR_HEIGHT = 350
    bev = BevGenerator()
"""