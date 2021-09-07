import socket
from Configuration import Configuration
from datetime import datetime

class ServerSocket(object):

    def __init__(self, ip = Configuration().server_ip , port = 0, bind = True):
        self.ip = ip
        self.port = port
        self.addr = (ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.rtp_seq_int = 0
        self.rtp_time_int = 1631013671
        if bind:
            self.sock.bind((self.ip, int(self.port)))

    def recive(self):
        data, addr = self.sock.recvfrom(1024)
        return data, addr

    def send(self, data, addr):
        self.sock.sendto(data, addr)

