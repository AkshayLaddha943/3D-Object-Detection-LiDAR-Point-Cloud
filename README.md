# 3D-Object-Detection-LiDAR-Point-Cloud
This repository contains the ROS2 workspace to evaluate the performance of PointPillars Architecture on a rosbag file recorded on a test vehicle equipped with a Velodyne VLP-32C. The rosbag is provided by RWTH Aachen University for evaluation.

## Methodology
For the project, PointPillars Architecture is inferenced for 3D Object Detection on LiDAR point clouds, assigning a bounding box and a class to every object in the input scene. I have used the pre-trained model from the repository which provides a Pytorch implementation of [PointPillars](https://github.com/zhulf0804/PointPillars) and modified it accordingly 

The file structure - 

**detector.py:** Implementation for pure Inertial Odometry (with an option to add bias and Gaussian noise)  
**config.py:** Implementation of Visual Odometry, evaluated using ORB-FLANN & Sparse LK Tracker  
**utils.py:** ESEKF-driven Visual & Inertial Fusion for Localization  

## PointPillars Architecture

<img width="1482" height="446" alt="image" src="https://github.com/user-attachments/assets/bc0c0da9-21e8-4b73-84a0-d816924d2350" />


## Results

https://github.com/user-attachments/assets/c26530ab-58e6-4dec-81bc-b196e184fa52
