import os
from Pypress.Http import HttpRequest, HttpResponse
from Pypress import Application, static_files

port = 6088
try:
    port = int(os.environ['PORT'])
except:
    pass


class MyApp(Application):
    def __init__(self):
        Application.__init__(self)

    @Application.get('/list')
    def getList(self, req: HttpRequest, res: HttpResponse):
        res.json([i for i in range(0, 10)])

    @Application.get('/:id?')
    def main(self, req: HttpRequest, res: HttpResponse):
        res.json({"Method": "Get"})

    @Application.post("/:id?")
    def index(self, req: HttpRequest, res: HttpResponse):
        res.readFile("server.py")


def middleware(app: MyApp, req: HttpRequest, res: HttpResponse, next):
    res.headers['Special'] = 'This request is special'
    next()


app = MyApp()
app.use(middleware)
app.use(static_files('./static'))
app.listen(port)
