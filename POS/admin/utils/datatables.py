from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from pymongo import MongoClient
from collections import OrderedDict
from .translate import arabic_trans

Builder.load_string('''
<DataTable>:
    id: main_win
    RecycleView:
        viewclass: 'CustLabel'
        id: table_floor
        RecycleGridLayout:
            id: table_floor_layout
            cols: 5
            default_size:  (None, 250)
            default_size_hint: (1, None)
            size_hint_y: None
            height: self.minimum_height
            spacing: 5
            font_name: "utils/arial"

<CustLabel@Label>:
    bcolor: (1,1,1,1)
    font_name: "utils/arial"
    canvas.before:
        Color:
            rgba: root.bcolor
        Rectangle:
            size: self.size
            pos: self.pos
''')


class DataTable(BoxLayout):
    def __init__(self, table='', **kwargs):
        super().__init__(**kwargs)

        products = table
        col_titles = [k for k in products.keys()]
        rows_len = len(products[col_titles[0]])
        self.columns = len(col_titles)
        table_data = []
        for t in col_titles:
            table_data.append({'text': str(t), 'size_hint_y': None, 'height': 50, 'bcolor': (0.06, 0.45, 0.45, 1), 'font_name': "utils/arial"})

        for r in range(rows_len):
            for t in col_titles:
                '''
                if t == 'product_name':
                    print('1561891518-----------------')
                    table_data.append(#str(products[t][r])
                        {'text': arabic_trans(u'طماطم'), 'size_hint_y': None, 'height': 30,
                         'bcolor': (0.06, 0.25, 0.25, 1)})
                else:'''
                table_data.append(
                    {'text': arabic_trans(str(products[t][r])), 'size_hint_y': None, 'height': 30,
                     'bcolor': (0.06, 0.25, 0.25, 1), 'font_name': "utils/arial"})
        self.ids.table_floor_layout.cols = self.columns
        self.ids.table_floor.data = table_data


'''
class DataTableApp(App):
    def build(self):
        return DataTable()


if __name__ == "__main__":
    DataTableApp().run()
'''
