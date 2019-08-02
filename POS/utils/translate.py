from kivy.uix.textinput import TextInput
from kivy.properties import NumericProperty, StringProperty
from arabic_reshaper import reshape
from bidi.algorithm import get_display


def arabic_trans(labelstr):
    test = str(labelstr)
    return get_display(reshape(test))


class Ar_text(TextInput):
    max_chars = NumericProperty(100)  # maximum character allowed
    str = StringProperty()

    def __init__(self, **kwargs):
        super(Ar_text, self).__init__(**kwargs)

    def insert_text(self, substring, from_undo=False):
        if not from_undo and (len(self.text) + len(substring) > self.max_chars):
            return
        self.str = self.str + substring
        self.text = arabic_trans(self.str)
        substring = ""
        super(Ar_text, self).insert_text(substring, from_undo)

    def do_backspace(self, from_undo=False, mode='bkspc'):
        self.str = self.str[0:len(self.str) - 1]
        self.text = arabic_trans(self.str)
