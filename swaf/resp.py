
codes = {
	307: 'Temporary Redirect',
	303: 'See Other',
	302: 'Found',
	301: 'Moved Permanently'
}


def authRequired(realm):
	return {
		'status': 401,
		'reason': 'Authentication Required',
		'headers': [
			('Content-type','text/plain'),
			('WWW-Authenticate', 'Basic realm="%s"' % realm)
		],
		'body': 'Authentication required.'
	}				

def redirect(url, status=303):
	if status not in codes.keys():
		raise ValueError('redirect called with unknown status value')
	return {
		'status': status,
		'reason': codes[status],
		'headers': [
			('Content-type', 'text/plain'),
			('Location', url)
		],
		'body': 'Moved to %s' % url
	}

def wrongMethod():
	return {
		'status': 405,
		'reason': 'Method Not Allowed',
		'headers': [('Content-type', 'text/plain')],
		'body': 'The request was issued with a method not allowed for this resource.'
	}	

def css(body):
	return ok('text/css', body)

def plain(body):
	return ok('text/plain', body)

def html(body):
	return ok('text/html', body)

def ok(ctype, body):
	return {
		'status': 200,
		'reason': 'OK',
		'headers': [('Content-type',ctype)],
		'body': body
	}

def notFound():
	return {
		'status': 404,
		'reason': 'Not Found',
		'headers': [('Content-type','text/plain')],
		'body': 'The requested resource cannot be found.'
	}
notfound = notFound

def forbidden():
	return {
		'status': 403,
		'reason': 'Forbidden',
		'headers': [('Content-type','text/plain')],
		'body': 'You do not have access to the requested resource.'
	}

def is_a_resp(x):
	if type(x)!=dict:
		return False
	if not x.has_key('status'):
		return False
	if not x.has_key('reason'):
		return False
	if not x.has_key('body'):
		return False
	if not x.has_key('headers'):
		return False

def error_verbose(code=None, report=None):
	r = {
		'status': 500,
		'reason': 'Internal Server Error',
		'headers': [('Content-type','text/plain')],
		'body': '500 Internal Server Error. Error code: %s.' % str(code)
	}

	r['body'] += '\n\n-------------------------------------------\n'
	r['body'] += 'Error Detail:\n\n'
	r['body'] += '\n'.join(report)

	return r	

def error_vague(code=None):
	r = {
		'status': 500,
		'reason': 'Internal Server Error',
		'headers': [('Content-type','text/plain')],
		'body': '500 Internal Server Error. Error code: %s.' % str(code)
	}
	
	return r
		