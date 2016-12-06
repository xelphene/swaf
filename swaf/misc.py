
import re
import operator
import types
import random
import datetime
import hashlib

def isListOfStrings(x):
	if type(x)!=list:
		return False
	for i in x:
		if type(i)!=str:
			return False
	return True

def isSetOfStrings(x):
	if type(x)!=set:
		return False
	for i in x:
		if type(i)!=str:
			return False
	return True

def isListOfFuncs(x):
	'''return True if x is a list of callables or an empty list.'''
	if type(x)==list or type(x)==tuple:
		x = [operator.isCallable(i) for i in x]
		return reduce(operator.__and__, x, True)
	else:
		return False	

def filterDict(d, keys):
	'''return the dict d with keys not in 'keys' removed.'''
	return dict(
		filter( lambda i: i[0] in keys, d.items() )
	)

def describeObject(handler):
	if hasattr(handler,'swaf_orig'):
		return describeObject(handler.swaf_orig)
	
	if type(handler) == types.MethodType:
		objname = handler.__module__ + '.' + handler.im_class.__name__ + '.' + handler.__name__
	else:
		if hasattr(handler, '__module__') and hasattr(handler,'__name__'):
			objname = handler.__module__ + '.' + handler.__name__
		elif hasattr(handler,'__module__') and hasattr(handler,'__class__'):
			objname = handler.__module__ + '.' + handler.__class__.__name__
		else:
			objname = repr(handler)
	
	
	if hasattr(handler, 'swaf_filter_name'):
		objname = '%s - %s' % (handler.swaf_filter_name, objname)

	if hasattr(handler, 'swaf_description') and handler.swaf_description!=None:
		objname += ' [%s]' % handler.swaf_description
	
	return objname
	

def parseSoS(o):

	'''given a list or set containing strings or a string containing one or
	more space-separated parts, return a set of strings from whichever it
	was.'''

	if type(o)==str:
		return set(o.split(' '))
	elif type(o)==list:
		if isListOfStrings(o):
			return set(o)
		else:	
			raise ValueError('filters object is a list containing things other than strings')
	elif type(o)==set:
		if isSetOfStrings(o):
			return o
		else:
			raise ValueError('filters object is a set containing things other than strings')		
	elif o is None:
		return set()
	else:
		raise ValueError('unknown object %s for conversion to set of strings' % repr(o))

def isHandler(o):
	return (
		hasattr(o, 'swaf_route') and 
		operator.isCallable(o)
	)

def isFilter(o):
	return (
		hasattr(o, 'swaf_filter_name') and 
		operator.isCallable(o)
	)

class Regex:
	def __init__(self, re_src):
		self._re_src = re_src
		self._re = re.compile(re_src)
		
	def match(self, s):
		return self._re.match(s)

	def __str__(self):
		return self._re_src
	
	def __repr__(self):
		return 'Regex(%s)' % repr(self._re_src)
		
def gen_sessionid():
	c1 = str(random.random())
	c2 = str(datetime.datetime.now())
	hash = hashlib.sha1()
	hash.update(c1)
	hash.update(c2)
	return hash.hexdigest()
