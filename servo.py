import time
import glob
import os

class Servo:

  def __init__(self, type, pin, polarity="0", period="5000000"):

		os.chdir("/sys/devices/")
		dir = glob.glob("bone_capemgr.*")
		print dir
		self.bone_capemgr_dir = dir[0]

		try:
			self._add_slots("am33xx_pwm")
			self._add_slots("bone_pwm_P8_" + str(pin))
			time.sleep(1)
		except:
			pass

		os.chdir("/sys/devices/")
		dir = glob.glob("ocp.*")
		print dir
		self.ocp_dir = dir[0]

		os.chdir("/sys/devices/%s" % (self.ocp_dir,))
		dir = glob.glob("pwm_test_P8_%s.*" % (pin,))
		print dir
		self.pwm_dir = dir[0]

		self.set_polarity(polarity)
		self.set_period(period)
		self.set_run("0")

	def _write_file(self, file_name, val):

		f = file(file_name, "w")
		f.write(val)
		f.close()

	def _add_slots(self, val):

		self._write_file("/sys/devices/%s/slots" % (self.bone_capemgr_dir,), val)

	def set_polarity(self, val):

		self._write_file("/sys/devices/%s/%s/polarity" % (self.ocp_dir, self.pwm_dir,), val)

	def set_period(self, val):

		self._write_file("/sys/devices/%s/%s/period" % (self.ocp_dir, self.pwm_dir,), val)

	def set_duty(self, val):
		
		self._write_file("/sys/devices/%s/%s/duty" % (self.ocp_dir, self.pwm_dir,), val)

	def set_run(self, val):
		
		self._write_file("/sys/devices/%s/%s/run" % (self.ocp_dir, self.pwm_dir,), val)

	def start(self):

		self.set_run("1")

	def stop(self):

		self.set_run("0")
