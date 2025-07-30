import os
import xacro

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node


def generate_launch_description():
    # Declare launch arguments
    declared_launch_arguments = [
        DeclareLaunchArgument(
            "simplify_meshes",
            default_value="false",
            description="Define whether to use simplified meshes for visualization",
        ),
        DeclareLaunchArgument(
            "use_joint_dynamics",
            default_value="true",
            description="Define whether to account for joint dynamics",
        ),
    ]

    return LaunchDescription(declared_launch_arguments + [OpaqueFunction(function=launch_setup)])


def launch_setup(context, *args, **kwargs):
    # Resolve LaunchConfigurations at runtime
    simplify_meshes = LaunchConfiguration("simplify_meshes").perform(context)
    use_joint_dynamics = LaunchConfiguration("use_joint_dynamics").perform(context)

    pkg_name = "neurowalker_description"
    pkg_path = FindPackageShare(pkg_name).find(pkg_name)

    # Paths
    xacro_file = os.path.join(pkg_path, "urdf", "neurowalker_description.xacro")
    rviz2_config = os.path.join(pkg_path, "rviz2", "default.rviz")

    # Process xacro with runtime-resolved values
    robot_description = xacro.process_file(
        xacro_file,
        mappings={
            "simplify_meshes": simplify_meshes,
            "use_joint_dynamics": use_joint_dynamics,
        }
    ).toxml()

    # Define nodes
    nodes = [
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            parameters=[{"robot_description": robot_description}],
        ),
        Node(
            package="joint_state_publisher_gui",
            executable="joint_state_publisher_gui",
            name="joint_state_publisher_gui",
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            arguments=["-d", rviz2_config],
        ),
    ]

    return nodes
