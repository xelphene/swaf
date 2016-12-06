
import simplejson
import Cookie
import datetime
import random
import sha

import swaf

def make_get_put_pg(dbh):

	'''Given a postgresql psycopg2 database handle, return functions that
	will add and retrieve swaf sessions to/from it. the returned functions
	will be a suitable get/put parameters to make_session_filter. The return
	value will be a (get,put) tuple of functions.
	
	These functions assume there is a table called "session" in the
	connected database with "sessionid" and "data" columns of some string
	type.'''
	
	def put(sessionid, data):
		if type(sessionid)!=str:
			raise TypeError('string required for sessionid parameter')
		if type(data)!=str:
			raise TypeError('string required for data parameter')

		cur = dbh.cursor()
		sql = '''
			select count(*) from session where sessionid=%s
		'''
		cur.execute(sql, (sessionid,))
		row = cur.fetchone()
		count = int(row[0])
		
		if count==0:
			sql = '''
				insert into session(sessionid, data, lastuse)
				values(%s, %s, now())
			'''
			cur.execute(sql, (sessionid, data))
			dbh.commit()
		else:
			sql = '''
				update session set
					data=%s,
					lastuse=now()
				where sessionid=%s
			'''
			cur.execute(sql, (data, sessionid))
			dbh.commit()
	
	def get(sessionid):
		if type(sessionid)!=str:
			raise TypeError('string required for sessionid parameter')
		sql = '''
			select data from session where sessionid=%s
		'''

		cur = dbh.cursor()
		cur.execute(sql, (sessionid,))
		row = cur.fetchone()
		if row:
			return str(row[0])
		else:
			return None
	
	return (get, put)

def make_session_filter_pg(dbh, init):

	''' given:
	
		dbh: a psycopg2 database handle connected to a PostgreSQL database
		with a "session" table with "sessionid" and "data" columns of string
		types
		
		init: a function which returns a data structure/object that is a
		blank session.
		
		return a swaf filter that does sessions.
	'''
	
	(get, put) = make_get_put_pg(dbh)
	return make_session_filter(get, put, init)
		
def gen_sessionid():
	c1 = str(random.random())
	c2 = str(datetime.datetime.now())
	hash = sha.new()
	hash.update(c1)
	hash.update(c2)
	return hash.hexdigest()
		
def serialize_session(session):
	return simplejson.dumps(session)

def deserialize_session(session):
	return simplejson.loads(session)
		
def make_session_filter(get, put, init):

	'''
		get: a function which takes a session ID and returns a session
		data string or None if no session with that ID exists.
		
		put: a function which takes a session ID and string and stores it
		
		init: a function which takes no arguments but returns a new, blank
		session object.
	'''

	@swaf.filter('session', 'basic')
	def session(req, next):
		if req['cookies'].has_key('sessionid'):
			sessionid = req['cookies']['sessionid'].value
			session = get(sessionid) 
			if session==None:
				session = init()
				sessionid = gen_sessionid()
				set_cookie = True
				put(sessionid, serialize_session(session))
			else:
				session = deserialize_session(session)
				set_cookie = False
		else:
			session = init()
			sessionid = gen_sessionid()
			put(sessionid, serialize_session(session))
			set_cookie = True
			
		req['session'] = session
		req['sessionid'] = sessionid
		resp = next(req)
		if resp.has_key('session'):
			session = resp['session']
		session = serialize_session(session)
		put(sessionid, session)
		
		if set_cookie:
			c = Cookie.SimpleCookie()
			c['sessionid'] = sessionid
			c = c.output(header='').strip()
			header = ('Set-Cookie', c)
			resp['headers'].append(header)
		
		return resp
	
	return session
	