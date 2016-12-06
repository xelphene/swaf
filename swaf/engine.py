
import logging
import types
import inspect
import operator
import sys
import traceback
import copy
import random

import swaf.dep
import swaf.router
from swaf.misc import describeObject, parseSoS, isHandler, isFilter
import swaf.wrap
import swaf.handlers

class Engine:
	def __init__(self):
		self._router = swaf.router.Router()
		self._handlers = set()
		self._filters = {}
		self._global_filters = set()
		self._log = logging.getLogger('swaf.Engine')
		self._log_prefix = ''

		self._prior_chain = []
		self._prior_handler = None
		self._show_verbose_errors = False
		self._wsgi_logging_initted = False
		self.addHandler(swaf.handlers.notFound)
	
	def enable_verbose_errors(self):
		self._show_verbose_errors = True
	
	def disable_verbose_errors(self):
		self._show_verbose_errors = False

	def addFilter(self, filter, name=None, filters=None, globalf=False):
		if not operator.isCallable(filter):
			raise ValueError('filter is not a callable')
		
		if name==None:
			if hasattr(filter, 'swaf_filter_name'):
				name = filter.swaf_filter_name
			else:
				raise ValueError('filter object %s has no swaf_filter_name attribute and name not specified as param' % repr(filter))
		
		if filters==None:
			if hasattr(filter, 'swaf_filters'):
				filters = filter.swaf_filters
			else:
				filters = set()
		filters = parseSoS(filters)
		
		if not self._filters.has_key(name):
			filter = swaf.wrap.wrapFilter(filter, name, filters)
			self._filters[name] = filter
			self._log.debug('%snew filter: %s as %s' % (
				self._log_prefix,
				swaf.misc.describeObject(filter),
				name
			))

			if globalf:
				self._global_filters.add(filter)

	def addGlobalFilter(self, filter, name=None, filters=None):
		self.addFilter(filter, name=name, filters=filters, globalf=True)
	
	def addHandler(self, handler, route=None, filters=None, description=None):
		if not operator.isCallable(handler):
			raise ValueError('handler is not a callable')
		
		if route==None:
			if hasattr(handler, 'swaf_route'):
				route = handler.swaf_route
			else:
				raise ValueError('handler object %s has no swaf_route attribute and route not specified as param' % repr(handler))
		
		if filters==None:
			if hasattr(handler, 'swaf_filters'):
				filters = handler.swaf_filters
			else:
				filters = set()
		filters = parseSoS(filters)
		
		if description==None:
			if hasattr(handler, 'swaf_description'):
				description = handler.swaf_description
			else:
				description = ''
		
		if handler not in self._handlers:
			handler = swaf.wrap.wrapHandler(handler, route, filters, description)
			self._router.add(route, handler)
			self._handlers.add(handler)
			self._log.debug('%snew handler: %s -> %s' % (
				self._log_prefix,
				route,
				swaf.misc.describeObject(handler)
			))

	def searchForHandlers(self, o):
		self._log.debug('searching %s' % repr(o))
		self._log_prefix = '    '
		for h in searchForHandlers(o):
			self.addHandler(h)
		self._log_prefix = ''
		self._log.debug('done searching %s' % repr(o))

	def searchForFilters(self, o):
		self._log.debug('searching %s' % repr(o))
		self._log_prefix = '    '
		for f in searchForFilters(o):
			self.addFilter(f)
		self._log_prefix = ''
		self._log.debug('done searching %s' % repr(o))
	
	def handle_inner(self, req):
		self._log.debug('handling request for %s' % req['path'])
		(handler, route_result) = self._router.route(req)
		req['route_result'] = route_result
		self._log.debug('  handler: %s' % describeObject(handler))
		self._prior_handler = handler
		
		self._log.debug('  handler-requested filters: %s' % ','.join(handler.swaf_filters))
		
		filters_to_use = handler.swaf_filters.union(self._global_filters)
		chain = swaf.dep.findFilters(filters_to_use, self.getFilter)
		chain = swaf.dep.filterDepList(chain)
		chain = [self.getFilter(i) for i in chain]
		chain.append(handler)
		self._prior_chain = copy.copy(chain)

		self._log.debug('call chain:')
		for i in chain:
			self._log.debug('    %s' % swaf.misc.describeObject(i))
		
		basef = chain.pop(0)
		
		resp = basef(req, chain)
		return resp
	
	def handle(self, req):	
		try:
			return self.handle_inner(req)		
		except NoSuchFilterError, nsfe:
			report = []

			report.append('The handler for this request, %s, requests a filter named %s but no such filter is in the Engine.' % (
				swaf.misc.describeObject(self._prior_handler),
				repr(nsfe.name)
			))

			report.append('')
			report.append('swaf filters available:')
			for i in self._filters.values():
				report.append('  %s' % swaf.misc.describeObject(i))
			
			return self.respond_to_error_report(report)
		except:
			report = []
			
			report.append('swaf call chain:')
			for i in self._prior_chain:
				report.append('  %s' % swaf.misc.describeObject(i))
			report.append('')

			report.append('swaf filters available:')
			for i in self._filters.values():
				report.append('  %s' % swaf.misc.describeObject(i))
			report.append('')
			
			report.append('Exception information:')
			(exc_type, exc_value, exc_trace) = sys.exc_info()
			report.append('  Exception type: %s' % str(exc_type))
			report.append('  Exception value: %s' % exc_value)
			
			frames = traceback.format_exception(exc_type, exc_value, exc_trace)
			for line in frames:
				line=line[:-1]
				for subline in line.split('\n'):
					report.append('  '+subline)
			
			
			return self.respond_to_error_report(report)
	
	def respond_to_error_report(self, report):
		errcode = gen_error_code()
		for line in report:
			self._log.error('SWAF_ERR:%s: %s' % (errcode,line))
			
		if self._show_verbose_errors:
			return swaf.resp.error_verbose(errcode, report)
		else:
			return swaf.resp.error_vague(errcode)
		
	def wsgi(self, env, start):
		if not self._wsgi_logging_initted:
			self.init_wsgi_logging()
			self._wsgi_logging_initted=True
			
		req = {
			'path': env['PATH_INFO'],
			'wsgienv': env
		}
		resp = self.handle(req)
		status = '%d %s' % (resp['status'], resp['reason'])
		start(status, resp['headers'])
		return resp['body']

	def init_wsgi_logging(self):

		'''set up the python logging API to write all error-level logs to
		stderr (where they will show up the apache error log).'''

		h = logging.StreamHandler(sys.stderr)
		h.setLevel(logging.ERROR)
		f = logging.Formatter('%(message)s')
		h.setFormatter(f)
		self._log.addHandler(h)
		
	def getFilter(self, name):
		if self._filters.has_key(name):
			return self._filters[name]
		else:
			raise NoSuchFilterError(name)
	
	def logConfig(self):
		self._log.info('swaf engine configuration:')
		self._log.info('  handlers:')
		for h in self._handlers:
			self._log.info('    %s @ %s' % (
				describeObject(h),
				h.swaf_route
			))
		self._log.info('  filters:')
		for f in self._filters.values():
			self._log.info('    %s as %s' % (
				describeObject(f),
				f.swaf_filter_name
			))

def searchForHandlers(o):
	handlers = []
	if type(o) == types.ModuleType:
		for (name, memb) in inspect.getmembers(o):
			if isHandler(memb):
				handlers.append(memb)
			if type(memb) == types.InstanceType:
				handlers += searchForHandlers(memb)
	elif type(o) == types.InstanceType:
		for (name, memb) in inspect.getmembers(o):
			if isHandler(memb):
				handlers.append(memb)
	return handlers

def searchForFilters(o):
	filters = []
	if type(o) == types.ModuleType:
		for (name, memb) in inspect.getmembers(o):
			if isFilter(memb):
				filters.append(memb)
			if type(memb) == types.InstanceType:
				filters += searchForHandlers(memb)
	elif type(o) == types.InstanceType:
		for (name, memb) in inspect.getmembers(o):
			if isFilter(memb):
				filter.append(memb)
	return filters

class NoSuchFilterError(Exception):
	def __init__(self, name):
		self.name = name
	
	def __str__(self):
		return 'No filter named %s' % repr(self.name)

def gen_error_code():
	return '%03d-%03d-%03d' % (
		random.randint(0,999),
		random.randint(0,999),
		random.randint(0,999)
	)
