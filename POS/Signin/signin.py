from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
import sqlite3

Builder.load_file('Signin/Signin.kv')


class SigninWindow(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conn = sqlite3.connect('POS.db')
        self.cur = self.conn.cursor()

    def validate_user(self):

        query = 'SELECT * FROM USERS'
        self.cur.execute(query)
        users = self.cur.fetchall()

        usernames = []
        passwords = []
        des = []
        for user in users:
            usernames.append(user[3])
            passwords.append(user[4])
            des.append(user[5])
        user = self.ids.usrnm_field.text
        pwd = self.ids.pwd_field.text
        info = self.ids.info

        self.ids.usrnm_field.text = ''
        self.ids.pwd_field.text = ''
        if user == '' or pwd == '':
            info.text = '[color=#FF0000]username and the password required![/color]'
            self.ids.usrnm_field.focus = True
        else:
            if user not in usernames:
                info.text = '[color=#FF0000]Invalid Username![/color]'
                self.ids.usrnm_field.focus = True
            else:
                index = usernames.index(user)
                if pwd != passwords[index]:
                    info.text = '[color=#FF0000]Invalid Password![/color]'
                    self.ids.usrnm_field.focus = True
                else:
                    if des[index] == 'Administrator':
                        self.parent.parent.current = 'scrn_admin'
                    elif des[index] == 'Operator':
                        self.parent.parent.parent.ids.scrn_op.children[0].ids.loggedin_user.text = user
                        self.parent.parent.current = 'scrn_op'
                    self.ids.info.text = ''


class SigninApp(App):
    def build(self):
        return SigninWindow()

if __name__ == "__main__":
    SigninApp().run()
