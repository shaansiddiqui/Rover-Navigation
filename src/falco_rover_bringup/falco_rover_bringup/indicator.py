import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Twist
from action_msgs.msg import GoalStatusArray
import math

class IndicatorNode(Node):
    def __init__(self):
        super().__init__('indicator_node')
        
        # Publisher for visual markers in RViz
        self.marker_pub = self.create_publisher(
            Marker, '/indicator/status_marker', 10)
        
        # Subscribe to cmd_vel
        self.cmd_vel_sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        
        # Subscribe to navigation status
        self.status_sub = self.create_subscription(
            GoalStatusArray,
            '/navigate_to_pose/_action/status',
            self.nav_status_callback, 10)
        
        self.is_moving = False
        self.nav_status = 0
        
        # Timer for publishing indicators
        self.timer = self.create_timer(0.5, self.publish_indicator)
        self.get_logger().info('Indicator Node Started')

    def cmd_vel_callback(self, msg):
        self.is_moving = abs(msg.linear.x) > 0.01 or abs(msg.angular.z) > 0.01

    def nav_status_callback(self, msg):
        if msg.status_list:
            self.nav_status = msg.status_list[-1].status

    def publish_indicator(self):
        marker = Marker()
        marker.header.frame_id = 'base_footprint'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'status'
        marker.id = 0
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD

        marker.pose.position.x = 0.0
        marker.pose.position.y = 0.0
        marker.pose.position.z = 0.4
        marker.pose.orientation.w = 1.0

        marker.scale.x = 0.15
        marker.scale.y = 0.15
        marker.scale.z = 0.15

        # GREEN = moving, YELLOW = goal received, RED = idle/failed
        if self.nav_status == 4:  # Goal reached
            r, g, b = 0.0, 1.0, 0.0
            self.get_logger().info('[LED GREEN] Goal Reached!')
        elif self.is_moving:
            r, g, b = 0.0, 1.0, 0.0
            self.get_logger().info('[LED GREEN] Robot Moving')
        elif self.nav_status == 2:  # Navigating
            r, g, b = 1.0, 1.0, 0.0
            self.get_logger().info('[LED YELLOW] Navigating')
        elif self.nav_status == 6:  # Failed
            r, g, b = 1.0, 0.0, 0.0
            self.get_logger().info('[LED RED] Navigation Failed')
        else:
            r, g, b = 1.0, 0.0, 0.0
            self.get_logger().info('[LED RED] Robot Idle')

        marker.color.r = r
        marker.color.g = g
        marker.color.b = b
        marker.color.a = 1.0

        self.marker_pub.publish(marker)

def main(args=None):
    rclpy.init(args=args)
    node = IndicatorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
