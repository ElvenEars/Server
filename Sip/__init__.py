from Log import Log
from threading import Thread
from RTP import RTP
from ServerSocket import ServerSocket
from Configuration import Configuration


class ServerConnection:
    def __init__(self, socket=tuple(), voice_socket=ServerSocket("", 0)):
        self.socket = socket
        self.voice_socket = voice_socket


class SIP(object):
    def __init__(self, SipSocket):
        self.SipSocket = SipSocket
        self.sip_message = SipMessage()
        self.voice_port = 30000
        self.sipAddr = {}
        self.sip_thread()

    def sip_thread(self):
        while True:
            self.sip_logic()

    def transmit(self):
        if self.sipAddr != ():
            for k in self.sipAddr:
                self.SipSocket.send(self.sip_message.make_invite(self.sipAddr[k].socket).encode(), self.sipAddr[k].socket)
                Thread(target=RTP, args=(self.sipAddr[k].voice_socket,)).start()
                print(" transmit to : " + self.sipAddr[k].voice_socket.ip + " : " + str(self.sipAddr[k].voice_socket.port))
        else:
            Log().to_log("Repeater not connected")

    def recive(self):
        if self.sipAddr != ():
            for k in self.sipAddr:
                self.SipSocket.send(self.sip_message.make_trying().encode(), self.sipAddr[k].socket)
                self.SipSocket.send(self.sip_message.make_ringing().encode(), self.sipAddr[k].socket)
                self.sip_message.add_body(SdpMessage(owner_sip_id=1001).get_message())
                self.SipSocket.send(self.sip_message.make_OK().encode(), self.sipAddr[k].socket)
                Thread(target=RTP, args=(self.sipAddr[k].voice_socket,)).start()
                print(" recive to : " + self.sipAddr[k].voice_socket.ip + " : " + str(self.sipAddr[k].voice_socket.port))
        else:
            Log().to_log("Repeater not connected")

    def sip_logic(self):
        sipData, sipAddr = self.SipSocket.recive()
        msg = sipData.decode()
        self.sip_message.parse(msg)
        Log().to_log(self.sip_message.get_method())
        if self.sip_message.get_method() == "REGISTER":
            if sipAddr[0] in self.sipAddr:
                self.SipSocket.send(self.sip_message.make_OK().encode(), sipAddr)
            else:
                self.sipAddr[sipAddr[0]] = ServerConnection(socket=sipAddr, voice_socket=ServerSocket(port = self.voice_port))
                self.voice_port = self.voice_port + 2
                Log().to_log("Add to base: " + sipAddr[0] + " " + str(sipAddr[1]))
                self.SipSocket.send(self.sip_message.make_unauthorized().encode(), sipAddr)

        if sipAddr[0] not in self.sipAddr:
            self.SipSocket.send(self.sip_message.make_OK().encode(), sipAddr)
            self.SipSocket.send(self.sip_message.make_unauthorized().encode(), sipAddr)
            return

        if self.sip_message.get_method() == "OPTIONS":
            self.SipSocket.send(self.sip_message.make_OK().encode(), sipAddr)
            self.transmit()

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
            self.recive()

        if self.sip_message.get_method() == "100":
            #self.SipSocket.send(self.sip_message.make_ack().encode(), sipAddr)
            pass

        if self.sip_message.get_method() == "180":
            pass

class SdpMessage:
    def __init__(self, owner_sip_id=Configuration().server_sip_id, ip=Configuration().server_ip, rdp_port=Configuration().server_voice_port):
        self.owner = str(owner_sip_id) + " 0 0 IN IP4 " + ip
        self.version = str(0)
        self.session_name = "A conversation"
        self.connection_information = "IN IP4 " + ip
        self.time_activate = "0 0"
        self.media_description = "audio "+str(rdp_port)+" RTP/AVP 8"
        self.media_attribute = 'rtpmap:8 PCMA/8000/1'
        self.media_attribute_next = 'sendrecv'
        self._SPLITTER = "\r\n"
        self.msg = self._generate_msg()


    def _generate_msg(self):
        msg = {}
        msg["v"] = self.version
        msg["o"] = self.owner
        msg["s"] = self.session_name
        msg["c"] = self.connection_information
        msg["t"] = self.time_activate
        msg["m"] = self.media_description
        msg["a"] = self.media_attribute
        return msg

    def get_message(self):
        msg = ""
        for k, v in self.msg.items():
            msg += k + "=" + v + self._SPLITTER
        msg += 'a=' + self.media_attribute_next + self._SPLITTER
        return msg


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
                         '180': 'SIP/2.0 180 Ringing',
                         '603': 'SIP/2.0 603 Decline'}

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

    def add_body(self, str):
        self._body = str + self._SPLITTER

    '''def make_ack(self):
        msg = self._REQUEST["ACK"] + " sip:100@10.21.207.50:" + str(Configuration().server_port) + " SIP/2.0" + self._SPLITTER
        self._header["CSeq"] = "20 INVITE"
        self._header["Content-Type"] = "application/sdp"
        self._header["Via"] = self._header["Via"].replace("10.21.207.50", ""+ Configuration().server_ip+ "")
        self._header["From"] = self._header["From"].replace("1000@10.21.207.50", "2000@" + Configuration().server_ip)
        self._header["To"] = self._header["To"].replace(Configuration().server_ip, "10.21.207.50")
        self._header["Ais - Reach"] = "group"
        self._header["Ais - Options"] = " priority = 0; slot = 1; OnlineCallID = 2; method = patcs; AutoFloor = 0"
        self._header["Ais - Msg - id"] = "repeater - id = 1000"
        for key in self._header:
            msg += key + ":" + self._header[key] + self._SPLITTER
        msg += self._SPLITTER
        msg = "ACK sip:100@10.21.207.50:" + str(Configuration().server_port) + " SIP/2.0\r\nVia: SIP/2.0/UDP "+ Configuration().server_ip + ":" + str(Configuration().server_port) + ";rport;branch=z9hG4bK1141423468\r\nFrom: <sip:16775904@"+ Configuration().server_ip + ":" + str(Configuration().server_port) + ">;tag=1024850604\r\nTo: <sip:100@10.21.207.50:"+ str(Configuration().server_port) + ">;tag=1363084463\r\nCall-ID: 316566532\r\nCSeq: 20 ACK\r\nContact: <sip:16775904@"+ Configuration().server_ip+ ":" + str(Configuration().server_port) + ">\r\nMax-Forwards: 70\r\nUser-Agent: PD200 Server\r\nContent-Length: 0\r\n"
        return msg'''

    def make_invite(self, socket):
        client_ip = socket[0]
        client_port = str(socket[1])
        session_id = str(100)
        body = SdpMessage(owner_sip_id="DPS").get_message()
        msg = self._REQUEST["INV"] + " sip:"+ session_id + "@" + client_ip + ":" + client_port + " SIP/2.0" + self._SPLITTER
        msg += "Via: SIP/2.0/UDP " + Configuration().server_ip + ":" + Configuration().server_port + ";rport;branch=z9hG4bK1847869345" + self._SPLITTER
        msg += "From: <sip:" + Configuration().server_sip_id + "@" + Configuration().server_ip + ":" + Configuration().server_port + ">;tag=1085229703" + self._SPLITTER
        msg += "To: <sip:" + session_id + "@" + client_ip + ":" + client_port + ">" + self._SPLITTER
        msg += "Call-ID: 2176886565" + self._SPLITTER
        msg += "CSeq: 20 INVITE" + self._SPLITTER
        msg += "Contact: <sip:" + Configuration().server_sip_id + "@" + Configuration().server_ip + ":" + Configuration().server_port + ">" + self._SPLITTER
        msg +="Content-Type: application/sdp"+ self._SPLITTER
        msg += "Max-Forwards: 70"+ self._SPLITTER
        msg += "User-Agent: MY Server"+ self._SPLITTER
        msg += "Subject: This is a call for a conversation"+ self._SPLITTER
        #AIS params
        msg += "Ais-Reach: group"+ self._SPLITTER
        msg += "Ais-Options: priority=0;slot=1;OnlineCallID=2;method=patcs;AutoFloor=0"+ self._SPLITTER
        msg += "Ais-Msg-id: repeater-id=1000"+ self._SPLITTER
        # AIS params
        msg += "Content-Length:   "+str(len(body)) + self._SPLITTER*2
        msg += body
        return msg
