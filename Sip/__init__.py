from Log import Log
from threading import Thread
from RTP import RTP
from ServerSocket import ServerSocket

class SIP(object):
    def __init__(self, SipSocket):
        self.SipSocket = SipSocket
        self.sip_message = SipMessage()
        self.RtpSocket = ServerSocket("10.21.10.125", 30000)
        self.sipAddr = ()
        self.sip_thread()


    def sip_thread(self):
        while True:
            self.sip_logic()


    def press_ptt(self):
        if self.sipAddr != ():
            self.SipSocket.send(self.sip_message.make_invite().encode(), self.SipSocket, self.sipAddr)
            rtpProcess = Thread(target=RTP, args=(self.RtpSocket,))
            rtpProcess.start()
        else:
            Log().to_log("Repeater not connected")

    def sip_logic(self):
        sipData, sipAddr = self.SipSocket.recive()
        self.sipAddr = sipAddr
        msg = sipData.decode()
        self.sip_message.parse(msg)
        Log().to_log(self.sip_message.get_method())

        if self.sip_message.get_method() == "REGISTER":
            self.SipSocket.send(self.sip_message.make_OK().encode(), sipAddr)

        if self.sip_message.get_method() == "OPTIONS":
            self.SipSocket.send(self.sip_message.make_OK().encode(), sipAddr)


        if self.sip_message.get_method() == "BYE":
            self.SipSocket.send(self.sip_message.make_OK().encode(), sipAddr)

        if self.sip_message.get_method() == "200":
            pass

        if self.sip_message.get_method() == "400":
            Log().to_log(self.sip_message.get_method())
            self.SipSocket.send(self.sip_message.make_OK().encode(), sipAddr)

        if self.sip_message.get_method() == "MESSAGE":
            Log().to_log(self.sip_message.get_message())
            Log().to_log(self.sip_message.get_ais_msg_id())
            self.SipSocket.send(self.sip_message.make_OK().encode(), sipAddr)

        if self.sip_message.get_method() == "INVITE":
            self.SipSocket.send(self.sip_message.make_trying().encode(), sipAddr)
            self.SipSocket.send(self.sip_message.make_ringing().encode(), sipAddr)
            self.sip_message.add_body(
                "v=0\r\no=1001 0 0 IN IP4 10.21.10.125\r\ns=A conversation\r\nc=IN IP4 10.21.10.125\r\nt=0 0\r\nm=audio 30000 RTP/AVP 8\r\na=rtpmap:8 PCMA/8000")
            self.SipSocket.send(self.sip_message.make_OK().encode(), sipAddr)
            rtpProcess = Thread(target=RTP, args=(self.RtpSocket,))
            rtpProcess.start()

        if self.sip_message.get_method() == "100":
            self.SipSocket.send(self.sip_message.make_ack().encode(), sipAddr)
            pass

        if self.sip_message.get_method() == "180":
            pass

class SipMessage(object):
    def __init__(self):
        self._body = ""
        self._header = ""
        self._contact = ""
        self._type = ""
        self._ANSWERS = {'200': 'SIP/2.0 200 OK',
                         '202': 'SIP/2.0 202 Accepted',
                         '400': 'SIP/2.0 400 Bad Request',
                         '401': 'SIP/2.0 401 Unauthorized',
                         '100': 'SIP/2.0 100 Trying',
                         '180': 'SIP/2.0 180 Ringing'}

        self._REQUEST = {'INV': 'INVITE',
                         'ACK': 'ACK',
                         'BYE': 'BYE',
                         'CAN': 'CANCEL',
                         'REG': 'REGISTER',
                         'OPT': 'OPTIONS',
                         'MES': 'MESSAGE'}
        self._SPLITTER = "\r\n"

    def parse(self, msg):
        self._body = msg.split(self._SPLITTER * 2)[1]
        d = dict()
        self._type = msg.split(self._SPLITTER * 2)[0].split(self._SPLITTER)[0]
        for m in msg.split(self._SPLITTER * 2)[0].split(self._SPLITTER)[1:]:
            d[m.split(":", 1)[0]] = m.split(":", 1)[1]
        self._header = d

    def get_message(self):
        return self._body.encode('utf-8').decode('utf-16be')

    def get_type(self):
        return self._type

    def get_via(self):
        try:
            return self._header["Via"]
        except:
            Log().to_log("Via does not exist")

    def get_from(self):
        try:
            return self._header["Via"]
        except:
            Log().to_log("From does not exist")

    def get_contact(self):
        try:
            return self._header["Contact"]
        except:
            Log().to_log("Contact does not exist")

    def get_to(self):
        try:
            return self._header["To"]
        except:
            Log().to_log("To does not exist")

    def get_user_agent(self):
        try:
            return self._header["User-Agent"]
        except:
            Log().to_log("User-Agent does not exist")

    def get_call_id(self):
        try:
            return self._header["Call-ID"]
        except:
            Log().to_log("Call-ID does not exist")

    def get_content_Length(self):
        try:
            return self._header["Content-Length"]
        except:
            Log().to_log("Content-Length does not exist")
    def get_ais_msg_id(self):
        try:
            return self._header["Ais-Msg-id"]
        except:
            Log().to_log("Ais-Msg-i does not exist")
    def get_method(self):
        for k in self._REQUEST:
            if self._type.__contains__(self._REQUEST[k]):
                return self._REQUEST[k]

        for k in self._ANSWERS:
            if self._type.__contains__(self._ANSWERS[k]):
                return k
        return "NONE"

    def __make_msg(self):
        msg = ""
        try:
            self._header["User-Agent"] = "Callta Server"
        except:
            pass
        for key in self._header:
            msg += key + ":" + self._header[key] + self._SPLITTER
        msg += self._SPLITTER
        return msg

    def make_OK(self):
        return self._ANSWERS['200'] + self._SPLITTER + self.__make_msg() + self._body + self._SPLITTER

    def make_ringing(self):
        return self._ANSWERS['180'] + self._SPLITTER + self.__make_msg()

    def make_unauthorized(self):
        return self._ANSWERS['401'] + self._SPLITTER + self.__make_msg()

    def make_trying(self):
        return self._ANSWERS['100'] + self._SPLITTER + self.__make_msg()

    def add_body(self,str):
        self._body = str + self._SPLITTER


    def make_ack(self):
        msg =  self._REQUEST["ACK"] + " sip:100@10.21.207.50:19888 SIP/2.0" + self._SPLITTER
        self._header["CSeq"] = "20 INVITE"
        self._header["Content-Type"] = "application/sdp"
        self._header["Via"] = self._header["Via"].replace("10.21.207.50", "10.21.10.125")
        self._header["From"] = self._header["From"].replace("1000@10.21.207.50", "2000@10.21.10.125")
        self._header["To"] = self._header["To"].replace("10.21.10.125", "10.21.207.50")
        self._header["Ais - Reach"] = "group"
        self._header["Ais - Options"] = " priority = 0; slot = 1; OnlineCallID = 2; method = patcs; AutoFloor = 0"
        self._header["Ais - Msg - id"] = "repeater - id = 1000"
        for key in self._header:
            msg += key + ":" + self._header[key] + self._SPLITTER
        msg += self._SPLITTER
        msg = "ACK sip:100@10.21.207.50:19888 SIP/2.0\r\nVia: SIP/2.0/UDP 10.21.10.125:19888;rport;branch=z9hG4bK1141423468\r\nFrom: <sip:16775904@10.21.10.125:19888>;tag=1024850604\r\nTo: <sip:100@10.21.207.50:19888>;tag=1363084463\r\nCall-ID: 316566532\r\nCSeq: 20 ACK\r\nContact: <sip:16775904@10.21.10.125:19888>\r\nMax-Forwards: 70\r\nUser-Agent: PD200 Server\r\nContent-Length: 0\r\n"

        return msg

    def make_invite(self):
        msg = self._REQUEST["INV"] + " sip:100@10.21.207.50:19888 SIP/2.0" + self._SPLITTER
        body = "v=0\r\no=1001 0 0 IN IP4 10.21.10.125\r\ns=A conversation\r\nc=IN IP4 10.21.10.125\r\nt=0 0\r\nm=audio 30000 RTP/AVP 8\r\na=rtpmap:8 PCMA/8000" + self._SPLITTER
        self._header["Content-Length"] = str(len(body))
        self._header["CSeq"] = "20 INVITE"
        self._header["Content-Type"] = "application/sdp"
        self._header["Via"] = self._header["Via"].replace("10.21.207.50","10.21.10.125")
        self._header["From"] = self._header["From"].replace("1000@10.21.207.50", "2000@10.21.10.125")
        self._header["To"] = self._header["To"].replace("10.21.10.125","10.21.207.50")
        self._header["Contact"] = self._header["Contact"].replace("10.21.10.125", "10.21.207.50")
        self._header["Ais - Reach"] = "group"
        self._header["Ais - Options"] =" priority = 0; slot = 1; OnlineCallID = 2; method = patcs; AutoFloor = 0"
        self._header["Ais - Msg - id"] = "repeater - id = 1000"
        del self._header["Accept"]
        for key in self._header:
            msg += key + ":" + self._header[key] + self._SPLITTER
        msg += self._SPLITTER
        msg += body
        msg2 = "INVITE sip:100@10.21.207.50:19888 SIP/2.0\r\nVia: SIP/2.0/UDP 10.21.10.125:19888;rport;branch=z9hG4bK1847869345\r\nFrom: <sip:16775904@10.21.10.125:19888>;tag=1085229703\r\nTo: <sip:100@10.21.207.50:19888>\r\nCall-ID: 2176886565\r\nCSeq: 20 INVITE\r\nContact: <sip:16775904@10.21.10.125:19888>\r\nContent-Type: application/sdp\r\nMax-Forwards: 70\r\nUser-Agent: MY Server\r\nSubject: This is a call for a conversation\r\nAis-Reach: group\r\nAis-Options: priority=0;slot=1;OnlineCallID=2;method=patcs;AutoFloor=0\r\nAis-Msg-id: repeater-id=1000\r\nContent-Length:   145\r\n\r\nv=0\r\no=DPS 0 0 IN IP4 10.21.10.125\r\ns=A conversation\r\nc=IN IP4 10.21.10.125\r\nt=0 0\r\nm=audio 30000 RTP/AVP 8\r\na=rtpmap:8 PCMA/8000/1\r\na=sendrecv\r\n"
        return msg2
