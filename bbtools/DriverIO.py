
class DriverIO:
	def __init__(self, file_name):
		self.__file = open(file_name, 'r+')
		
	def get(self):
		self.__file.seek(0)
		return self.__file.read()
		
	def set(self, val):		
		self.__file.seek(0)
		self.__file.write(str(val))
		self.__file.flush()

	def __del__(self):
		self.__file.close()
