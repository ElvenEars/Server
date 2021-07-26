from ServerSocket import ServerSocket
from Log import Log
from Sip import SipMessage
from threading import Thread
import struct
import time
FLAGE = False

class SIP(object):
    def __init__(self, SipSocket, sip_message):
        self.SipSocket = SipSocket
        self.sip_message = sip_message
        self.sip_thread(SipSocket, sip_message)

    def sip_thread(self, SipSocket, sip_message):
        while True:

            self.sip_logic(SipSocket, sip_message)

    def sip_logic(self, SipSocket, sip_message):
        sipData, sipAddr = SipSocket.recive()
        msg = sipData.decode()
        sip_message.parse(msg)
        Log().to_log(sip_message.get_method())

        if sip_message.get_method() == "REGISTER":
            SipSocket.send(sip_message.make_OK().encode(), sipAddr)

        if sip_message.get_method() == "OPTIONS":
            SipSocket.send(sip_message.make_OK().encode(), sipAddr)
            SipSocket.send(sip_message.make_invite().encode(), sipAddr)

        if sip_message.get_method() == "BYE":
            SipSocket.send(sip_message.make_OK().encode(), sipAddr)

        if sip_message.get_method() == "200":
            pass

        if sip_message.get_method() == "400":
            Log().to_log(sip_message.get_method())
            SipSocket.send(sip_message.make_OK().encode(), sipAddr)

        if sip_message.get_method() == "MESSAGE":
            Log().to_log(sip_message.get_message())
            Log().to_log(sip_message.get_ais_msg_id())
            SipSocket.send(sip_message.make_OK().encode(), sipAddr)

        if sip_message.get_method() == "INVITE":
            SipSocket.send(sip_message.make_trying().encode(), sipAddr)
            SipSocket.send(sip_message.make_ringing().encode(), sipAddr)
            sip_message.add_body("v=0\r\no=1001 0 0 IN IP4 10.21.10.125\r\ns=A conversation\r\nc=IN IP4 10.21.10.125\r\nt=0 0\r\nm=audio 30000 RTP/AVP 8\r\na=rtpmap:8 PCMA/8000")
            SipSocket.send(sip_message.make_OK().encode(), sipAddr)

        if sip_message.get_method() == "100":
            SipSocket.send(sip_message.make_ack().encode(), sipAddr)
            pass

        if sip_message.get_method() == "180":
            pass

class RTP (object):

    def __init__(self, RtpSocket,sip_message):
        self.data = b''
        self.RtpSocket = RtpSocket
        self.rtp_seq_int = 34026
        self.rtp_time_int = 4150191817
        self.rtp_thread()

    def toWav(self, data):
        _file = b'RIFF'
        datalength = len(data)
        _audioformat = 6
        _numofchannels = 1
        _samplerate = 8000
        _bitspersample = 8
        _file += (struct.pack('<L4s4sLHHLLHHH4sLL4s',
                              50 + datalength, b'WAVE', b'fmt ', 18,
                              _audioformat, _numofchannels, _samplerate,
                              int(_numofchannels * _samplerate * (_bitspersample / 8)),
                              int(_numofchannels * (_bitspersample / 8)), _bitspersample, 0,
                              b'fact', 4,
                              datalength, b'data'))

        _file += (struct.pack('<L', datalength))
        _file += (data)
        return _file

    def rtp_logic(self):
        rtpData, rtpAddr = self.RtpSocket.recive()
        start = b'\x90\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe0\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x006\x00\x00\x00\x02\x00\x03\xe8'

        if rtpData != start:
            end = b'\x13\x03\x00\x00\x00\x00\x00\x00'
            extra = b'\xec'
            if len(rtpData) != 48 and rtpData[47] != extra:
                self.data += rtpData[43:]

            if len(rtpData) == 48 and rtpData[40:] == end and len(self.data) != 0:
                print(len(self.data))
                wav = open("test.wav", "wb")
                wav.write(self.toWav(self.data))
                wav.close()
                wav = open("test_test.wav", "wb")
                wav.write(self.data)
                wav.close()
                self.data = b''
            Log().to_log(str(rtpData))
        else:
            wav = open("test_test.wav", 'rb')
            timespan = 480
            rtp_version = b'\x90\x08'
            rtp_sync = b'\x4e\x2e\x19\xd9'
            rtp_profile = b'\xe0\x00'
            rtp_ext = b'\x00\x06\x01\x00\x00\x64\x00\xff\xfa\xe0\x00\x00\x03\xe8\x10\xf0\x04\x22\x00\xff\x00\x00\x00\x00\x00\x00'
            rtp_resp = b'\x90\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe0\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x46\x00\x00\x00\x02\x00\x00\x00'
            self.RtpSocket.send(rtp_resp, rtpAddr)
            rtp_resp = b'\x90\x08\x00\x00\x60\xf6\x97\x79\x00\x00\x00\x00\xe0\x00\x00\x08\x00\x00\x03\xe8\x00\x00\x00\x00\x00\x00\x03\xe8\x10\xf0\x04\x00\x00\xff\x0f\x00\x00\x00\x00\x00\x13\x0a\x00\x00\x0a\x00\x00\x00'
            self.RtpSocket.send(rtp_resp, rtpAddr)
            rtp_resp = b'\x90\x08\x00\x00\x60\xf6\x97\x79\x00\x00\x00\x00\xe0\x00\x00\x08\x00\x00\x00\x64\x00\xff\xfa\xe0\x00\x00\x03\xe8\x10\xf0\x04\x00\x00\xff\x0f\x00\x00\x00\x00\x00\x13\x00\x00\x00\x00\x00\x00\x00'
            self.RtpSocket.send(rtp_resp, rtpAddr)
            while True:
                w = wav.read(timespan)
                self.rtp_seq_int = self.rtp_seq_int + 1
                rtp_seq = self.rtp_seq_int.to_bytes(2, byteorder='big')
                self.rtp_time_int = self.rtp_time_int + timespan
                rtp_time = self.rtp_time_int.to_bytes(4, byteorder='big')
                start_rtp = rtp_version + rtp_seq + rtp_time + rtp_sync + rtp_profile + rtp_ext
                if len(w) == 0: break
                print("send = ")
                print(w)
                self.RtpSocket.send(start_rtp + bytes(w), rtpAddr)
                time.sleep(0.048)

    def rtp_thread(self):
        while True:
            self.rtp_logic()

def main():

    SipSocket = ServerSocket("10.21.10.125", 19888)
    RtpSocket = ServerSocket("10.21.10.125", 30000)
    sip_message = SipMessage()
    sipProcess = Thread(target=SIP, args=(SipSocket, sip_message))
    rtpProcess = Thread(target=RTP, args=(RtpSocket, sip_message))
    sipProcess.start()
    rtpProcess.start()

if __name__ == '__main__':
    main()




