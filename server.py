import os
from Pypress.Http import *
from Pypress import Application
from typing import *

port = 6088
try:
    port = int(os.environ['PORT'])
except:
    pass


class MyApp(Application):
    def __init__(self):
        Application.__init__(self)

    @Application.get('/')
    def main(self, req: HttpRequest, res: HttpResponse):
        res.json({"Json": "Object"})

    @Application.get('/list')
    def getList(self, req: HttpRequest, res: HttpResponse):
        res.json([i for i in range(0, 10)])


def middleware(app: MyApp, req: HttpRequest, res: HttpResponse, next):
    res.headers['Special'] = 'This request is special'
    next()


app = MyApp()
app.use(middleware)
app.listen(port)