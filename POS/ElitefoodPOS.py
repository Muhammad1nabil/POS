from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

from admin.admin import AdminWindow
from Signin.signin import SigninWindow
from Operator.Operator import OperatorWindow
from kivy.config import Config


class ElitefoodPOSWindow(BoxLayout):

    admin_widget = AdminWindow()
    signin_widget = SigninWindow()
    operator_widget = OperatorWindow()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ids.scrn_si.add_widget(self.signin_widget)
        self.ids.scrn_admin.add_widget(self.admin_widget)
        self.ids.scrn_op.add_widget(self.operator_widget)


class ElitefoodPOSApp(App):
    def build(self):

        return ElitefoodPOSWindow()

if __name__ == '__main__':
    Config.set('kivy', 'window_icon', 'logo.jpg')
    __path__ = 'kivy.garden'
    Config.set('graphics', 'borderless', 1)
    Config.set('graphics', 'window_state', 'maximized')
    Config.set('kivy', 'exit_on_escape', 0)
    Config.write()
    ElitefoodPOSApp().run()
