import shutil
import os

# Copy existing burger.yaml
src = '/opt/ros/humble/share/turtlebot3_navigation2/param/burger.yaml'
dst = os.path.expanduser('~/falco_rover_ws/src/falco_rover_bringup/config/nav2_params.yaml')

shutil.copy(src, dst)

# Read it
with open(dst, 'r') as f:
    content = f.read()

# Add pointcloud to both observation_sources
pointcloud_addition = """
        pointcloud:
          topic: /depth_camera/points
          max_obstacle_height: 2.0
          clearing: True
          marking: True
          data_type: "PointCloud2"
          raytrace_max_range: 3.0
          obstacle_max_range: 2.5"""

# Replace observation_sources
content = content.replace(
    'observation_sources: scan',
    'observation_sources: scan pointcloud'
)

# Add pointcloud config after each scan config block
content = content.replace(
    'data_type: "LaserScan"\n      voxel_layer:',
    'data_type: "LaserScan"' + pointcloud_addition + '\n      voxel_layer:'
)

content = content.replace(
    'use_sim_time: False',
    'use_sim_time: True'
)

with open(dst, 'w') as f:
    f.write(content)

print("Done! nav2_params.yaml created with depth camera!")
