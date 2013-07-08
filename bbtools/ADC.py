import glob
import errno
import devices
from DriverIO import *

AIN0 = 'P9_39'
AIN1 = 'P9_40'
AIN2 = 'P9_37'
AIN3 = 'P9_38'
AIN4 = 'P9_33'
AIN5 = 'P9_36'
AIN6 = 'P9_35'
AIN7 = AIN0

AIN_PINS = {
	AIN0 : 'AIN0',
	AIN1 : 'AIN1',
	AIN2 : 'AIN2',
	AIN3 : 'AIN3',
	AIN4 : 'AIN4',
	AIN5 : 'AIN5',
	AIN6 : 'AIN6'
}

class ADC:
	pass
	