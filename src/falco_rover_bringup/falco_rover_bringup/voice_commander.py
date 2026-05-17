import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from action_msgs.msg import GoalStatusArray
import subprocess
import threading

class VoiceCommander(Node):
    def __init__(self):
        super().__init__('voice_commander')
        
        # Subscribe to cmd_vel for movement detection
        self.cmd_vel_sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        
        # Subscribe to navigation status
        self.status_sub = self.create_subscription(
            GoalStatusArray,
            '/navigate_to_pose/_action/status',
            self.nav_status_callback, 10)
        
        self.is_moving = False
        self.last_nav_status = -1
        self.speaking = False
        
        # Announce startup
        self.speak("Falco Rover autonomous navigation system online.")
        self.get_logger().info('Voice Commander Started')

    def speak(self, text):
        if not self.speaking:
            self.speaking = True
            self.get_logger().info(f'Voice: {text}')
            def run():
                subprocess.run(['espeak', '-s', '150', text])
                self.speaking = False
            threading.Thread(target=run, daemon=True).start()

    def cmd_vel_callback(self, msg):
        moving = abs(msg.linear.x) > 0.01 or abs(msg.angular.z) > 0.01
        
        if moving and not self.is_moving:
            self.is_moving = True
            self.speak("Robot moving. Navigation active.")
        elif not moving and self.is_moving:
            self.is_moving = False
            self.speak("Robot stopped.")

    def nav_status_callback(self, msg):
        if not msg.status_list:
            return
            
        status = msg.status_list[-1].status
        
        if status == 2 and self.last_nav_status != 2:
            self.speak("Navigation goal received. Computing path.")
        elif status == 4 and self.last_nav_status != 4:
            self.speak("Goal reached successfully.")
        elif status == 6 and self.last_nav_status != 6:
            self.speak("Navigation failed. Attempting recovery.")
            
        self.last_nav_status = status

def main(args=None):
    rclpy.init(args=args)
    node = VoiceCommander()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
