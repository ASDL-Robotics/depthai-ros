import os
import unittest
import time
import launch
import launch_testing
import launch_testing.actions
import launch_testing.markers
import launch_testing.asserts
import pytest
import rclpy
import rclpy.node

from sensor_msgs.msg import Image, CameraInfo
from std_srvs.srv import Trigger
from rcl_interfaces.msg import Parameter, ParameterValue, ParameterType
from rcl_interfaces.srv import SetParameters, GetParameters
from launch_ros.actions import ComposableNodeContainer
from ament_index_python.packages import get_package_share_directory
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.descriptions import ComposableNode
from rclpy.node import Node
from depthai_ros_driver.parameter_manager import ParameterManager

IS_RVC4 = os.getenv("DEPTHAI_PLATFORM") == "rvc4"

@pytest.mark.rostest
@unittest.skipUnless(IS_RVC4, reason="Test not supported on RVC2")
def generate_test_description():
    name = "oak"
    params = {
        "pipeline_gen": {"i_pipeline_type": "DEPTH"},
        "stereo": {
            "i_use_neural_depth": True,
            "i_aligned": False,
        },
    }

    driver = ComposableNodeContainer(
        name=f"{name}_container",
        namespace="",
        package="rclcpp_components",
        executable="component_container",
        composable_node_descriptions=[
            ComposableNode(
                package="depthai_ros_driver",
                plugin="depthai_ros_driver::Driver",
                name=name,
                parameters=[
                    params,
                ],
            )
        ],
        output="both",
    )

    return launch.LaunchDescription(
        [
            driver,
            launch.actions.TimerAction(
                period=1.0, actions=[launch_testing.actions.ReadyToTest()]
            ),
        ]
    ), {"driver_node": driver}



class TestDriverLaunch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.node = rclpy.create_node("test")
        self.paramMan = ParameterManager(self.node)

    def tearDown(self):
        self.node.destroy_node()

    @unittest.skipUnless(IS_RVC4, reason="Test not supported on RVC2")
    def test_driver_output(self, proc_output):
        proc_output.assertWaitFor("Driver ready!", timeout=10.0, stream="stderr")

    @unittest.skipUnless(IS_RVC4, reason="Test not supported on RVC2")
    def testMessages(self, width=0, height=0):
        if width == 0 or height == 0:
            return
        images_received = []
        info_received = []
        sub = self.node.create_subscription(
            Image,
            "/oak/stereo/image_raw",
            lambda msg: images_received.append(msg),
            10,
        )
        sub_info = self.node.create_subscription(
            CameraInfo,
            "/oak/stereo/camera_info",
            lambda msg: info_received.append(msg),
            10,
        )
        try:
            end_time = time.time() + 5
            while time.time() < end_time:
                rclpy.spin_once(self.node, timeout_sec=1)
                if len(images_received) > 30 and len(info_received) > 30:
                    break
            self.assertGreater(len(images_received), 30)
            self.assertGreater(len(info_received), 30)
            self.assertEqual(images_received[0].width, width)
            self.assertEqual(images_received[0].height, height)
        finally:
            self.node.destroy_subscription(sub)

    @unittest.skipUnless(IS_RVC4, reason="Test not supported on RVC2")
    def test_published_stereo_image(self, proc_output):
        parameters = [
            Parameter(
                name="stereo.i_neural_depth_model",
                value=ParameterValue(type=4, string_value="NEURAL_DEPTH_LARGE"),
            )
        ]
        self.assertTrue(self.paramMan.setParameters(parameters))
        self.testMessages(768, 480)

    @unittest.skipUnless(IS_RVC4, reason="Test not supported on RVC2")
    def test_change_neural_depth_model(self, proc_output):
        parameters = [
            Parameter(
                name="stereo.i_neural_depth_model",
                value=ParameterValue(type=4, string_value="NEURAL_DEPTH_NANO"),
            )
        ]
        self.assertTrue(self.paramMan.setParameters(parameters))
        self.testMessages(384, 240)


@launch_testing.post_shutdown_test()
class TestShutdown(unittest.TestCase):
    @unittest.skipUnless(IS_RVC4, reason="Test not supported on RVC2")
    def test_exit_codes(self, proc_info):
        launch_testing.asserts.assertExitCodes(proc_info)
