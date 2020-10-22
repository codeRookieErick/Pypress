from .Http import *


class Application(Server):
    baseRoutes = {}

    def __init__(self, connectionTimeout=None):
        Server.__init__(self, connectionTimeout)
        self.routes = Application.baseRoutes
        self.stack = []

    def register_function(httpMethod, route):
        def inner(function):
            if httpMethod.upper() not in Application.baseRoutes:
                Application.baseRoutes[httpMethod.upper()] = {route: function}
            else:
                Application.baseRoutes[httpMethod.upper()][route] = function
            return function

        return inner

    def get(route):
        return Application.register_function('GET', route)

    def post(route):
        return Application.register_function('POST', route)

    def use(self, handler):
        self.stack.append(handler)

    def __getattr__(self, item):
        item = item.upper()
        if not item in self.routes:
            self.routes[item] = {}

        def result(route, handler):
            self.routes[item][route] = handler

        return result

    def onReceive(self, clientPort, data):
        req = HttpRequest(data)
        res = HttpResponse()
        stack = self.stack.copy()

        def next():
            if len(stack) > 0:
                stack.pop()(self, req, res, next)

        if req.method in self.routes:
            if req.path in self.routes[req.method]:
                handler = self.routes[req.method][req.path]

                def middleware(app, req, res, next):
                    handler(app, req, res)
                    next()

                stack.append(middleware)

        next()
        clientPort.send(str(res).encode())