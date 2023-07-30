import sys
import socket as soc

class Request:
    def __init__(self, socket, dataBase):
        self.socket = socket
        self.dataBase = dataBase
        self.buffer = b""

    def get_buffer(self):
        while self.buffer.find(b"  ") == -1:
            self.buffer += self.socket.recv(2048)
            if len(self.buffer) == 0:
                return b""
        endOfHeader = self.buffer.find(b"  ")
        header = self.buffer[0: endOfHeader]
        self.buffer = self.buffer[endOfHeader+2:]
        return header

    def process_header(self):
        header = ""
        method = ""
        keyOrCounter = ""
        path = b""
        content_body = b"" 
        
        dataBytes = self.get_buffer()
        if len(dataBytes) == 0:
            return ()
        header = dataBytes.split(b' ')
        content_body_index = dataBytes.find(b"  ")
        #Gets whether isit GET/POST/DELETE
        method = header[0].decode().lower()
        #finds the index of the second '/' 
        keyOrCounterIndex = header[1].find(b'/',1)
        #the keyOrCounter in the header[1]
        KeyOrCounter = header[1][1: keyOrCounterIndex].decode()
        #the remaining path
        path = header[1][keyOrCounterIndex+1:]
        if method == "post":
            #find all the indexes of "Content-Length"
            for i in range(0,len(header)):
                curr = header[i].decode()
                if curr.lower() == "content-length":
                    try:
                        content_length = int(header[i+1].decode())
                        while len(self.buffer) < content_length:
                            self.buffer += self.socket.recv(content_length - len(self.buffer))
                        content_body = self.buffer[:content_length]
                        self.buffer = self.buffer[content_length:]
                        print(self.buffer)
                        break
                    except ValueError:
                        continue
        return (method, KeyOrCounter, path, content_body)

    def execute_header(self, method, keyOrCounter, path, content_body):
        if(method == "get"):
            if(keyOrCounter == "key"):
                if path in self.dataBase.counter:
                    count = self.dataBase.counter.get(path) - 1
                    if count == 0:
                        self.dataBase.counter.pop(path)
                        key = self.dataBase.key.pop(path)
                        return b"200 " + b"Ok " + b"Content-Length " + str(len(key)).encode() + b"  " + key
                    else:
                        self.dataBase.counter[path] = count
                if path in self.dataBase.key:
                    return  b"200 " + b"OK " + b"Content-Length " + str(len(self.dataBase.key.get(path))).encode() + b"  " + self.dataBase.key.get(path)
                else:
                    return b"404 NotFound  "
            if(keyOrCounter == "counter"):
                if path in self.dataBase.counter:
                    return b"200 " + b"OK " + b"Content-Length " + str(len(str(self.dataBase.counter.get(path)))).encode() + b"  " + str(self.dataBase.counter.get(path)).encode()
                
                if path in self.dataBase.key:
                    return b"200 " + b"OK " + b"Content-Length " + str(len("Infinity")).encode() + b"  " + b"Infinity"
                else :
                    return b"404 NotFound  "
        if(method == "post"):
            if(keyOrCounter == "key"):
                if path in self.dataBase.counter:
                    return b"405 " + b"MethodNotAllowed  "
                else:
                    self.dataBase.key[path] = content_body
                    return b"200 " + b"OK  "
            if(keyOrCounter == "counter"):
                if path not in self.dataBase.key:
                    return b"405 + MethodNotAllowed"
                self.dataBase.counter[path] = self.dataBase.counter.get(path, 0) + int(content_body.decode())
                return b"200 " + b"OK  "
        if(method == "delete"):
            if(keyOrCounter == "key"):
                if path not in self.dataBase.key:
                    return b"404 " + b"NotFound  "
                if path in self.dataBase.counter:
                    return b"405 " + b"MethodNotAllowed  "
                else:
                    byte = self.dataBase.key.pop(path)
                    return b"200 " + b"OK " +b"Content-Length " + str(len(byte)).encode() + b"  "+ byte    
            if(keyOrCounter == "counter"):
                if path not in self.dataBase.counter:
                    return b"404" + b"NotFound  "
                else:
                    content_len = len(str(self.dataBase.counter[path]))
                    content = self.dataBase.counter.pop(path)
                    return b"200 " + b"OK " + b"Content-Length " + str(content_len).encode() + b"  " + str(content).encode()
        else:
            return b"error"
class Database:
    def __init__(self) -> None:
        self.key = {}
        self.counter = {}

def main():
    webServer = WebServer(int(sys.argv[1]))
    webServer.execute()

if __name__ == "__main__":
    main()
