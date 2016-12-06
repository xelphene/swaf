
import re
import types

from swaf.misc import isListOfStrings, Regex

class NotFound:
	def __call__(self, req):
		return False
	def __str__(self):
		return '(not found route)'
	
NotFoundRoute = NotFound()

class Router:
	def __init__(self):
		self._routes = []
		self._defaultHandler = None
		self._pathCache = {}
	
	def add(self, predicate, handler):
		if type(predicate) == str:
			if predicate[0]=='^':
				predicate = Regex(predicate)
				p = lambda req: predicate.match(req['path'])
			else:
				p = lambda req: req['path'] == predicate
		elif predicate == NotFoundRoute:
			self._defaultHandler = handler
			p = predicate
		elif isListOfStrings(predicate):
			s = set(predicate)
			p = lambda req: req['path'] in s
		elif type(predicate) == type(re.compile('')):
			p = lambda req: predicate.match(req['path'])
		elif issubclass(predicate.__class__, Regex):
			p = lambda req: predicate.match(req['path'])
		elif type(predicate) in [types.FunctionType, types.MethodType]:
			p = predicate
		else:
			raise TypeError("routing predicate must be a callable, a string, a list of strings or a regex")

		self._pathCache = {}
		self._routes.append( (p, handler) )
	
	def route(self, req):
		'''returns a (handler, predicate_result) tuple'''
		
		if req.has_key('path'):
			if self._pathCache.has_key(req['path']):
				(handler, pred) = self._pathCache[req['path']]
				result = pred(req)
				return (handler,result)
			else:
				(handler, pred, result) = self.fullSearch(req)
				self._pathCache[req['path']] = (handler, pred)
				return (handler, result)
		else:
			(handler, pred, result) = self.fullSearch(req)
			return (handler, result)
	
	def fullSearch(self, req):
		'''returns a (handler, predicate, result) tuple'''
		for (pred, handler) in self._routes:
			result = pred(req)
			if result:
				return (handler, pred, result)
		
		if self._defaultHandler==None:
			raise AssertionError("defaultHandler needed but None set")
		
		return (self._defaultHandler, NotFoundRoute, NotFoundRoute(req))
		
		