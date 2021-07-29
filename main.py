from ServerSocket import ServerSocket
from Sip import SIP


def main():
    SipSocket = ServerSocket("10.21.10.125", 19888)
    SIP(SipSocket)



if __name__ == '__main__':
    main()
