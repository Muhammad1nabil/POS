from collections import OrderedDict
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.uix.modalview import ModalView
from kivy.lang import Builder
import sqlite3
from datetime import datetime
from utils.datatables import DataTable
from utils.translate import arabic_trans, Ar_text

Builder.load_file('Operator/Operator.kv')


class Notify(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.7, 0.7)


class OperatorWindow(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.notesinp = Ar_text(hint_text=arabic_trans('الملاحظات'), font_name='utils/STC', size_hint_x=0.4)
        self.perdis = TextInput(hint_text=arabic_trans('خصم نسبة%'), font_name='utils/STC', size_hint_x=0.2, input_filter='float',
                                on_text_validate=lambda x: self.discount(1), multiline=False)
        self.fixdis = TextInput(hint_text=arabic_trans('خصم مبلغ'), font_name='utils/STC', size_hint_x=0.2, input_filter='float',
                                on_text_validate=lambda x: self.discount(0), multiline=False)
        perdisl = Label(text=arabic_trans('خصم نسبة'), font_name='utils/STC', size_hint_x=0.1, color=(.06, .45, .45, 1))
        fixdisl = Label(text=arabic_trans('خصم مبلغ'), font_name='utils/STC', size_hint_x=0.1, color=(.06, .45, .45, 1))
        self.ids.notes.add_widget(self.notesinp)
        self.ids.notes.add_widget(self.perdis)
        self.ids.notes.add_widget(perdisl)
        self.ids.notes.add_widget(self.fixdis)
        self.ids.notes.add_widget(fixdisl)

        self.ids.qtylabel.text = arabic_trans('الكميه')
        self.ids.codelabel.text = arabic_trans('كود الصنف')
        self.ids.disclabel.text = arabic_trans('خصم علي الوحده')
        self.ids.pricelabel.text = arabic_trans('سعر الوحده')
        self.ids.noteslabel.text = arabic_trans('ملاحظات الصنف')
        self.itemnotes = Ar_text(hint_text=arabic_trans('ملاحظات الصنف'), font_name='utils/STC', on_text_validate=lambda x:
                                 self.update_purchases(self.ids.code_inp.text), multiline=False)
        self.ids.notes_inp.add_widget(self.itemnotes)
        self.conn = sqlite3.connect("POS.db")
        self.cur = self.conn.cursor()
        self.cur.execute('SELECT * FROM USERS')

        self.target_cust = ('-1', '', '', '', '', 0)
        self.notify = Notify()
        self.total = 0.00
        self.disc = 0.00
        self.number = 0
        product_names = []
        product_prices = []
        spinveg = []
        spinfru = []
        spinpro = []
        spinfast = []
        spincusts = ['new']
        cats = []
        query = 'SELECT * FROM PRODUCTS'
        self.cur.execute(query)
        self.products = self.cur.fetchall()

        self.cur.execute('SELECT * FROM CUSTOMERS')
        self.customers = self.cur.fetchall()
        for product in self.products:
            product_names.append(arabic_trans(product[2]))
            product_prices.append(product[3])
            cats.append(product[4])

        query = 'SELECT customer_code, delivery FROM CUSTOMERS'
        self.cur.execute(query)
        self.cust_codes = self.cur.fetchall()
        self.customer_codes = []
        for customer in self.cust_codes:
            if customer:
                self.customer_codes.append(customer[0])
                line = ' | '.join([customer[0], str(customer[1]) + ' L.E'])
                spincusts.append(line)
        for x in range(len(product_prices)):
            line = '  |  '.join([product_names[x], str(product_prices[x]) + ' L.E'])
            if arabic_trans(cats[x]) == arabic_trans('خضار'):
                spinveg.append(line)
            elif arabic_trans(cats[x]) == arabic_trans('فاكهة'):
                spinfru.append(line)
            elif arabic_trans(cats[x]) == arabic_trans('منتجات'):
                spinpro.append(line)
            elif arabic_trans(cats[x]) == arabic_trans('مأكولات جاهزه'):
                spinfast.append(line)

        self.ids.veg_spin.values = spinveg
        self.ids.fruit_spin.values = spinfru
        self.ids.product_spin.values = spinpro
        self.ids.fastfood_spin.values = spinfast
        self.ids.cust_code_spin.values = spincusts

        self.items_kivy = []
        self.preview = self.ids.receipt_preview

        self.product_srn = self.ids.products
        self.items = self.getitems()
        item_table = DataTable(table=self.items)
        self.product_srn.add_widget(item_table)

        self.ids.veg_spin.text = arabic_trans('خضار')
        self.ids.fruit_spin.text = arabic_trans('فاكهة')
        self.ids.product_spin.text = arabic_trans('منتجات')
        self.ids.fastfood_spin.text = arabic_trans('مأكولات جاهزه')

        print(self.notesinp.text)

    def logout(self):
        self.parent.parent.current = 'scrn_si'

    def killswitch(self, dtx):
        self.notify.dismiss()
        self.notify.clear_widgets()

    def update_purchases(self, pcode):
        if pcode == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]Product code is Required![/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)

        else:
            codes = []
            target_prod = []
            x = False
            for prod in self.products:
                codes.append(str(prod[1]))
            print(codes)
            if pcode not in codes:
                self.notify.add_widget(
                    Label(text='[color=#FF0000][b]Product code is not valid![/b][/color]', markup=True))
                self.notify.open()
                Clock.schedule_once(self.killswitch, 1)
                x = True
            else:
                prod = self.products[codes.index(pcode)]
                target_prod = prod
            if x:
                return
            pname = target_prod[2]
            quntity = self.ids.qty_inp.text
            discount = self.ids.disc_inp.text
            unit_price = target_prod[3]
            note = self.itemnotes.text

            if quntity == '':
                quntity = 1.0
            if discount == '':
                discount = float(0.0)
            quntity = float(quntity)
            discount = float(discount) * quntity
            prod_price = float(unit_price) * quntity - discount
            self.total += prod_price
            self.disc += discount
            ptarget = -1
            if list(self.items['code'].values()).__contains__(pcode):
                index = list(self.items['code'].values()).index(pcode)
                ptarget = list(self.items['code'].keys())[index]

            print(ptarget)
            if ptarget >= 0:
                print(self.items['qty'])
                newqty = self.items['qty'][ptarget] + float(quntity)
                self.items['qty'][ptarget] = newqty
                self.items['product total'][ptarget] += prod_price
                self.items['disc'][ptarget] += discount
                self.items['notes'][ptarget] = arabic_trans(note)
            else:
                n = self.number
                self.items['item no'][n] = self.number + 1
                self.items['code'][n] = pcode
                self.items['product name'][n] = pname
                self.items['qty'][n] = quntity
                self.items['disc'][n] = discount
                self.items['unit price'][n] = float(unit_price)
                self.items['product total'][n] = prod_price
                self.items['notes'][n] = arabic_trans(note)
                self.number += 1
            self.update_preview()
            print(self.items)
            self.product_srn.clear_widgets()
            item_table = DataTable(table=self.items)
            self.product_srn.add_widget(item_table)
            self.itemnotes.text = ''

    def on_spinner_select(self, text, stype):
        a = text[:text.find('  |  ')].strip()
        for prod in self.products:
            if arabic_trans(a) == prod[2]:
                self.ids.code_inp.text = str(prod[1])
                self.ids.price_inp.text = str(prod[3])
                if stype == 'vegetables':
                    self.ids.veg_spin.text = arabic_trans('خضار')
                elif stype == 'Fruits':
                    self.ids.fruit_spin.text = arabic_trans('فاكهة')
                elif stype == 'Products':
                    self.ids.product_spin.text = arabic_trans('منتجات')
                elif stype == 'Fast Food':
                    self.ids.fastfood_spin.text = arabic_trans('مأكولات جاهزه')
                self.ids.qty_inp.text = ''
                self.ids.disc_inp.text = ''

    def remove_item(self):
        if self.ids.remove_inp.text == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]Item Number is Required![/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
            return

        itemno = int(self.ids.remove_inp.text) - 1
        print(itemno)
        print(list(self.items['item no'].keys()))
        if not list(self.items['item no'].keys()).__contains__(itemno):
            self.notify.add_widget(Label(text='[color=#FF0000][b]item number is not Exist![/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
        else:
            self.total -= self.items['product total'][itemno]
            self.disc -= self.items['disc'][itemno]
            self.items['item no'].pop(itemno)
            self.items['code'].pop(itemno)
            self.items['product name'].pop(itemno)
            self.items['qty'].pop(itemno)
            self.items['disc'].pop(itemno)
            self.items['unit price'].pop(itemno)
            self.items['product total'].pop(itemno)
            self.product_srn.clear_widgets()
            print(self.items)
            item_table = DataTable(table=self.items)
            self.product_srn.add_widget(item_table)
            self.ids.remove_inp.text = ''
            self.update_preview()

    def clear_order(self):
        self.ids.products.clear_widgets()
        self.ids.code_inp.text = ''
        self.ids.qty_inp.text = ''
        self.ids.disc_inp.text = ''
        self.ids.price_inp.text = '0.0'
        self.itemnotes.text = ''
        self.ids.receipt_preview.text = '\n'
        self.total = 0.0
        self.items['item no'] = {}
        self.items['code'] = {}
        self.items['product name'] = {}
        self.items['qty'] = {}
        self.items['disc'] = {}
        self.items['unit price'] = {}
        self.items['product total'] = {}
        self.items['notes'] = {}
        self.number = 0
        self.product_srn.clear_widgets()
        item_table = DataTable(table=self.items)
        self.product_srn.add_widget(item_table)
        self.ids.cust_code_spin.text = 'Customer Code | delivery'
        self.target_cust = ('-1', '', '', '', '', 0)
        self.disc = 0.00
        self.notesinp.text = ''
        self.perdis.text = ''
        self.fixdis.text = ''

    def finishtrans(self):

        if self.target_cust[1] == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]Customer code is Required![/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
            return
        if self.items['item no'].__len__() <= 0:
            self.notify.add_widget(Label(text='[color=#FF0000][b]No Order![/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
            return
        pcode = list(self.items['code'].values())
        price = list(self.items['product total'].values())
        qty = list(self.items['qty'].values())
        dis = list(self.items['disc'].values())
        dnote = list(self.items['notes'].values())
        date = datetime.today().date()
        query = 'INSERT INTO TRANSACTIONS(customer_code, Date, total_price, disc, notes) VALUES(?, ?, ?, ?, ?)'
        values = [self.target_cust[1], date, self.total, self.disc, arabic_trans(self.notesinp.text)]
        self.cur.execute(query, values)
        order_id = self.cur.lastrowid
        for i in range(len(pcode)):
            query = 'INSERT INTO TRANS_DETAILS(order_id, prod_id, price, quantity, discount, note, date) VALUES(?, ?, ?, ?, ?, ?, ?)'
            values = [order_id, pcode.pop(), price.pop(), qty.pop(), dis.pop(), dnote.pop(), date]
            self.cur.execute(query, values)
        self.conn.commit()
        self.clear_order()

        self.notify.add_widget(Label(text='[color=#00FF00][b]Successfully Added![/b][/color]', markup=True))
        self.notify.open()
        Clock.schedule_once(self.killswitch, 2)

    def select_cust(self):
        text = self.ids.cust_code_spin.text
        if text == 'new':
            self.target_cust = (0, 'new', 'new', 'new', 'new', 5)
            self.total += self.target_cust[5]
            self.update_preview()
        else:
            a = text[:text.find(' | ')].strip()
            for cust in self.customers:
                if a == cust[1]:
                    if self.target_cust[0] == '-1':
                        self.total += cust[5]
                        self.target_cust = cust
                        self.update_preview()
                    else:
                        self.total -= self.target_cust[5]
                        self.target_cust = cust
                        self.total += self.target_cust[5]
                        self.update_preview()

    def check_cust(self, text):
        print(text)
        if text.strip() in self.customer_codes:
            for cust in self.customers:
                if text.strip() == cust[1]:
                    if self.target_cust[0] == '-1':
                        self.total += cust[5]
                        self.target_cust = cust
                        self.update_preview()
                        return
                    else:
                        self.total -= self.target_cust[5]
                        self.target_cust = cust
                        self.total += self.target_cust[5]
                        self.update_preview()
                        return
            self.notify.add_widget(Label(text='[color=#00FF00][b]Invalid Customer ID![/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 2)

    def getitems(self):
        _items = OrderedDict()
        _items['item no'] = {}
        _items['code'] = {}
        _items['product name'] = {}
        _items['qty'] = {}
        _items['disc'] = {}
        _items['unit price'] = {}
        _items['product total'] = {}
        _items['notes'] = {}

        return _items

    def update_preview(self):
        purchase_total = '\n`  '
        if self.target_cust[5] > 0:
            purchase_total += '\n\nDelivery\t\t\t\t\t\t\t\t' + str(self.target_cust[5])
        if self.disc != 0.00:
            purchase_total += '\n\nDiscount\t\t\t\t\t\t\t' + str(self.disc)
        purchase_total += '\n\nTotal\t\t\t\t\t\t\t\t' + str(self.total)
        nu_preview = ''
        i = self.items['code'].keys()

        for n in i:
            pname = self.items['product name'][n]
            quntity = self.items['qty'][n]
            prod_price = self.items['product total'][n]
            nu_preview = nu_preview + '\n' + str(prod_price) + '\t\tx' + str(quntity) + '\t\t' + arabic_trans(pname)
        nu_preview += purchase_total
        self.preview.text = nu_preview

    def discount(self, ti):
        if ti:
            percentage = float(self.perdis.text) / 100
            dis = percentage * self.total
            self.disc += dis
            self.total -= dis
        else:
            dis = float(self.fixdis.text)
            self.disc += dis
            self.total -= dis

        self.update_preview()
        self.perdis.text = ''
        self.fixdis.text = ''


class OperatorApp(App):
    def build(self):
        return OperatorWindow()

if __name__ == "__main__":
    OperatorApp().run()
