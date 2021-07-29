from ServerSocket import ServerSocket
from Sip import SIP
from kivy.app import App
from kivy.uix.button import Button

class TestApp(App):
    def build(self):
        return Button(text='Hello World')



def main():
    SipSocket = ServerSocket("10.21.10.125", 19888)
    SIP(SipSocket)
    TestApp().run()



if __name__ == '__main__':
    main()
