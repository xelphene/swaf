
import types
import logging
import inspect
import pprint
import operator
import re
from operator import isCallable

from resp import *
import swaf.error
import swaf.misc
from swaf.misc import isListOfFuncs

DEBUG=1

def wrapFilter(f, filter_name, filters):
	newf = chainWrap(f)
	newf.__name__ = f.__name__
	newf.__module__ = f.__module__
	newf = debugWrap(newf)
	newf.swaf_orig = f
	newf.swaf_filter_name = filter_name
	newf.swaf_filters = filters
	return newf

def makeWrappedNext(chain):
	
	'''given a list of callables (chain), return a function which takes one
	param (req). When this returned function is called, it will call
	chain[0]( req, chain[1:] ). '''
	
	assert isListOfFuncs(chain)
	def next(req):
		nextf = chain.pop(0)
		return nextf(req, chain)
	next.chain = chain
	return next

def chainWrap(handler):
	def newhandler(req, arg2):
		if isListOfFuncs(arg2):
			arg2 = makeWrappedNext(arg2)
		return handler(req, arg2)
	return newhandler

def debugWrap(f):
	description = swaf.misc.describeObject(f)
	
	pp = pprint.PrettyPrinter()
	logger = logging.getLogger('swaf.wrap')
	def debug(req, chain):
		if DEBUG:
			if not hasattr(debug,'_traceIndent'):
				debug._traceIndent = 0
			if len(chain)>0:
				chain[0]._traceIndent = debug._traceIndent+1
			
			indent = '.    '*debug._traceIndent
			cn = [fi.__name__ for fi in chain]
			cn = ' -> '.join(cn)
			logger.debug('%s| about to call %s' % (indent, description))
			logger.debug('%s| chain=%s' % (indent, cn))
			logger.debug('%s| req=%s' % (indent, repr(req) ) )
			rv = f(req,chain)
			logger.debug('%s| %s.%s returned with %s' % (indent, f.__module__, f.__name__, repr(rv)))
			return rv
		else:
			return f(req, chain)
	
	debug.__name__ = f.__name__
	debug.__module__ = f.__module__
	
	debug.swaf_orig = f
	
	if hasattr(f,'swaf_description'):
		debug.swaf_description = f.swaf_description
	if hasattr(f,'swaf_route'):
		debug.swaf_route = f.swaf_route
	if hasattr(f,'swaf_filters'):
		debug.swaf_filters = f.swaf_filters
			
	return debug

def wrapHandler(handler, route, filters, description):
	if type(handler)==types.InstanceType:
		(args, varargs, varkw, defaults) = inspect.getargspec(handler.__call__)
		# remove the 'self' arg from __call__
		assert len(args)>0
		args = args[1:]
	elif type(handler)==types.MethodType:
		(args, varargs, varkw, defaults) = inspect.getargspec(handler)
		# remove the 'self' arg
		assert len(args)>0
		args = args[1:]
	else:
		(args, varargs, varkw, defaults) = inspect.getargspec(handler)
		
	def callHandler(req, next):
		if varkw==None:
			req = swaf.misc.filterDict(req, args)
			if set(req.keys()) != set(args):
				raise swaf.error.LeafUnknownParamError(handler,req)
			return handler(**req)
		else:
			return handler(**req)

	callHandler.swaf_orig = handler
	callHandler.swaf_route = route
	callHandler.swaf_filters = filters
	callHandler.swaf_description = description
	callHandler = debugWrap(callHandler)
	callHandler.swaf_orig = handler
	callHandler.swaf_route = route
	callHandler.swaf_filters = filters
	callHandler.swaf_description = description

	return callHandler
