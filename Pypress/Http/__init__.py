from functools import reduce
import json
import socket


class HttpResponse:
    def __init__(self):
        self.resposeStatus = 404
        self.resposeText = 'NotFound'
        self.headers = {
            "Content-Type": "text/plain",
            "Conten-Length": "0",
            "Connection": "close"
        }
        self.body = ""

    def status(self, resposeStatus, resposeText=None):
        self.resposeStatus = resposeStatus
        self.resposeText = None or 'OK'
        return self

    def contentType(self, value):
        self.headers["Content-Type"] = value
        return self

    def json(self, data):
        self.body = json.dumps(data)
        return self.contentType("text/json")

    def write(self, data):
        self.body += data
        return self

    def __str__(self):
        result = f"HTTP/1.1 {self.resposeStatus} {self.resposeText}\n"
        self.headers["Content-Length"] = len(self.body)
        if len(self.headers) > 0:
            mappedHeaders = [f"{i}:{self.headers[i]}\n" for i in self.headers]
            result += reduce(lambda a, b: a + b, mappedHeaders)
        result += '\n'
        result += self.body
        return result


class HttpRequest:
    def __init__(self, raw):
        self.raw = raw
        headerAndBody = self.raw.split('\n\n', 1)
        self.headers = headerAndBody[0].split('\n')
        if len(headerAndBody) > 1:
            self.body = headerAndBody[1]
        else:
            self.body = ''
        firstLine = self.headers[:1][0].split(' ')
        self.headers = self.headers[1:]
        self.method = firstLine[0]
        self.httpVersion = firstLine[2] if len(firstLine) >= 2 else 'HTTP/1.1'
        self.url = firstLine[1] if len(firstLine) >= 1 else ''
        self.querystring = self.url.split('?', 1)[1] if '?' in self.url else ''
        self.path = self.url.split('?')[:1][0]
        self.queryParameters = dict([
            tuple([j.strip() for j in i.split('=', 1)])
            for i in self.querystring.split('&') if len(i.split('=')) == 2
        ])
        self.headers = dict([
            tuple([j.strip() for j in i.split(':', 1)]) for i in self.headers
            if len(i.split(':')) == 2
        ])


class Server:
    def __init__(self, connectionTimeout=None):
        self.connectionTimeout = connectionTimeout or 0.1
        self.maxPacket = 32768

    def __del__(self):
        self.serverSocket.close()

    def onConnect(self, clientPort):
        pass

    def onReceive(self, clientPort, data):
        raise NotImplementedError()

    def receive(self, clientPort):
        rdata = []
        timeout = clientPort.gettimeout()
        try:
            clientPort.settimeout(self.connectionTimeout)
            while True:
                try:
                    rdata.append(clientPort.recv(self.maxPacket))
                except:
                    break
        finally:
            clientPort.settimeout(timeout)
        raw = ''.join([i.decode() for i in rdata])
        return ''.join([i + '\n' for i in raw.splitlines()])

    def listen(self, port):
        print(f'listening on {port}...')
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind(('', port))
        self.serverSocket.listen(5)
        while True:
            (clientSocket, address) = self.serverSocket.accept()
            self.onConnect(clientSocket)
            try:
                raw_data = self.receive(clientSocket)
                self.onReceive(clientSocket, raw_data)
            except socket.timeout:
                continue
            except Exception as e:
                break
            finally:
                clientSocket.close()
