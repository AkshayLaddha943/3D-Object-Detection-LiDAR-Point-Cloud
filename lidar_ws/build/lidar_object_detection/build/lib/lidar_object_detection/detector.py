import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2
from vision_msgs.msg import (
    BoundingBox3D,
    Detection3DArray,
    Detection3D,
    ObjectHypothesisWithPose
)
from visualization_msgs.msg import Marker, MarkerArray

import torch
import numpy as np
import math

from .utils import create_pillar
from .config import Parameters
import time

from pointpillars.model.pointpillars import PointPillars

lidar_qos = QoSProfile(history=HistoryPolicy.KEEP_LAST, depth=1, reliability=ReliabilityPolicy.BEST_EFFORT)

class LidarDetection(Node):
    def __init__(self,):
        super().__init__('lidar_detector')

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.ptcloud_topic = "/points2"
        self.ckpt_path = "/home/akshladdhs/Point_Cloud_Object_Detection/lidar_ws/src/lidar_object_detection/models/epoch_160.pth"

        self.model = PointPillars(nclasses=3)

        self.lidar_sub = self.create_subscription(PointCloud2, self.ptcloud_topic, self.lidar_callback, lidar_qos)
        self.bbox_pub = self.create_publisher(Detection3DArray, "/output/bbox", 10)
        self.marker_pub = self.create_publisher(MarkerArray, "/output/markers", 10)

        #load pytorch model
        checkpoint = torch.load(self.ckpt_path, map_location=self.device, weights_only=True)

        self.model.load_state_dict(checkpoint)
        self.model = self.model.to(self.device)
        self.model.eval()

    def preprocess(self, msg: PointCloud2):
        # pc2_data = point_cloud2.read_points_list(msg, field_names=["x", "y", "z", "intensity"], skip_nans=True)
        # points = np.asarray(pc2_data, dtype=np.float32)

        points = point_cloud2.read_points_numpy(msg, field_names=["x", "y", "z", "intensity"], skip_nans=True)
        points = points.astype(np.float32, copy=False)

        #range based filtering
        mask = (
            (points[:, 0] >= Parameters.x_min) & 
            (points[:, 0] < Parameters.x_max) &
            (points[:, 1] >= Parameters.y_min) &
            (points[:, 1] < Parameters.y_max) &
            (points[:, 2] >= Parameters.z_min) &
            (points[:, 2] < Parameters.z_max)
        )

        filtered_points = points[mask]

        if len(filtered_points) == 0:
            return None

        if Parameters.normalize_intensity:
            filtered_points[:, 3] = (filtered_points[:, 3] / Parameters.intensity_scale)

        #generate pillars
        # pillars, indices = create_pillar(Parameters, filtered_points)

        # #padding
        # num_pillars = len(pillars)

        # pillars = pillars[:Parameters.max_pillars]
        # indices = indices[:Parameters.max_pillars]

        # padded_pillars = np.zeros((num_pillars, Parameters.max_points_per_pillar, 4), dtype=np.float32)

        # num_points = np.zeros(num_pillars, dtype=np.int32)
        
        # for i, pillar in enumerate(pillars):
        #     n = min(len(pillar), Parameters.max_points_per_pillar)
        #     padded_pillars[i, :n, :] = pillar[:n]
        #     num_points[i] = n

        # pillar_tensor = torch.from_numpy(padded_pillars)
        # indices_tensor = torch.from_numpy(indices.astype(np.int32))
        # num_points_tensor = torch.from_numpy(num_points)

        # return pillar_tensor, indices_tensor, num_points_tensor
        return filtered_points

    def lidar_callback(self, msg: PointCloud2):
        start_time = time.perf_counter()

        filtered_points = self.preprocess(msg)

        if filtered_points is None:
            self.publish_bbox([], [], [], msg.header)
            return

        preprocess_end = time.perf_counter()

        filtered_tensor = torch.from_numpy(filtered_points).float().to(self.device)

        with torch.inference_mode():
            result_filter = self.model(batched_pts=[filtered_tensor], mode="test")[0]

        if self.device.type == "cuda":
            torch.cuda.synchronize()

        inference_end = time.perf_counter()

        if isinstance(result_filter, dict):
            lidar_bbox, labels, scores = result_filter['lidar_bboxes'], result_filter['labels'], result_filter['scores']
            mask = scores >= Parameters.score_threshold

            lidar_bbox = lidar_bbox[mask]
            labels = labels[mask]
            scores = scores[mask]

            self.get_logger().info(f"Detected {len(lidar_bbox)} objects")
            self.publish_bbox(lidar_bbox, labels, scores, msg.header)
        elif (
            isinstance(result_filter, tuple)
            and len(result_filter) == 3
            and all(len(item) == 0 for item in result_filter)
        ):
            self.get_logger().info("No objects detected")
            self.publish_bbox([], [], [], msg.header)

        else:
            self.get_logger().error(f"Unexpected model output: {type(result_filter)}")

        total_end = time.perf_counter()

        self.get_logger().info(
        f"Preprocessing: {(preprocess_end-start_time)*1000:.2f} ms | "
        f"Inference: {(inference_end-preprocess_end)*1000:.2f} ms | "
        f"Total: {(total_end-start_time)*1000:.2f} ms"
    )

    def publish_bbox(self, bbox, label, scores, header):
        Detection_Array = Detection3DArray()
        Detection_Array.header = header

        for box, labels, score in zip(bbox, label, scores):
            x, y, z, w, l, h, yaw = box

            detection = Detection3D()
            detection.header = header

            bbox_msg = BoundingBox3D()
            bbox_msg.center.position.x = float(x)
            bbox_msg.center.position.y = float(y)
            bbox_msg.center.position.z = float(z)

            bbox_msg.size.x = float(w)
            bbox_msg.size.y = float(l)
            bbox_msg.size.z = float(h)

            bbox_msg.center.orientation.x = 0.0
            bbox_msg.center.orientation.y = 0.0
            bbox_msg.center.orientation.z = math.sin(float(yaw) / 2.0)
            bbox_msg.center.orientation.w = math.cos(float(yaw) / 2.0)

            detection.bbox = bbox_msg

            #classification
            hypothesis = ObjectHypothesisWithPose()

            hypothesis.hypothesis.class_id = Parameters.classes.get(int(labels), "Unknown")
            hypothesis.hypothesis.score = float(score)
            hypothesis.pose.pose = bbox_msg.center

            detection.results.append(hypothesis)
            Detection_Array.detections.append(detection)

        self.bbox_pub.publish(Detection_Array)
        self.publish_markers(Detection_Array)

    def publish_markers(self, detect: Detection3DArray):
        marker_array = MarkerArray()

        clear_marker = Marker()
        clear_marker.header = detect.header
        clear_marker.action = Marker.DELETEALL

        marker_array.markers.append(clear_marker)

        for i, detection in enumerate(detect.detections):
            marker = Marker()
            marker.header = detect.header

            marker.ns = "pointpillars"
            marker.id = i

            marker.type = Marker.CUBE
            marker.color.a = 0.3
            marker.action = Marker.ADD

            # Bounding box center and orientation
            marker.pose = detection.bbox.center

            # Bounding box dimensions
            marker.scale.x = detection.bbox.size.x
            marker.scale.y = detection.bbox.size.y
            marker.scale.z = detection.bbox.size.z

            # Visualization color
            marker.color.r = 0.0
            marker.color.g = 1.0
            marker.color.b = 0.0
            marker.color.a = 0.3

            marker_array.markers.append(marker)

        self.marker_pub.publish(marker_array)

def main(args=None):
    rclpy.init(args=args)
    node = LidarDetection()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
        