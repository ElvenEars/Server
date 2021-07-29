import socket

class ServerSocket(object):

    def __init__(self, ip , port):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))

    def recive(self):
        data, addr = self.sock.recvfrom(1024)
        return data, addr

    def send(self, data, addr):
        self.sock.sendto(data, addr)
