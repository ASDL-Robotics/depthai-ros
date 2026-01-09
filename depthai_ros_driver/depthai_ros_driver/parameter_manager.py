import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import Parameter, ParameterValue, ParameterType
from rcl_interfaces.srv import SetParameters, GetParameters
from std_srvs.srv import Trigger


class ParameterManager:
    def __init__(self, node: Node) -> None:
        self.node = node
        self.stopSrv = self.node.create_client(Trigger, "/oak/stop_driver")
        while not self.stopSrv.wait_for_service(timeout_sec=1.0):
            self.node.get_logger().info("service not available, waiting again...")
        self.startSrv = self.node.create_client(Trigger, "/oak/start_driver")
        while not self.startSrv.wait_for_service(timeout_sec=1.0):
            self.node.get_logger().info("service not available, waiting again...")
        self.paramSrv = self.node.create_client(SetParameters, "/oak/set_parameters")
        while not self.paramSrv.wait_for_service(timeout_sec=1.0):
            self.node.get_logger().info("service not available, waiting again...")

    def setParameters(self, params: list[Parameter]) -> bool:
        req = SetParameters.Request()
        req.parameters = params
        future = self.paramSrv.call_async(req)
        rclpy.spin_until_future_complete(self.node, future)
        self.node.get_logger().info(str(future.result().results[0].reason))
        if future.result().results[0].successful:
            return self.restartDriver()
        else:
            return False

    def restartDriver(self) -> bool:
        req = Trigger.Request()
        future = self.stopSrv.call_async(req)
        rclpy.spin_until_future_complete(self.node, future)
        if not future.result().success:
            return False
        req = Trigger.Request()
        future = self.startSrv.call_async(req)
        rclpy.spin_until_future_complete(self.node, future)
        if not future.result().success:
            return False
        return True
