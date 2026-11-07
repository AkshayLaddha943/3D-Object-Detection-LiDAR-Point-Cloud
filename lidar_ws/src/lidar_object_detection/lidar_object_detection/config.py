import numpy as np


class GridParameters:
    x_min = 0.0
    x_max = 69.12
    delta_x = 0.16

    y_min = -39.68
    y_max = 39.68
    delta_y = 0.16

    z_min = -3
    z_max = 1
    delta_z = 4

    def __init__(self):
        super(GridParameters, self).__init__()


# class DataParameters:

#     classes = {"Car":               0,
#                "Pedestrian":        1,
#                "Person_sitting":    1,
#                "Cyclist":           2,
#                "Truck":             3,
#                "Van":               3,
#                "Tram":              3,
#                "Misc":              3,
#                }

#     nb_classes = len(np.unique(list(classes.values())))
#     assert nb_classes == np.max(np.unique(list(classes.values()))) + 1, 'Starting class indexing at zero.'

#     def __init__(self):
#         super(DataParameters, self).__init__()


class NetworkParameters:

    normalize_intensity = True
    intensity_scale = 255.0

    max_points_per_pillar = 32
    max_pillars = 12000
    nb_features = 9
    nb_channels = 64
    downscaling_factor = 2

    classes = {0: "Pedestrian", 1: "Cyclist", 2: "Car"}

    nb_classes = 3

    score_threshold = 0.55
    nms_threshold = 0.01
    nms_pre = 100
    max_detections = 50

    # Output bounding-box range
    bbox_range = [0, -40, -3, 70.4, 40, 0.0]

    # # length, width, height, z-center, orientation
    # anchor_dims = np.array([[3.9, 1.6, 1.56, -1, 0],
    #                         [3.9, 1.6, 1.56, -1, 1.5708],
    #                         [0.8, 0.6, 1.73, -0.6, 0],
    #                         [0.8, 0.6, 1.73, -0.6, 1.5708],
    #                         ], dtype=np.float32).tolist()
    # nb_dims = 3

    # positive_iou_threshold = 0.40
    # negative_iou_threshold = 0.25
    # learning_rate = 1e-3
    # decay_rate = 1e-8
    # alpha = 0.25
    # gamma = 4.0

    # focal_weight = 1000.0      
    # loc_weight = 2.0        
    # size_weight = 2.0       
    # angle_weight = 0.5      
    # heading_weight = 0.2    
    # class_weight = 0.2      

    def __init__(self):
        super(NetworkParameters, self).__init__()


class Parameters(GridParameters, NetworkParameters):

    def __init__(self):
        super(Parameters, self).__init__()