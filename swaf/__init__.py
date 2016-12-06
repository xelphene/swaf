
import operator

def makeHandler(callable, route, filters=None, description=None):
	assert operator.isCallable(callable)
	callable.swaf_route = route
	callable.swaf_filters = filters
	callable.swaf_description = description
	return callable
	
def handler(route, filters=None, description=None):
	def decorate(o):
		o = makeHandler(o, route, filters, description)
		return o
	return decorate


def makeFilter(f, filter_name=None, filters=None):
	if filter_name == None:
		filter_name = f.__name__
	
	f.swaf_filters = filters
	f.swaf_filter_name = filter_name
	
	return f

def filter(filter_name=None, filters=None):
	def decorate(o):
		o = makeFilter(o, filter_name, filters)
		return o
	return decorate
