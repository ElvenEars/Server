import struct
from threading import Event
from ServerSocket import ServerSocket
from Log import Log
import time
from datetime import datetime

class RTP(object):

    def __init__(self, RtpSocket = ServerSocket("",0,False), transmitList = {}):
        self._data = b''
        self.RtpSocket = RtpSocket
        self.transmitList = transmitList
        self._rtp_seq_int = 0
        self._rtp_time_int = 0
        self._timespan = 480
        self._rtp_version = b'\x90\x08'
        self._rtp_sync = b'\x4e\x2e\x19\xd9'
        self._rtp_profile = b'\xe0\x00'
        self._rtp_ext = b'\x00\x06\x01\x00\x00\x64\x00\xff\xfa\xe0\x00\x00\x03\xe8\x10\xf0\x04\x22\x00\xff\x00\x00\x00\x00\x00\x00'
        self._rtp_resp1 = b"\x90\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe0\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x46\x00\x00\x00\x03\x00\x00\x00"
        self._rtp_resp2 = b"\x90\x08\x00\x00\x61\x15\x0d\xa3\x00\x00\x00\x00\xe0\x00\x00\x08\x00\x00\x03\xe8\x00\x00\x00\x00\x00\x00\x03\xe8\x10\xf0\x04\x00\x00\xff\x0f\x00\x00\x00\x00\x00\x13\x0a\x00\x00\x0a\x00\x00\x00"
        s1 = b'\x90\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe0\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x46\x00\x00\x00\x02\x00\x00\x00'
        n1 = b"\x90\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe0\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x46\x00\x00\x00\x03\x00\x00\x00"
        s2 = b'\x90\x08\x00\x00\x60\xf6\x97\x79\x00\x00\x00\x00\xe0\x00\x00\x08\x00\x00\x03\xe8\x00\x00\x00\x00\x00\x00\x03\xe8\x10\xf0\x04\x00\x00\xff\x0f\x00\x00\x00\x00\x00\x13\x0a\x00\x00\x0a\x00\x00\x00'
        n2 = b"\x90\x08\x00\x00\x61\x15\x0d\xa3\x00\x00\x00\x00\xe0\x00\x00\x08\x00\x00\x03\xe8\x00\x00\x00\x00\x00\x00\x03\xe8\x10\xf0\x04\x00\x00\xff\x0f\x00\x00\x00\x00\x00\x13\x0a\x00\x00\x0a\x00\x00\x00"
        s3 = b'\x90\x08\x00\x00\x60\xf6\x97\x79\x00\x00\x00\x00\xe0\x00\x00\x08\x00\x00\x00\x64\x00\xff\xfa\xe0\x00\x00\x03\xe8\x10\xf0\x04\x00\x00\xff\x0f\x00\x00\x00\x00\x00\x13\x00\x00\x00\x00\x00\x00\x00'
        n3 = b"\x90\x08\x00\x00\x61\x15\x0d\xa3\x00\x00\x00\x00\xe0\x00\x00\x08\x00\x00\x00\x64\x00\xff\xfa\xe0\x00\x00\x03\xe8\x10\xf0\x04\x00\x00\xff\x0f\x00\x00\x00\x00\x00\x13\x00\x00\x04\x00\x00\x00\x00"
        self._rtp_resp3 =  b"\x90\x08\x00\x00\x61\x15\x0d\xa3\x00\x00\x00\x00\xe0\x00\x00\x08\x00\x00\x00\x64\x00\xff\xfa\xe0\x00\x00\x03\xe8\x10\xf0\x04\x00\x00\xff\x0f\x00\x00\x00\x00\x00\x13\x00\x00\x04\x00\x00\x00\x00"
        self._start = b'\x90\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe0\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x006\x00\x00\x00\x02\x00\x03\xe8'
        self._end = b'\x13\x03\x00\x00\x00\x00\x00\x00'
        self._pre_end = b'\x90\x08\x7b\xb4\xe1\xfc\x48\xf6\xc3\x75\xc9\xa5\xe0\x00\x00\x08\x00\x00\x00\x64\x00\x00\x03\xec\x00\x00\x03\xe8\x10\x10\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x13\x03\x00\x00\x00\x00\x00\x00'
        self._extra = b'\xec'
        self._wav_header = 0
        #self.rtp_thread()
        self.rtp_logic()

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

    def _generate_rtp_header(self, rtp_seq_int, rtp_time_int):
        rtp_seq = rtp_seq_int.to_bytes(2, byteorder='big')
        rtp_time = rtp_time_int.to_bytes(4, byteorder='big')
        rtp_header = self._rtp_version + rtp_seq + rtp_time + self._rtp_sync + self._rtp_profile + self._rtp_ext
        return rtp_header

    def rtp_start(self, rtpAddr, server_socket):
        #self.RtpSocket.send(self._start, rtpAddr)
        server_socket.send(self._rtp_resp1, rtpAddr)
        server_socket.send(self._rtp_resp2, rtpAddr)
        server_socket.send(self._rtp_resp3, rtpAddr)

    def rtp_send(self, data, rtpAddr, server_socket ):
        server_socket.send(data, rtpAddr)

    def rtp_end(self, rtpAddr, server_socket):
        server_socket.send(self._pre_end, rtpAddr)
        
    def rtp_logic(self):

        while True:
            Log().to_log("\nlisten " + self.RtpSocket.ip + " : " + str(self.RtpSocket.port))
            rtpData, rtpAddr = self.RtpSocket.recive()
            if rtpData == self._start:
                for t in self.transmitList:
                    self.rtp_start(self.transmitList[t].client_voice_socket.addr, self.transmitList[t].server_voice_socket)
                    Log().to_log(" transmit to : " + self.transmitList[t].client_voice_socket.ip + " : " + str(
                        self.transmitList[t].client_voice_socket.port))
                #self.RtpSocket.send(self._rtp_resp1, rtpAddr)
                #self.RtpSocket.send(self._rtp_resp2, rtpAddr)
                #self.RtpSocket.send(self._rtp_resp3, rtpAddr)

            else:
                if len(rtpData) != 48 and rtpData[47] != self._extra:
                    data = rtpData[40:]
                    self._data += data
                    for t in self.transmitList:
                        message = self._generate_rtp_header(self.transmitList[t].server_voice_socket.rtp_seq_int, self.transmitList[t].server_voice_socket.rtp_time_int) + data
                        self.transmitList[t].server_voice_socket.rtp_seq_int += 1
                        self.transmitList[t].server_voice_socket.rtp_time_int += self._timespan
                        self.rtp_send(message, self.transmitList[t].client_voice_socket.addr, self.transmitList[t].server_voice_socket)


                if len(rtpData) == 48 and rtpData[40:] == self._end and len(self._data) != 0:
                    print(len(self._data))
                    for t in self.transmitList:
                        self.rtp_end(self.transmitList[t].client_voice_socket.addr, self.transmitList[t].server_voice_socket)
                    wav = open(datetime.now().strftime("%d-%m-%Y %H.%M.%S")+".wav", "wb+")
                    wav.write(self.toWav(self._data))
                    wav.close()
                    self._data = b''
                    break
                Log().to_log(str(rtpData))
        '''
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
       '''

    def rtp_thread(self):
        while True:
            self.rtp_logic()
