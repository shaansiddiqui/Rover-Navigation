import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    nav2_params = os.path.join(
        get_package_share_directory('falco_rover_bringup'),
        'config', 'nav2_params.yaml'
    )

    urdf_file = os.path.join(
        get_package_share_directory('falco_rover_bringup'),
        'urdf', 'falco_rover.urdf'
    )

    with open(urdf_file, 'r') as f:
        robot_description = f.read()

    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    world = os.path.join(
        get_package_share_directory('turtlebot3_gazebo'),
        'worlds', 'turtlebot3_world.world'
    )

    # Gazebo server
    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': world}.items()
    )

    # Gazebo client (GUI)
    gzclient = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
        )
    )

    # Our custom robot state publisher with depth camera URDF
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True
        }]
    )

    # Spawn our custom robot in Gazebo
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'falco_rover',
            '-topic', 'robot_description',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.01'
        ],
        output='screen'
    )

    # Nav2
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('turtlebot3_navigation2'),
                        'launch', 'navigation2.launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'true',
            'map': '/home/shaan/my_map.yaml',
            'params_file': nav2_params
        }.items()
    )

    # EKF Sensor Fusion
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[
            '/home/shaan/falco_rover_ws/src/falco_rover_bringup/config/ekf.yaml',
            {'use_sim_time': True}
        ]
    )

    # Pointcloud to LaserScan (depth camera → Nav2 obstacle layer)
    pointcloud_node = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pointcloud_to_laserscan_node',
        remappings=[
            ('cloud_in', '/depth_camera/points'),
            ('scan', '/depth_camera/scan'),
        ],
        parameters=[
            os.path.join(
                get_package_share_directory('falco_rover_bringup'),
                'config', 'pointcloud_to_laserscan.yaml'
            )
        ]
    )

    # Voice Commander
    voice_node = Node(
        package='falco_rover_bringup',
        executable='voice_commander',
        name='voice_commander',
        output='screen'
    )

    # Indicator
    indicator_node = Node(
        package='falco_rover_bringup',
        executable='indicator',
        name='indicator_node',
        output='screen'
    )

    return LaunchDescription([
        gzserver,
        gzclient,
        robot_state_publisher,
        spawn_robot,
        nav2,
        ekf_node,
        pointcloud_node,
        voice_node,
        indicator_node,
    ])
