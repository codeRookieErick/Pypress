import os
from Pypress.Http import HttpRequest, HttpResponse
from Pypress import Application, static_files

port = 6088
try:
    port = int(os.environ['PORT'])
except:
    pass


def middleware(app: Application, req: HttpRequest, res: HttpResponse, next):
    res.headers['Special'] = 'This request is special'
    next()


app = Application()

app.use(middleware)
app.use(static_files('./static'))


@app.get('/list')
def get_list(self, req: HttpRequest, res: HttpResponse):
    res.json([i for i in range(0, 10)])


@app.get('/:id?')
def main(self, req: HttpRequest, res: HttpResponse):
    res.json({"Method": "Get"})


app.listen(port)
