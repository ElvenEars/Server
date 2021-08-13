from ServerSocket import ServerSocket
from Sip import SIP
from threading import Thread
from Configuration import Configuration

def main():
    SipSocket = ServerSocket(Configuration().server_ip, Configuration().server_port)
    sipProcess = Thread(target=SIP, args=(SipSocket,))
    sipProcess.start()

if __name__ == '__main__':
    main()
