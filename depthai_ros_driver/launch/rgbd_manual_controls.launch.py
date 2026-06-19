import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def launch_setup(context, *args, **kwargs):
    params_file = LaunchConfiguration("params_file")
    depthai_prefix = get_package_share_directory("depthai_ros_driver")

    name = LaunchConfiguration("name").perform(context)
    return [
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(depthai_prefix, "launch", "driver.launch.py")
            ),
            launch_arguments={
                "name": name,
                "camera_model": LaunchConfiguration("camera_model"),
                "parent_frame": LaunchConfiguration("parent_frame"),
                "cam_pos_x": LaunchConfiguration("cam_pos_x"),
                "cam_pos_y": LaunchConfiguration("cam_pos_y"),
                "cam_pos_z": LaunchConfiguration("cam_pos_z"),
                "cam_roll": LaunchConfiguration("cam_roll"),
                "cam_pitch": LaunchConfiguration("cam_pitch"),
                "cam_yaw": LaunchConfiguration("cam_yaw"),
                "params_file": params_file,
                "use_rviz": LaunchConfiguration("use_rviz"),
                "rviz_config": LaunchConfiguration("rviz_config"),
                "rs_compat": LaunchConfiguration("rs_compat"),
                "publish_tf_from_calibration": LaunchConfiguration(
                    "publish_tf_from_calibration"
                ),
                "override_cam_model": LaunchConfiguration("override_cam_model"),
                "imu_from_descr": LaunchConfiguration("imu_from_descr"),
            }.items(),
        )
    ]


def generate_launch_description():
    depthai_prefix = get_package_share_directory("depthai_ros_driver")
    declared_arguments = [
        DeclareLaunchArgument("name", default_value="oak"),
        DeclareLaunchArgument("camera_model", default_value="OAK-D"),
        DeclareLaunchArgument("parent_frame", default_value="oak_parent_frame"),
        DeclareLaunchArgument("cam_pos_x", default_value="0.0"),
        DeclareLaunchArgument("cam_pos_y", default_value="0.0"),
        DeclareLaunchArgument("cam_pos_z", default_value="0.0"),
        DeclareLaunchArgument("cam_roll", default_value="0.0"),
        DeclareLaunchArgument("cam_pitch", default_value="0.0"),
        DeclareLaunchArgument("cam_yaw", default_value="0.0"),
        DeclareLaunchArgument(
            "params_file",
            default_value=os.path.join(
                depthai_prefix, "config", "rgbd_manual_controls.yaml"
            ),
        ),
        DeclareLaunchArgument("use_rviz", default_value="False"),
        DeclareLaunchArgument(
            "rviz_config",
            default_value=os.path.join(depthai_prefix, "config", "rviz", "rgbd.rviz"),
        ),
        DeclareLaunchArgument("rs_compat", default_value="False"),
        DeclareLaunchArgument("publish_tf_from_calibration", default_value="true"),
        DeclareLaunchArgument("override_cam_model", default_value="false"),
        DeclareLaunchArgument("imu_from_descr", default_value="false"),
    ]

    return LaunchDescription(
        declared_arguments + [OpaqueFunction(function=launch_setup)]
    )
