from ServerSocket import ServerSocket
from Log import Log
from Sip import SipMessage
from threading import Thread
from threading import Event
import struct

FLAGE = False


class SIP(object):
    def __init__(self, SipSocket):
        self.SipSocket = SipSocket
        self.sip_message = SipMessage()
        self.RtpSocket = ServerSocket("10.21.10.125", 30000)
        self.sip_thread(SipSocket)


    def sip_thread(self, SipSocket):
        while True:
            self.sip_logic(SipSocket)

    def sip_logic(self, SipSocket):
        sipData, sipAddr = SipSocket.recive()
        msg = sipData.decode()
        self.sip_message.parse(msg)
        Log().to_log(self.sip_message.get_method())

        if self.sip_message.get_method() == "REGISTER":
            SipSocket.send(self.sip_message.make_OK().encode(), sipAddr)

        if self.sip_message.get_method() == "OPTIONS":
            SipSocket.send(self.sip_message.make_OK().encode(), sipAddr)
            SipSocket.send(self.sip_message.make_invite().encode(), sipAddr)
            rtpProcess = Thread(target=RTP, args=(self.RtpSocket,))
            rtpProcess.start()

        if self.sip_message.get_method() == "BYE":
            SipSocket.send(self.sip_message.make_OK().encode(), sipAddr)

        if self.sip_message.get_method() == "200":
            pass

        if self.sip_message.get_method() == "400":
            Log().to_log(self.sip_message.get_method())
            SipSocket.send(self.sip_message.make_OK().encode(), sipAddr)

        if self.sip_message.get_method() == "MESSAGE":
            Log().to_log(self.sip_message.get_message())
            Log().to_log(self.sip_message.get_ais_msg_id())
            SipSocket.send(self.sip_message.make_OK().encode(), sipAddr)

        if self.sip_message.get_method() == "INVITE":
            SipSocket.send(self.sip_message.make_trying().encode(), sipAddr)
            SipSocket.send(self.sip_message.make_ringing().encode(), sipAddr)
            self.sip_message.add_body("v=0\r\no=1001 0 0 IN IP4 10.21.10.125\r\ns=A conversation\r\nc=IN IP4 10.21.10.125\r\nt=0 0\r\nm=audio 30000 RTP/AVP 8\r\na=rtpmap:8 PCMA/8000")
            SipSocket.send(self.sip_message.make_OK().encode(), sipAddr)

        if self.sip_message.get_method() == "100":
            SipSocket.send(self.sip_message.make_ack().encode(), sipAddr)
            pass

        if self.sip_message.get_method() == "180":
            pass


class RTP(object):

    def __init__(self, RtpSocket):
        self._data = b''
        self.RtpSocket = RtpSocket
        self._rtp_seq_int = 0
        self._rtp_time_int = 0
        self._timespan = 480
        self._rtp_version = b'\x90\x08'
        self._rtp_sync = b'\x4e\x2e\x19\xd9'
        self._rtp_profile = b'\xe0\x00'
        self._rtp_ext = b'\x00\x06\x01\x00\x00\x64\x00\xff\xfa\xe0\x00\x00\x03\xe8\x10\xf0\x04\x22\x00\xff\x00\x00\x00\x00\x00\x00'
        self._rtp_resp1 = b'\x90\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe0\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x46\x00\x00\x00\x02\x00\x00\x00'
        self._rtp_resp2 = b'\x90\x08\x00\x00\x60\xf6\x97\x79\x00\x00\x00\x00\xe0\x00\x00\x08\x00\x00\x03\xe8\x00\x00\x00\x00\x00\x00\x03\xe8\x10\xf0\x04\x00\x00\xff\x0f\x00\x00\x00\x00\x00\x13\x0a\x00\x00\x0a\x00\x00\x00'
        self._rtp_resp3 = b'\x90\x08\x00\x00\x60\xf6\x97\x79\x00\x00\x00\x00\xe0\x00\x00\x08\x00\x00\x00\x64\x00\xff\xfa\xe0\x00\x00\x03\xe8\x10\xf0\x04\x00\x00\xff\x0f\x00\x00\x00\x00\x00\x13\x00\x00\x00\x00\x00\x00\x00'
        self._start = b'\x90\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe0\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x006\x00\x00\x00\x02\x00\x03\xe8'
        self._end = b'\x13\x03\x00\x00\x00\x00\x00\x00'
        self._extra = b'\xec'
        self._wav_header = 0
        self.rtp_thread()

    def toWav(self, _data):
        _file = b'RIFF'
        datalength = len(_data)
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
                              datalength, b'_data'))

        _file += (struct.pack('<L', datalength))
        self._wav_header = len(_file)
        _file += (_data)
        return _file

    def _generate_rtp_header(self):
        self._rtp_seq_int = self._rtp_seq_int + 1
        rtp_seq = self._rtp_seq_int.to_bytes(2, byteorder='big')
        self._rtp_time_int = self._rtp_time_int + self._timespan
        rtp_time = self._rtp_time_int.to_bytes(4, byteorder='big')
        rtp_header = self._rtp_version + rtp_seq + rtp_time + self._rtp_sync + self._rtp_profile + self._rtp_ext
        return rtp_header

    def rtp_logic(self):
        rtpData, rtpAddr = self.RtpSocket.recive()

        if rtpData != self._start:

            if len(rtpData) != 48 and rtpData[47] != self._extra:
                self._data += rtpData[43:]

            if len(rtpData) == 48 and rtpData[40:] == self._end and len(self._data) != 0:
                print(len(self._data))
                wav = open("test.wav", "wb")
                wav.write(self.toWav(self._data))
                wav.close()
                self._data = b''
            Log().to_log(str(rtpData))
        else:
            wav = open("test.wav", 'rb')
            self.RtpSocket.send(self._rtp_resp1, rtpAddr)
            self.RtpSocket.send(self._rtp_resp2, rtpAddr)
            self.RtpSocket.send(self._rtp_resp3, rtpAddr)
            w = wav.read(self._wav_header)
            while True:
                w = wav.read(self._timespan)
                if len(w) == 0: break
                self.RtpSocket.send(self._generate_rtp_header() + bytes(w), rtpAddr)
                Event().wait(0.0562)

    def rtp_thread(self):
        while True:
            self.rtp_logic()


def main():
    SipSocket = ServerSocket("10.21.10.125", 19888)
    SIP(SipSocket)
    #sipProcess = Thread(target=SIP, args=(SipSocket,))
    #sipProcess.start()



if __name__ == '__main__':
    main()
