import time
from PWM import *
#from Queue import Queue
from collections import deque
from threading import Timer, Lock

STEP_PERCENT_VALUE = 3
STEP_ANGLE_VALUE = 5
STEP_DELAY_VALUE = 0.1

class Servo:

	def __init__(self, pin, polarity = POLARITY_HIGH, period = '20ms', # '50hz' '1000hz' '500hz'
				min_duty = '1ms', max_duty = '2ms', min_angle = -90.0, max_angle = 90.0):
				
		self.__pin = PWM(pin, polarity, period)
		self.setMinMaxDuty(min_duty, max_duty)
		self.setMinMaxAngle(min_angle, max_angle)
		
		self.__targetDuty = self.__pin.get_duty_ns()
		self.__targetsQueue = deque() # Queue()
		self.__timer = None
		self.__lock = Lock()
		if self.__targetDuty == 0:
			self.setPercent(50)
			
	def __del__(self):
		print('Servo destroy')
		del self.__pin
		
	def setMinMaxDuty(self, min, max):
		period = self.__pin.get_period_ns()
		min_duty = getValue(min)
		max_duty = getValue(max)
		if type(max_duty) != int or type(min_duty) != int:
			raise TypeError()
			
		assert min_duty < max_duty, 'Min duty must be less than Max duty'
		assert period >= max_duty, 'Max duty must be less than or equal to Period'
		assert min_duty >= 0, 'Min duty must be bigger than or equal to  zero'

		self.__min_duty = min_duty
		self.__max_duty = max_duty
		
	def setMinMaxAngle(self, min_angle, max_angle):		
		assert min_angle < max_angle, 'Min angle must be less than Max angle'
		
		self.__min_angle = min_angle
		self.__max_angle = max_angle
	
	def setAngle(self, val, step = None, delay = STEP_DELAY_VALUE, async = True, queue = False, start = True):
		val = min([self.__max_angle, val])
		val = max([self.__min_angle, val])
		delta = self.__max_angle - self.__min_angle
		percent = (val - self.__min_angle) * 100.0 / delta
		
		self.setPercent(percent, None if step == None else step*100.0/delta, delay, async, queue, start)

	def setPercent(self, val, step = None, delay = STEP_DELAY_VALUE, async = True, queue = False, start = True):
		assert 0.0 <= val <= 100.0, 'Bad percent value'
		
		targetDuty = int(self.__min_duty + (self.__max_duty - self.__min_duty) * val / 100.0)
		
		print('before lock')
		self.__lock.acquire()
		try:
			currentDuty = self.__pin.get_duty_ns()
			if step == None or not self.isEnabled() and not queue:
				print('before no step')
				self.__destroyTimer()
				self.__targetsQueue.clear()
				self.__targetDuty = targetDuty
				if targetDuty == currentDuty: return
				self.__pin.set_duty(self.__targetDuty)
				print('after no step')
			else:
				print('before step')
				step = int((self.__max_duty - self.__min_duty) * step / 100.0)
				if not async and self.isEnabled():
					print('before sync')
					self.__destroyTimer()
					self.__targetsQueue.clear()
					self.__targetDuty = targetDuty
					if targetDuty == currentDuty: return
					self.__currentDuty = currentDuty
					self.__syncStepping(step, delay)
					print('after sync')
				elif (self.isMoving() or not start or not self.isEnabled()) and queue:
					print('before queue')
					self.__targetsQueue.append((targetDuty, step, delay))
					print('after queue')
				else:
					print('before async')
					self.__destroyTimer()
					self.__targetsQueue.clear()
					self.__targetDuty = targetDuty
					if targetDuty == currentDuty: return
					self.__currentDuty = currentDuty
					print('before do step')
					self.__doStep(step)
					print('after do step')
					if self.__currentDuty != targetDuty:
						self.__timer = Timer(delay, self.__doAsyncStep, [step])
						self.__timer.start()
					print('after async')
				print('after step')
		finally:
			self.__lock.release()
			
	
	def __destroyTimer(self):
		if self.isMoving():
			self.__timer.cancel()
			self.__timer = None

	def __doAsyncStep(self, step):
		self.__lock.acquire()
		try:
			if not self.isMoving(): return
			self.__doStep(step)
			if self.__currentDuty != self.__targetDuty:
				self.__timer = Timer(self.__timer.interval, self.__doAsyncStep, [step])
				self.__timer.start()
			elif len(self.__targetsQueue) > 0:
				(targetDuty, step, delay) = self.__targetsQueue.popleft()
				self.__targetDuty = targetDuty
				self.__timer = Timer(delay, self.__doAsyncStep, [step])
				self.__timer.start()
		finally:
			self.__lock.release()
	
	def __syncStepping(self, step, delay):
		while self.__targetDuty != self.__currentDuty:
			self.__doStep(step)
			if self.__targetDuty != self.__currentDuty:
				time.sleep(delay)
	
	def __doStep(self, step):
		if self.__targetDuty > self.__currentDuty and self.__targetDuty - self.__currentDuty > step:
			self.__currentDuty += step
		elif self.__currentDuty > self.__targetDuty and self.__currentDuty - self.__targetDuty > step:
			self.__currentDuty -= step
		else:
			self.__currentDuty = self.__targetDuty
		self.__pin.set_duty(self.__currentDuty)
	

	def addTargetAngle(self, val, step = STEP_ANGLE_VALUE, delay = STEP_DELAY_VALUE):
		self.setAngle(val, step, delay, True, True, False)
	
	def addTargetPercent(self, val, step = STEP_PERCENT_VALUE, delay = STEP_DELAY_VALUE):
		self.setPercent(val, step, delay, True, True, False)
	
	def start(self):
		if not self.isEnabled(): return 
		self.__lock.acquire()
		try:
			if not self.isMoving() and len(self.__targetsQueue) > 0:
				(targetDuty, step, delay) = self.__targetsQueue.popleft()
				self.__targetDuty = targetDuty
				self.__currentDuty = self.__pin.get_duty_ns()
				self.__timer = Timer(delay, self.__doAsyncStep, [step])
				self.__timer.start()	
		finally:
			self.__lock.release()
	

	def stop(self):
		if not self.isEnabled(): return 
		self.__lock.acquire()
		try:
			if self.isMoving():
				step = self.__timer.args[0]
				delay = self.__timer.interval
				self.__targetsQueue.appendleft((self.__targetDuty, step, delay))
				self.__destroyTimer()
		finally:
			self.__lock.release()
		
	
	def clearTargetsQueue(self):
		self.__lock.acquire()
		try:
			self.__targetsQueue.clear()
		finally:
			self.__lock.release()
		

	def enable(self, start = True):
		self.__pin.enable()
		if start:
			self.start()

	def disable(self):
		self.stop()
		self.__pin.disable()

	def isEnabled(self):
		return self.__pin.is_enabled()

	def getAngle(self):
		alpha = self.__max_angle - self.__min_angle
		delta = self.__max_duty - self.__min_duty
		return self.__min_angle + (self.__pin.get_duty_ns() - self.__min_duty) * alpha / float(delta)
		
	def getPercent(self):
		delta = self.__max_duty - self.__min_duty
		return (self.__pin.get_duty_ns() - self.__min_duty) * 100.0 / delta

	def getTargetAngle(self):
		alpha = self.__max_angle - self.__min_angle
		delta = self.__max_duty - self.__min_duty
		return self.__min_angle + (self.__targetDuty - self.__min_duty) * alpha / float(delta)
		
	def getTargetPercent(self):
		delta = self.__max_duty - self.__min_duty
		return (self.__targetDuty - self.__min_duty) * 100.0 / delta
	
	def isMoving(self):
		return self.__timer != None
	
