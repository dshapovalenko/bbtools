import glob
import time

devices_dir = "/sys/devices"
dir = devices_dir

class bone_capemgr:
	name = "bone_capemgr"
	
	@classmethod
	def _init(cls):
		cls.dir = glob.glob('%s/%s.*' % (devices_dir, cls.name))[0]
		cls.sys_name  = cls.dir[len(devices_dir) + 1:]

	@classmethod
	def get_modules(cls):
		file = open(cls.dir + '/slots', 'r')
		slots = set()
		try:
			for slot in file:
				rec = slot.strip().split(',')
				if len(rec) == 4:
					slots.add(rec[-1].strip())
		finally:
			file.close()
		return list(slots);

	@classmethod
	def get_module_id(cls, module):
		file = open(cls.dir + '/slots', 'r')
		try:
			for slot in file:
				rec = slot.strip().split(':', 1)
				attrs = rec[1].split(',')
				if len(attrs) == 4 and attrs[3].strip() == module:
					return int(rec[0])
		finally:
			file.close()
		return None
	
	@classmethod
	def load_module(cls, module):
		file = open(cls.dir + '/slots', 'w')
		file.write(module)
		file.close()
		time.sleep(0.1)

	@classmethod
	def unload_module(cls, module):
		id = cls.get_module_id(module)
		file = open(cls.dir + '/slots', 'w')
		file.write('-%d' % id)
		file.close()
		time.sleep(0.1)

bone_capemgr._init()


class ocp:
	name = "ocp"
	
	@classmethod
	def _init(cls):
		cls.dir = glob.glob('%s/%s.*' % (devices_dir, cls.name))[0]
		cls.sys_name  = cls.dir[len(devices_dir) + 1:]

ocp._init()