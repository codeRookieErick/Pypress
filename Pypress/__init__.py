from .Http import *
import re
import os


class Router:
    baseRoutes = {}

    def __init__(self):
        self.routes = Router.baseRoutes
        self.stack = []


class Application(Server):
    baseRoutes = {}

    def __init__(self, connectionTimeout=None):
        Server.__init__(self, connectionTimeout)
        self.routes = Application.baseRoutes
        self.stack = []

    def register_function(self, httpMethod, route):
        def inner(function):
            if httpMethod.upper() not in Application.baseRoutes:
                Application.baseRoutes[httpMethod.upper()] = {route: function}
            else:
                Application.baseRoutes[httpMethod.upper()][route] = function
            return function

        return inner

    def get(self, route):
        return self.register_function('GET', route)

    def post(self, route):
        return self.register_function('POST', route)

    def use(self, handler):
        self.stack.append(handler)

    def __getattr__(self, method):
        def inner(route):
            return self.register_function(method.upper(), route)
        return inner

    def onReceive(self, clientPort, data):
        req = None
        res = HttpResponse()
        try:
            req = HttpRequest(data)
        except Exception as e:
            print(e)
            print(data)
            res.status(403, "BadRequest")
            clientPort.send(str(res).encode())
            return

        stack = self.stack.copy()

        def next():
            if len(stack) > 0:
                stack.pop()(self, req, res, next)

        if req.method in self.routes:
            regularPaths = [i for i in self.routes[req.method]]
            for route in regularPaths:
                pattern = re.sub(r":([\w]+)", r"(?P<\1>[\\w]+)", route)
                pattern = "^" + pattern + "$"
                match = re.match(pattern, req.path)
                if match:
                    handler = self.routes[req.method][route]
                    queryParams = match.groupdict()
                    for i in queryParams:
                        req.params[i] = queryParams[i]

                    def middleware(app, req, res, next):
                        res.status(200, "OK")
                        handler(app, req, res)
                        next()
                    stack.append(middleware)
                    break

        stack.reverse()
        next()
        clientPort.send(str(res).encode())


def body_parser(app: Application, req: HttpRequest, res: HttpResponse, next):
    print(req.body)
    next()


contentTypes = {
    "text/": ["html", "css"],
    "text/javascript": ["js"],
    "text/html": ["htm"],
    "application/": ["json", "xml", "pdf"],
    "image/": ["gif", "png", "jpeg", "bmp", "webp"],
    "image/jpeg": ["jpg"],
    "audio/": ["mpeg", "webm", "ogg", "midi", "wav"],
    "text/plain": ["txt", "*"]
}


def static_files(folder: str):
    def result(app: Application, req: HttpRequest, res: HttpResponse, next):
        fileToSearch = os.sep.join([folder, req.path])
        if os.path.isfile(fileToSearch):
            extension = fileToSearch.split(".")[-1:][0]
            contentType = 'text/plain'
            for i in contentTypes:
                if extension in contentTypes[i]:
                    contentType = i
                    if contentType.endswith("/"):
                        contentType += extension
                    break
            res.readFile(fileToSearch, contentType)
        else:
            next()
    return result


def header_inspector(headerName: str):
    def result(app: Application, req: HttpRequest, res: HttpResponse, next):
        if headerName in req.headers:
            print(f'{headerName}: {req.headers[headerName]}')
        next()
    return result


def body_inspector(app: Application, req: HttpRequest, res: HttpResponse, next):
    print(req.body)
    next()
