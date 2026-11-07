from sensor_msgs_py import point_cloud2
import numpy as np

def create_pillar(params, points: np.ndarray):
    x_pillar = np.floor((points[:, 0] - params.x_min) / params.delta_x).astype(np.int32)
    y_pillar = np.floor((points[:, 1] - params.y_min) / params.delta_y).astype(np.int32)

    xy_pillar = np.stack((x_pillar, y_pillar), axis=1)

    indices, inv = np.unique(xy_pillar, axis=0, return_inverse=True)

    order = np.argsort(inv, kind="stable")
    counts = np.bincount(inv, minlength=len(indices))

    pillars = np.split(points[order], np.cumsum(counts)[:-1])

    return pillars, indices
