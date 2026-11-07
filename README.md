# 3D-Object-Detection-LiDAR-Point-Cloud
This repository contains the ROS2 workspace to evaluate the performance of PointPillars Architecture on a rosbag file recorded on a test vehicle equipped with a Velodyne VLP-32C. The rosbag is provided by RWTH Aachen University for evaluation.

## Methodology
For the project, PointPillars Architecture is inferenced for 3D Object Detection on LiDAR point clouds, assigning a bounding box and a class to every object in the input scene. I have used the pre-trained model from the repository which provides a Pytorch implementation of [PointPillars](https://github.com/zhulf0804/PointPillars) and modified it accordingly 

The file structure - 

**detector.py:** Main script, that subscribes to the pointcloud topic, preprocesses, performs inference and publishes results
**config.py:** Contains all the parameters that can be tuned to modify and achieve the desired results
**utils.py:** To create vertical pillars from raw point cloud data

Since, the PointPillars repository already contains method to create vertical pillars, we comment out this block

Steps:

- Clone the Repository [PointPillars](https://github.com/zhulf0804/PointPillars) inside the _ws/src folder
- Create a venv and install the requirements.txt file
- Store the pretrained model .pth file inside models folder

## PointPillars Architecture

<img width="1482" height="446" alt="image" src="https://github.com/user-attachments/assets/bc0c0da9-21e8-4b73-84a0-d816924d2350" />


## Results

https://github.com/user-attachments/assets/da387856-2adb-46e4-8f6f-76dac4fb31cc



