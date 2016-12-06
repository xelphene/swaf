
def htmlesc(s):
	s = s.replace('&','&amp;')
	s = s.replace('<','&lt;')
	s = s.replace('>','&gt;')
	s = s.replace('"','&#34;')
	s = s.replace("'",'&#39;')
	return s

def asciiize(s):

	'''given an arbitrary string containing text of an unknown encoding,
	munge it as best as we can to plain printable ascii.  unknown characters
	will be removed.  changes CP1252 and unicode curly quotes and dashes to
	their nearest ascii equivalent.  a string containing only printable
	ascii characters (bytes 32-126 inclusive), \n and \t will be returned.'''

	s = str(s)

	#
	# replace what we know how to replace
	#

	reptable = [
		('\xe2\x80\x93', '-'),
		('\x91', "'"),
		('\x92', "'"),
		('\x93', '"'),
		('\x94', '"'),
		('\x96', '-'),
		('\x97', '-'),
		('\x85', '...')
	]
	for (searchkey, replacement) in reptable:
		try:
			s = s.replace(searchkey, replacement)
		except UnicodeDecodeError, ude:
			raise Exception('Unicode error: %s for string %s' % (
				str(ude), repr(s)
			))

	#
	# strip everything else out if it isn't printable ascii
	#

	ss = ''
	for c in s:
		if ord(c) >= 32 and ord(c) <= 126:
			ss += c
		elif c == '\n':
			ss += c
		elif c == '\t':
			ss += c
		else:
			pass

	return ss

