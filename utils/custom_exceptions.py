class error_400(Exception):
    def __init__(self, message="400 Bad Request"):
        self.message = message
        super().__init__(self.message)


class error_401(Exception):
    def __init__(self, message="401 Unauthorized"):
        self.message = message
        super().__init__(self.message)


class error_403(Exception):
    def __init__(self, message="403 Forbidden"):
        self.message = message
        super().__init__(self.message)


class error_404(Exception):
    def __init__(self, message="404 Not Found"):
        self.message = message
        super().__init__(self.message)


class error_409(Exception):
    def __init__(self, message="409 Conflict"):
        self.message = message
        super().__init__(self.message)


class error_415(Exception):
    def __init__(self, message="415 Unsupported Media Type"):
        self.message = message
        super().__init__(self.message)


class error_500(Exception):
    def __init__(self, message="500 Internal server error"):
        self.message = message
        super().__init__(self.message)