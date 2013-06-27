import time
from bbtools.servo import Servo

class BBRobot:

  def __init__(self):
		self.gripper = Servo("pwm", 13)

	def start_gripper(self):
		self.gripper.start()

	def stop_gripper(self):
		self.gripper.stop()

	def take(self):
		self.gripper.set_duty("1700000")
		time.sleep(1)

	def half_take(self):
		self.gripper.set_duty("1200000")
		time.sleep(1)

	def release(self):
		self.gripper.set_duty("0000000")
		time.sleep(1)
