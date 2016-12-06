
import os
import cgi
import pprint
import Cookie
import base64
import copy
import logging

from swaf.resp import *
import swaf

@swaf.filter('basic')
def wsgi_basic(req, next):
	req['remoteaddr'] = req['wsgienv'].get('REMOTE_ADDR')
	req['method'] = req['wsgienv'].get('REQUEST_METHOD')
	req['query'] = req['wsgienv'].get('QUERY_STRING')
	req['body'] = req['wsgienv'].get('wsgi.input')
	req['path'] = req['wsgienv'].get('PATH_INFO')
	req['cookies'] = req['wsgienv'].get('HTTP_COOKIE')
	if req['cookies'] != None:
		req['cookies'] = Cookie.SimpleCookie(req['cookies'])
	else:
		req['cookies'] = Cookie.SimpleCookie()
	return next(req)

def requireMethod(method):
	@swaf.filter('require_method_'+method.lower(), filters='basic')
	def _requireMethod(req, next):
		if req['method']==method:
			return next(req)
		else:
			return wrongMethod()
	return _requireMethod

get = requireMethod('GET')
post = requireMethod('POST')

def postform(read_max=8192):
	@swaf.filter(filters='basic')
	def _postform(req, next):
		if req['method']=='POST':

			if req['wsgienv'].has_key('CONTENT_TYPE'):
				ctype, pdict = cgi.parse_header('Content-Type: %s' % req['wsgienv']['CONTENT_TYPE'])
				logging.info('postform: content-type=%s' % repr(ctype))
			else:
				logging.info('postform: no content-type')
				ctype=None
				pdict = {}
			
			if ctype=='content-type: multipart/form-data':
				f = cgi.parse_multipart(req['wsgienv']['wsgi.input'], pdict)
				req['postform'] = f
			else:
				body = req['body'].read(read_max)
				req['postform'] = cgi.parse_qs(body)
		else:
			req['postform'] = {}
		return next(req)
	return _postform

@swaf.filter('asciiform')
def asciiform(req, next):
	if req.has_key['postform'] and type(req['postform'])==dict:
		for k in req['postform'].keys():
			if type(req['postform'][k]) == list:
				new_values = []
				for v in req['postform'][k]:
					if type(v) == str:
						v = swaf.util.asciiize(v)
					new_values.append(v)
				req['postform'][k] = new_values
		return next(req)
	else:
		return next(req)

def rawpost(read_max=8192):
	@swaf.filter(filters='basic')
	def _rawpost(req, next):
		if req['method']=='POST':
			body = req['body'].read(read_max)
			req['body_str'] = body
		else:
			req['body_str'] = ''
		return next(req)
	return _rawpost

@swaf.filter(filters='basic')
def query(req, next):
	if req.has_key('query') and req['query']:
		req['query'] = cgi.parse_qs( req['query'] )
	else:
		req['query'] = {}
	return next(req)

@swaf.filter(filters='basic')
def cookies(req, next):
	if req.has_key('cookies') and req['cookies']:
		req['cookies'] = Cookie.SimpleCookie(req['cookies'])
	return next(req)

@swaf.filter()
def auth(req, next):

	'''NOTE: for this to work you have to do "WSGIPassAuthorization On" in
	the apache conf file.'''

	if req['wsgienv'].has_key('HTTP_AUTHORIZATION'):
		(authtype, authdata) = req['wsgienv']['HTTP_AUTHORIZATION'].split(' ',1)
		if authtype=='Basic':
			ds = base64.decodestring(authdata)
			parts = ds.split(':',1)
			if len(parts)==2:
				req['auth'] = {
					'present': True,
					'username': parts[0],
					'password': parts[1]
				}
			else:
				req['auth'] = {
					'present': True,
					'username': parts[0],
					'password': ''
				}
		else:
			req['auth'] = {
				'present': False,
				'username': '',
				'password': ''
			}
	else:
		req['auth'] = {
			'present': False,
			'username': '',
			'password': ''
		}
			
	return next(req)

@swaf.filter()
def wsgidump(req, next):
	if 'WSGI_DUMP' in req['wsgienv']['QUERY_STRING']:
		dump = ''
		keys = req['wsgienv'].keys()
		keys.sort()
		for k in keys:
			dump += '%s = %s\n' % (k, repr(req['wsgienv'][k]))
		return plain(dump)
	else:
		return next(req)

def PkgMakoTemplates(mod, mod_dir='/tmp'):
	import mako.lookup
	path = os.path.join(mod.__path__[0], 'tmpl')
	tl = mako.lookup.TemplateLookup(
		directories = [path],
		module_directory = mod_dir
	)
	
	@swaf.filter('tmpl')
	def tmpl(req, next):
		def trender(path, **kwargs):
			targs = copy.copy(req)
			targs.update(kwargs)
			#logging.info('TARGS: %s' % repr(targs))
			t = tl.get_template(path)
			return html( t.render(**targs) )

		def trender_raw(path, **kwargs):
			targs = copy.copy(req)
			targs.update(kwargs)
			#logging.info('TARGS: %s' % repr(targs))
			t = tl.get_template(path)
			return t.render(**targs)
		
		req['trender'] = trender
		req['trender_raw'] = trender_raw
		return next(req)
	
	return tmpl

def DirMakoTemplates(dirpath, mod_dir='/tmp'):
	path = dirpath
	import mako.lookup
	tl = mako.lookup.TemplateLookup(
		directories = [path],
		module_directory = mod_dir
	)
	
	@swaf.filter('tmpl')
	def tmpl(req, next):
		def trender(path, **kwargs):
			targs = copy.copy(req)
			targs.update(kwargs)
			#logging.info('TARGS: %s' % repr(targs))
			t = tl.get_template(path)
			return html( t.render(**targs) )

		def trender_raw(path, **kwargs):
			targs = copy.copy(req)
			targs.update(kwargs)
			#logging.info('TARGS: %s' % repr(targs))
			t = tl.get_template(path)
			return t.render(**targs)
		
		req['trender'] = trender
		req['trender_raw'] = trender_raw
		return next(req)
	
	return tmpl

import sys
def writeLog(msg):
	sys.stderr.write('%s\n' % msg)

@swaf.filter('errlog')
def add_apache_error_log(req, next):
	req['errlog'] = writeLog
	return next(req)

def make_adder(name, value):
	@swaf.filter(name)
	def add_value(req, next):
		req[name] = value
		return next(req)
	return add_value
