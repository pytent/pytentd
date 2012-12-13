''' Defines errors for tentd. '''

class TentError(Exception):
	def __init__(self, reason, status):
		self.reason = reason
		self.status = status
	def __str__(self):
		return 'HTTP Status: {0}\nReason: {1}'.format(self.status, self.reason)
