from ServerSocket import ServerSocket
from Sip import SIP
from kivy.app import App
from kivy.uix.button import Button
from threading import Thread
import asyncio

class TestApp(App):
    def build(self):

        button = Button(text='PTT',
                        size_hint=(.5, .5),
                        pos_hint={'center_x': .5, 'center_y': .5})
        button.bind(on_press=self.on_press_button)

        return button

    def on_press_button(self, instance):
        #self.SIP.press_ptt()
        print('Вы нажали на кнопку!')



def main():
    SipSocket = ServerSocket("10.21.10.125", 19888)
    sipProcess = Thread(target=SIP, args=(SipSocket,))
    sipProcess.start()




if __name__ == '__main__':
    main()
    TestApp().run()
