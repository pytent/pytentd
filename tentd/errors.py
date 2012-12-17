class TentError(Exception):
    def __init__(self, message, status):
        self.reason = message
        self.status = status
