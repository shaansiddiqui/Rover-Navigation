# 🤖 Falco Rover | GPS-Denied Autonomous Navigation using ROS2, SLAM & Depth Camera Fusion

> GPS-denied autonomous navigation using ROS2 Humble, Gazebo, Nav2, SLAM, EKF, and multi-sensor fusion.

![ROS2](https://img.shields.io/badge/ROS2-Humble-blue)
![Gazebo](https://img.shields.io/badge/Gazebo-Classic-orange)
![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04-purple)
![License](https://img.shields.io/badge/License-Apache%202.0-green)

---

## 📌 Overview

The **Falco Rover** is a fully autonomous ground robot that navigates inside closed, GPS-denied indoor environments using only onboard sensors. It requires **no GPS** and **no continuous user input** — just one initial pose estimate and one navigation goal.

**Key features:**
- 360° LiDAR-based SLAM mapping and AMCL localisation
- Intel RealSense D435 depth camera integrated into Nav2 obstacle layer via `pointcloud_to_laserscan`
- EKF sensor fusion (IMU + odometry)
- A* global path planning + DWB local obstacle avoidance
- Autonomous recovery behaviours (spin, backup, wait)
- Custom voice announcements via espeak
- Custom LED status indicator (GREEN/YELLOW/RED) via RViz markers

---

## 🏗️ System Architecture

```
RP LiDAR A1M8  ──→  /scan  ──→  AMCL (localisation)
                              └──→  costmap_2d (obstacle layer)

RealSense D435 ──→  /depth_camera/points
                              └──→  pointcloud_to_laserscan
                                          └──→  /depth_camera/scan ──→  costmap_2d

IMU (MPU6050)  ──→  /imu  ──→  ekf_filter_node
Wheel Odom     ──→  /odom ──→  ekf_filter_node
                              └──→  /odometry/filtered ──→  Nav2

Nav2 Stack: map_server → planner_server (A*) → controller_server (DWB) → /cmd_vel → motors
```

---

## 🧰 Hardware (Simulated)

| Component | Model | ROS2 Topic |
|---|---|---|
| LiDAR | RP LiDAR A1M8 | `/scan` |
| Depth Camera | Intel RealSense D435 | `/depth_camera/points` |
| IMU | MPU-6050 | `/imu` |
| Motors | Differential Drive | `/cmd_vel`, `/odom` |
| Compute | RPi (simulated by CPU) | — |
| Voice | espeak | — |
| LED | RViz Marker | `/indicator/status_marker` |

---

## 🛠️ Software Stack

| Package | Role |
|---|---|
| ROS2 Humble | Robot middleware |
| Gazebo Classic | Physics simulation |
| SLAM Toolbox | Environment mapping |
| AMCL | Probabilistic localisation |
| Nav2 | Path planning + obstacle avoidance |
| robot_localization (EKF) | IMU + odometry fusion |
| pointcloud_to_laserscan | Depth camera → 2D scan |
| voice_commander.py | Custom voice feedback node |
| indicator.py | Custom LED status node |

---

## 📁 Repository Structure

```
falco-rover/
├── falco_rover_bringup/          # Main ROS2 package
│   ├── config/
│   │   ├── ekf.yaml              # EKF sensor fusion config
│   │   ├── nav2_params.yaml      # Nav2 tuned parameters
│   │   └── pointcloud_to_laserscan.yaml
│   ├── launch/
│   │   └── falco_navigation.launch.py   # Master launch file
│   ├── urdf/
│   │   └── falco_rover.urdf      # Custom robot model
│   ├── falco_rover_bringup/
│   │   ├── voice_commander.py    # Custom voice node
│   │   └── indicator.py          # Custom LED node
│   ├── package.xml
│   └── setup.py
└── README.md
```

---

## ⚙️ Prerequisites

```bash
# ROS2 Humble
sudo apt install ros-humble-desktop

# Nav2
sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup

# TurtleBot3
sudo apt install ros-humble-turtlebot3 ros-humble-turtlebot3-gazebo ros-humble-turtlebot3-navigation2

# EKF
sudo apt install ros-humble-robot-localization

# Pointcloud to LaserScan
sudo apt install ros-humble-pointcloud-to-laserscan

# espeak
sudo apt install espeak
```

---

## 🚀 Installation

```bash
# Create workspace
mkdir -p ~/falco_rover_ws/src
cd ~/falco_rover_ws/src

# Clone this repo
git clone https://github.com/YOUR_USERNAME/falco-rover.git falco_rover_bringup

# Build
cd ~/falco_rover_ws
colcon build --symlink-install
source install/setup.bash
```

---

## 🗺️ Phase 1 — Mapping (Run Once)

```bash
# Terminal 1 — Launch Gazebo
cd ~/falco_rover_ws
source install/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

# Terminal 2 — Launch SLAM
ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True

# Terminal 3 — Drive robot around to build map
ros2 run turtlebot3_teleop teleop_keyboard

# Terminal 4 — Save map when done
ros2 run nav2_map_server map_saver_cli -f ~/my_map
```

---

## 🤖 Phase 2 — Autonomous Navigation

```bash
cd ~/falco_rover_ws
source install/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
ros2 launch falco_rover_bringup falco_navigation.launch.py
```

Then in RViz:
1. Click **2D Pose Estimate** → click on map where robot is
2. Click **Nav2 Goal** → click anywhere on the map
3. Robot navigates fully autonomously

---

## 🔍 Verify Sensors

```bash
# Check all sensor topics publishing
timeout 5 ros2 topic hz /scan
timeout 5 ros2 topic hz /imu
timeout 5 ros2 topic hz /depth_camera/points
timeout 5 ros2 topic hz /depth_camera/scan

# Check all nodes running
ros2 node list

# View TF tree
ros2 run tf2_tools view_frames

# View node graph
ros2 run rqt_graph rqt_graph
```

---

## 🧠 Navigation Algorithm

The system follows an 8-step autonomous navigation pipeline:

1. **EKF Fusion** — IMU + odometry → `/odometry/filtered`
2. **Depth Camera Integration** — PointCloud2 → 2D LaserScan via `pointcloud_to_laserscan`
3. **AMCL Localisation** — LiDAR scan matched against saved map → `/amcl_pose`
4. **Costmap Construction** — dual sources: `/scan` + `/depth_camera/scan`
5. **Global Planning (A\*)** — optimal path from current pose to goal
6. **Local Avoidance (DWB)** — real-time obstacle avoidance at 10 Hz
7. **Recovery Behaviours** — spin → backup → wait if stuck
8. **Goal Notification** — voice announcement + LED GREEN on arrival

---

## 📊 Sensor Specifications

### RP LiDAR A1M8
| Spec | Value |
|---|---|
| Range | 0.15m – 12m |
| Scan Rate | 5.5 Hz (4.87 Hz in simulation) |
| Angular Resolution | 1° (360 samples) |
| FOV | 360° |
| Interface | UART/USB |

### Intel RealSense D435
| Spec | Value |
|---|---|
| Depth Range | 0.1m – 10m |
| Resolution | 640×480 @ 30fps |
| Horizontal FOV | 87° |
| Interface | USB 3.1 |

### IMU (MPU-6050)
| Spec | Value |
|---|---|
| Update Rate | 100 Hz (93 Hz in simulation) |
| Gyro Range | ±2000 °/s |
| Accel Range | ±16g |
| Interface | I2C/SPI |

---

## 🎯 Custom Contributions

### 1. `falco_rover.urdf`
Extended TurtleBot3 Waffle Pi with:
- `depth_camera_link` at correct mounting position
- Gazebo depth camera plugin (libgazebo_ros_camera.so)
- LiDAR, IMU, and differential drive Gazebo plugins

### 2. `falco_navigation.launch.py`
Single command launches entire system:
- Gazebo + robot spawning
- Nav2 with custom params
- EKF sensor fusion
- pointcloud_to_laserscan
- voice_commander
- indicator_node

### 3. `voice_commander.py`
Custom ROS2 node — espeak announcements on navigation events.

### 4. `indicator.py`
Custom ROS2 node — RViz LED marker (GREEN/YELLOW/RED) based on nav status.

### 5. Depth Camera → Nav2 Integration
`pointcloud_to_laserscan` converts `/depth_camera/points` → `/depth_camera/scan`, fed into both local and global costmaps as a second obstacle source.

---

## 📹 Demo Video

[Watch simulation video](https://youtu.be/H4JcajxRSFE)

---

## 📄 Report

Full technical report available in [`/report`](./report/Falco_Rover_Navigation_Report.pdf)

---

## 📝 License

Apache License 2.0
