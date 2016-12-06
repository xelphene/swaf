
import logging
import urllib
import httplib

import swaf

log = logging.getLogger('swaf.filters.recap')

def do_recap_call(privatekey, remoteip, challenge, response):
	params = {
		'privatekey': privatekey,
		'remoteip': remoteip,
		'challenge': challenge,
		'response': response
	}
	params_str = urllib.urlencode(params)
	headers = {
		'Content-Type': 'application/x-www-form-urlencoded'
	}

	c = httplib.HTTPConnection('www.google.com',80)
	#c = httplib.HTTPConnection('localhost', 89)
	c.request('POST', '/recaptcha/api/verify', params_str, headers)
	
	r = c.getresponse()
	body = r.read()
	for line in body.split('\n'):
		logging.debug('recap: %s' % repr(line))
	return body.split('\n')

def check_req(req):
	'''does the request res look like it has a captcha to verify?'''

	if req['method']!='POST':
		log.debug('not a candidate form. request method is %s, not POST' % repr(req['method']))
		return (False, 'not a candidate form. request method is %s, not POST' % repr(req['method']) )

	postform = req['postform']
	
	challenge_present = (
		postform.has_key('recaptcha_challenge_field') and
		len(postform['recaptcha_challenge_field']) > 0 and
		len(postform['recaptcha_challenge_field'][0]) > 0
	)

	if not challenge_present:
		log.debug('recaptcha_challenge_field not present in posted form')
		return False, 'recaptcha_challenge_field not present in posted form'

	response_present = (
		postform.has_key('recaptcha_response_field') and
		len(postform['recaptcha_response_field']) > 0 and
		len(postform['recaptcha_response_field'][0]) > 0
	)

	if not response_present:
		log.debug('recaptcha_response_field not present in posted form')
		return False, 'recaptcha_response_field not present in posted form'
	
	return True, ''

def do_recap(privatekey, remoteaddr, challenge, response):
	try:
		recap_response = do_recap_call(
			privatekey,
			remoteaddr,
			challenge,
			response
		)
	except Exception, e:
		return {
			'passed': False,
			'attempted': True,
			'valid_result': False,
			'explanation': 'Exception while making call to recaptcha service: %s' % str(e),
			'recaptcha_error_code': 'recaptcha-not-reachable'
		}

	if len(recap_response) < 2:
		return {
			'passed': False,
			'attempted': True,
			'valid_result': False,
			'explanation': 'recaptcha service returned in invalid result (<2 lines). recaptcha service response was %s' % repr('\n'.join(recap_response)),
			'recaptcha_error_code': ''
		}
	
	if recap_response[0]=='true':
		return {
			'passed': True,
			'attemped': True,
			'valid_response': True,
			'explanation': 'success',
			'recaptcha_error_code': recap_response[1]
		}

	elif recap_response[0]=='false':	
		return {
			'passed': False,
			'attemped': True,
			'valid_response': True,
			'explanation': 'recaptcha service returned error %s' % repr(recap_response[1]),
			'recaptcha_error_code': recap_response[1]
		}
	else:
		return {
			'passed': False,
			'attempted': True,
			'valid_response': False,
			'explanation': 'recaptcha service returned in invalid result (line 1 is neither "true" nor "false"). recaptcha service response was %s' % repr('\n'.join(recap_response)),
			'recaptcha_error_code': ''
		}

def make_recap_filter(privatekey):
	@swaf.filter('recaptcha', filters='basic postform')
	def validate_recaptcha(req, next):
		
		postform = req['postform']
		
		(attempt, reason_not_attempted) = check_req(req)
		
		if attempt:
			challenge = postform['recaptcha_challenge_field'][0]
			response  = postform['recaptcha_response_field'][0]
			result = do_recap(privatekey, req['remoteaddr'], challenge, response)
			req['recaptcha'] = result
			return next(req)

		else:
			req['recaptcha'] = {
				'passed': False,
				'attempted': False,
				'valid_result': False,
				'explanation': 'not attempted; %s' % reason_not_attempted,
				'recaptcha_error_code': ''
			}
			return next(req)
		
	return validate_recaptcha
	