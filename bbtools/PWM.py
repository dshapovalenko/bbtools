import glob
import errno
import devices
from DriverIO import *

POLARITY_HIGH = 0	# active high
POLARITY_LOW = 1	# active low (driver default)

# EHRPWM0 A: P9_22,[P9_31] B: P9_21,[P9_29]
# EHRPWM1 A: P9_14,[P8_36] B: P9_16,[P8_34]
# EHRPWM2 A: P8_19,[P8_45] B: P8_13,[P8_46]
# ECAPPWM0: P9_42
# ECAPPWM2: [P9_28]

PWM0A = 'P9_22'
PWM0B = 'P9_21'
PWM1A = 'P9_14'
PWM1B = 'P9_16'
PWM2A = 'P8_19'
PWM3B = 'P8_13'
ECAPPWM0 = 'P9_42'

PWM_PINS = {
	PWM0A : 0,
	PWM0B : 0,
	PWM1A : 1,
	PWM1B : 1,
	PWM2A : 2,
	PWM3B : 2,
	ECAPPWM0 : 100	
}

def getValue(val):
	if type(val) == int:
		if val < 0 or val > 1000000000:
			raise ValueError()
		return val
	elif type(val) == float:
		if val < 0 or val > 1:
			raise ValueError()
		return val
	elif type(val) == str:
		if val.endswith("%"):
			return getValue(float(val[:-1]) / 100)
		elif val.lower().endswith("ns"):
			return getValue(int(val[:-2]))
		elif val.lower().endswith("us"):
			return getValue(int(val[:-2])*1000)
		elif val.lower().endswith("ms"):
			return getValue(int(val[:-2])*1000000)
		elif val.lower().endswith("hz"):
			if val <= 0:
				raise ValueError()
			return getValue(int(1000000000 / float(val[:-2])))
		else:
			return getValue(int(val))
	else:
		raise TypeError()


class PWM:
	
	def __init__(self, pin, polarity, period):
		if pin not in PWM_PINS:
			raise Exception("Invalid pin")
		
		modules = devices.bone_capemgr.get_modules()
		if "am33xx_pwm" not in modules:
			devices.bone_capemgr.load_module("am33xx_pwm")
		
		pwm_module = "sc_pwm_" + pin;
		self.pwm_module = pwm_module
		if pwm_module in modules:
			raise Exception("Pin already in use")
			
		try:
			devices.bone_capemgr.load_module(pwm_module)		
		except IOError as e:
			if e.errno in {errno.EEXIST, errno.ENOENT}:
				raise Exception("Invalid pin")
			else:
				raise e
		
		self.dir = glob.glob("%s/pwm_test_%s.*" % (devices.ocp.dir, pin))[0]
		
		self.__fpolarity = DriverIO(self.dir + "/polarity")
		self.__fperiod = DriverIO(self.dir + "/period")
		self.__fduty = DriverIO(self.dir + "/duty")
		self.__frun = DriverIO(self.dir + "/run")
		
		#self.disable()	# not need
		self.set_polarity(polarity)
		self.set_period(period)
		
	def __del__(self):
		print('PWM destroy')
		try:
			del self.__fpolarity
			del self.__fperiod
			del self.__fduty
			devices.bone_capemgr.unload_module(self.pwm_module)		
		except Exception as e:
			print(e)
	
	def set_polarity(self, val):
		if val not in {POLARITY_HIGH, POLARITY_LOW}:
			raise ValueError()
		#self.__polarity = val
		self.__fpolarity.set(val)

	def set_period(self, val):
		val = getValue(val)
		if type(val) == float:
			raise TypeError()
		assert val > 0, 'Period must be bigger than zero'
		
		self.__period = val
		try:
			self.__fperiod.set(val)
		except IOError as e:
			if e.errno == errno.EINVAL:
				raise Exception("Period on both channels of each EHRPWM must be same")
			else:
				raise e

	def set_duty(self, val):
		val = getValue(val)
		if type(val) == float:
			val = int(self.__period * val)
		#self.__duty = val
		self.__fduty.set(val)

	def set_run(self, val):
		if type(val) != bool:
			raise TypeError()
		#self.__run = val
		self.__frun.set(int(val))

	def get_run(self):
		return bool(int(self.__frun.get()))
		
	def enable(self):
		self.set_run(True)

	def disable(self):
		self.set_run(False)

	def is_enabled(self):
		return self.get_run()

	def get_polarity(self):
		#return self.__polarity
		return int(self.__fpolarity.get())

	def get_period_ns(self):
		#return self.__period
		return int(self.__fperiod.get())

	def get_period_us(self):
		return self.get_period_ns() // 1000

	def get_period_ms(self):
		return self.get_period_ns() // 1000000

	def get_period_hz(self):
		return 1000000000.0 / self.get_period_ns()

	def get_duty_ns(self):
		#return self.__duty
		return int(self.__fduty.get())

	def get_duty_us(self):
		return self.get_duty_ns() // 1000

	def get_duty_ms(self):
		return self.get_duty_ns() // 1000000

	def get_duty_hz(self):
		return 1000000000.0 / self.get_duty_ns()

	def get_duty_percent(self):
		return self.get_duty_ns() * 100.0 / self.get_period_ns()

	def get_duty(self):
		return float(self.get_duty_ns()) / self.get_period_ns()
