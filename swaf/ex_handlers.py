
import re

import swaf
from swaf.misc import Regex

class Handler:
	def __init__(self):
		self._state = 'blah o'
		self.swaf_route = '/obj'
		self.swaf_description = 'the callable object handler'
		self.swaf_filters = 'GET'
	
	def __call__(self):
		return self._state

h1 = Handler()
# h1 is a handler

####

@swaf.handler('/func', 'GET auth tmpl', 'the function handler')
def h2(trender):
	#return 'blah f'
	return trender('/home.tmpl')

### 

h3 = lambda: 'blah l'
h3 = swaf.makeHandler(h3, Regex('^/lambda'))

###

class Handler4:
	def __init__(self):
		self._state = 'blah o4'
	
	@swaf.handler('/method')
	def handle(self, path):
		return self._state
	#handle.swaf_route = '/asdf'

#o4 = Handler4()
