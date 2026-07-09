# -*- coding: utf-8 -*-
"""
MARKIROVKA — ANDROID VERSION (Kivy)
Bluetooth orqali Xprinter 370B ga TSPL yuboradi.
Etiketkada faqat mahsulot nomi, markazda.
"""

import os
import json

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.utils import platform
from kivy.core.window import Window
from kivy.clock import Clock

# ============================================================
#  ANDROID BLUETOOTH
# ============================================================

ANDROID = platform == "android"

VERSIYA = "1.2"

if ANDROID:
    from jnius import autoclass
    from android.permissions import request_permissions, Permission
    
    BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
    UUID = autoclass('java.util.UUID')
    SPP_UUID = "00001101-0000-1000-8000-00805F9B34FB"


# ============================================================
#  DATA
# ============================================================

STANDART_MAHSULOTLAR = [
    {"id": 1,  "nomi": "Aysberg salati"},
    {"id": 2,  "nomi": "Blinchik goshtli"},
    {"id": 3,  "nomi": "Blinchik tvarogli"},
    {"id": 4,  "nomi": "Bo'laklangan bodringlar"},
    {"id": 5,  "nomi": "Bo'laklangan pomidorlar"},
    {"id": 6,  "nomi": "Gamberger noni"},
    {"id": 7,  "nomi": "Kesilgan qizil piyoz"},
    {"id": 8,  "nomi": "Ko'katlar"},
    {"id": 9,  "nomi": "Margarin"},
    {"id": 10, "nomi": "Marinadlangan bodring"},
    {"id": 11, "nomi": "Oq karam"},
    {"id": 12, "nomi": "Pishloq"},
    {"id": 13, "nomi": "Qizil karam"},
    {"id": 14, "nomi": "Salat Grecheskiy"},
    {"id": 15, "nomi": "Salat Sezar"},
    {"id": 16, "nomi": "Sezar salat siri"},
    {"id": 17, "nomi": "Sirniki"},
    {"id": 18, "nomi": "Sosiska (defrost)"},
    {"id": 19, "nomi": "Tayyor guruch"},
    {"id": 20, "nomi": "Tayyor salat"},
    {"id": 21, "nomi": "To'g'ralgan piyoz"},
    {"id": 22, "nomi": "Tomatniy shirin sous"},
    {"id": 23, "nomi": "Toralgan limon"},
    {"id": 24, "nomi": "Zaytun"},
]

RANGLAR = [
    (0.91, 0.30, 0.24, 1), (0.90, 0.49, 0.13, 1), (0.95, 0.61, 0.07, 1),
    (0.15, 0.68, 0.38, 1), (0.16, 0.50, 0.73, 1), (0.56, 0.27, 0.68, 1),
    (0.09, 0.63, 0.52, 1), (0.83, 0.33, 0.00, 1), (0.10, 0.74, 0.61, 1),
    (0.75, 0.22, 0.17, 1), (0.20, 0.60, 0.86, 1), (0.61, 0.35, 0.71, 1),
]


def translit(matn):
    """Kirillcha → Lotincha (TSPL faqat ASCII tushunadi)"""
    c = {'А':'A','Б':'B','В':'V','Г':'G','Д':'D','Е':'E','Ё':'Yo','Ж':'Zh',
         'З':'Z','И':'I','Й':'Y','К':'K','Л':'L','М':'M','Н':'N','О':'O',
         'П':'P','Р':'R','С':'S','Т':'T','У':'U','Ф':'F','Х':'X','Ц':'Ts',
         'Ч':'Ch','Ш':'Sh','Щ':'Shch','Ъ':'','Ы':'Y','Ь':'','Э':'E','Ю':'Yu',
         'Я':'Ya','а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'yo',
         'ж':'zh','з':'z','и':'i','й':'y','к':'k','л':'l','м':'m','н':'n',
         'о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'x',
         'ц':'ts','ч':'ch','ш':'sh','щ':'shch','ъ':'','ы':'y','ь':'','э':'e',
         'ю':'yu','я':'ya','ў':"o'",'қ':'q','ғ':"g'",'ҳ':'h',
         'Ў':"O'",'Қ':'Q','Ғ':"G'",'Ҳ':'H'}
    for k, v in c.items():
        matn = matn.replace(k, v)
    # Faqat ASCII qoldirish
    return matn.encode('ascii', 'ignore').decode('ascii')


# ============================================================
#  TSPL GENERATOR — nom markazda
# ============================================================

def tspl_yarat(nomi, nusxa=1):
    """
    40x30mm etiketka: FAQAT NOM, MARKAZDA.
    203 DPI: 40mm = 320 dots, 30mm = 240 dots.
    TSPL font "4" = 24x32 dots (1 belgi).
    """
    nomi = translit(nomi).strip()
    
    LABEL_W = 320
    LABEL_H = 240
    
    # Font tanlash: qisqa nom = katta, uzun = kichik
    # (font_id, char_w, char_h, x_mul, y_mul)
    variants = [
        ("4", 24, 32, 2, 2),   # juda katta: 48x64 / belgi
        ("4", 24, 32, 1, 1),   # katta: 24x32
        ("3", 16, 24, 1, 1),   # o'rta: 16x24
        ("2", 12, 20, 1, 1),   # kichik: 12x20
    ]
    
    max_w = LABEL_W - 24  # padding
    
    tanlangan = None
    lines = []
    
    for font_id, cw, ch, xm, ym in variants:
        char_w = cw * xm
        char_h = ch * ym
        max_chars = max_w // char_w
        
        # So'zlarni qatorlarga bo'lish
        sozlar = nomi.split()
        test_lines = []
        joriy = ""
        sigdi = True
        for soz in sozlar:
            if len(soz) > max_chars:
                sigdi = False
                break
            test = (joriy + " " + soz).strip()
            if len(test) <= max_chars:
                joriy = test
            else:
                test_lines.append(joriy)
                joriy = soz
        if not sigdi:
            continue
        if joriy:
            test_lines.append(joriy)
        
        # Balandlik tekshirish
        line_gap = 8
        total_h = len(test_lines) * (char_h + line_gap)
        if total_h <= LABEL_H - 20:
            tanlangan = (font_id, char_w, char_h, xm, ym)
            lines = test_lines
            break
    
    if not tanlangan:
        # Fallback: eng kichik font, kesib
        font_id, cw, ch, xm, ym = "2", 12, 20, 1, 1
        char_w, char_h = cw, ch
        max_chars = max_w // char_w
        lines = [nomi[i:i+max_chars] for i in range(0, len(nomi), max_chars)][:5]
        tanlangan = (font_id, char_w, char_h, xm, ym)
    
    font_id, char_w, char_h, xm, ym = tanlangan
    
    # TSPL yaratish
    line_gap = 8
    total_h = len(lines) * (char_h + line_gap) - line_gap
    y = (LABEL_H - total_h) // 2
    
    cmd = [
        "SIZE 40 mm, 30 mm",
        "GAP 2 mm, 0 mm",
        "DIRECTION 0",
        "REFERENCE 0,0",
        "CLS",
        "BOX 2,2,318,238,2",
    ]
    
    for line in lines:
        text_w = len(line) * char_w
        x = max(4, (LABEL_W - text_w) // 2)
        cmd.append(f'TEXT {x},{y},"{font_id}",0,{xm},{ym},"{line}"')
        y += char_h + line_gap
    
    cmd.append(f"PRINT {nusxa},1")
    
    return ("\r\n".join(cmd) + "\r\n").encode("ascii")


# ============================================================
#  ESC/POS GENERATOR — XP-326B kabi portativ printerlar uchun
# ============================================================

def escpos_yarat(nomi, nusxa=1):
    """
    ESC/POS protokoli: markazda, katta, qalin matn.
    Uzun nom bir necha qatorga bo'linadi — hammasi ko'rinadi.
    XP-P326B va boshqa mobil/chek printerlar uchun.
    """
    nomi = translit(nomi).strip()

    ESC = b"\x1b"
    GS  = b"\x1d"

    # 58mm qog'oz: normal shriftda ~32 belgi bir qatorda.
    # Shrift kattalashsa, qatorga sig'adigan belgilar kamayadi.
    # (gs_size, char_per_line) — kattadan kichikka
    variants = [
        (b"\x33", 8),   # 4x — juda katta, ~8 belgi
        (b"\x22", 10),  # 3x — ~10 belgi
        (b"\x11", 16),  # 2x — ~16 belgi
        (b"\x00", 32),  # 1x — normal, ~32 belgi
    ]

    # Nom sig'adigan eng katta shriftni tanlash (max 2 qator)
    tanlangan_size = variants[-1][0]
    lines = [nomi]

    for gs_size, cpl in variants:
        # So'zlarni qatorlarga bo'lish
        sozlar = nomi.split()
        test_lines = []
        joriy = ""
        sigdi = True
        for soz in sozlar:
            if len(soz) > cpl:
                sigdi = False   # bitta so'z sig'madi — kichikroq shrift kerak
                break
            test = (joriy + " " + soz).strip()
            if len(test) <= cpl:
                joriy = test
            else:
                test_lines.append(joriy)
                joriy = soz
        if joriy:
            test_lines.append(joriy)

        # Ko'pi bilan 2 qatorga sig'sa — shu shriftni olamiz
        if sigdi and len(test_lines) <= 2:
            tanlangan_size = gs_size
            lines = test_lines
            break
        # Agar eng kichik shrift ham 2 qatordan oshsa — baribar shuni olamiz
        if gs_size == b"\x00":
            tanlangan_size = gs_size
            lines = test_lines if test_lines else [nomi]

    data = b""
    for _ in range(nusxa):
        data += ESC + b"@"             # Init
        data += ESC + b"a" + b"\x01"   # Markazga
        data += ESC + b"E" + b"\x01"   # Bold ON
        data += GS + b"!" + tanlangan_size

        for line in lines:
            data += line.encode("ascii", "ignore")
            data += b"\n"

        data += GS + b"!" + b"\x00"    # Normal o'lcham
        data += ESC + b"E" + b"\x00"   # Bold OFF
        data += b"\n\n\n"              # Qog'oz surish

    return data


# ============================================================
#  BLUETOOTH PRINT
# ============================================================

def bt_qurilmalar():
    """Ulangan (paired) Bluetooth qurilmalar ro'yxati"""
    if not ANDROID:
        return ["TEST-PRINTER"]
    try:
        adapter = BluetoothAdapter.getDefaultAdapter()
        if adapter is None:
            return []
        paired = adapter.getBondedDevices().toArray()
        return [d.getName() for d in paired if d.getName()]
    except Exception:
        return []


def bt_chop_et(device_name, data):
    """Bluetooth orqali TSPL yuborish"""
    if not ANDROID:
        print("TEST MODE — TSPL:")
        print(data.decode("ascii"))
        return True
    
    try:
        adapter = BluetoothAdapter.getDefaultAdapter()
        if adapter is None:
            return "Bluetooth mavjud emas"
        if not adapter.isEnabled():
            return "Bluetooth o'chirilgan — yoqing!"
        
        paired = adapter.getBondedDevices().toArray()
        device = None
        for d in paired:
            if d.getName() == device_name:
                device = d
                break
        
        if device is None:
            return f"'{device_name}' topilmadi. Avval Bluetooth sozlamalarida ulang (pair)."
        
        import time as _t
        socket = device.createRfcommSocketToServiceRecord(
            UUID.fromString(SPP_UUID))
        socket.connect()
        out = socket.getOutputStream()
        
        # Ma'lumotni bo'laklab yuborish (chunk) — printer bufferi kichik
        CHUNK = 128
        for i in range(0, len(data), CHUNK):
            out.write(data[i:i+CHUNK])
            out.flush()
            _t.sleep(0.03)  # printerga ulgurish uchun
        
        # Printer bosib chiqarishga ulgurishi uchun kutamiz
        _t.sleep(1.2)
        out.close()
        socket.close()
        return True
    except Exception as e:
        return f"Bluetooth xato: {e}"


# ============================================================
#  APP
# ============================================================

class MarkirovkaApp(App):
    title = "Markirovka"
    
    def build(self):
        Window.clearcolor = (0.10, 0.10, 0.18, 1)
        
        self.data_file = os.path.join(self.user_data_dir, "mahsulotlar.json")
        self.sozlama_file = os.path.join(self.user_data_dir, "sozlamalar.json")
        
        if ANDROID:
            request_permissions([
                Permission.BLUETOOTH,
                Permission.BLUETOOTH_ADMIN,
                Permission.BLUETOOTH_CONNECT,
                Permission.BLUETOOTH_SCAN,
            ])
        
        root = BoxLayout(orientation="vertical")
        
        # ===== HEADER =====
        header = BoxLayout(size_hint_y=None, height="56dp",
                          padding=["8dp", "4dp"], spacing="6dp")
        
        header.add_widget(Label(text=f"[b]MARKIROVKA[/b] [size=11sp][color=888888]v{VERSIYA}[/color][/size]",
                               markup=True,
                               font_size="20sp", size_hint_x=0.4,
                               halign="left"))
        
        self.nusxa_input = TextInput(text="1", multiline=False,
                                    input_filter="int",
                                    size_hint_x=0.12,
                                    font_size="18sp",
                                    halign="center")
        header.add_widget(Label(text="Nusxa:", size_hint_x=0.12,
                               font_size="14sp"))
        header.add_widget(self.nusxa_input)
        
        admin_btn = Button(text="Admin", size_hint_x=0.18,
                          background_color=(0.90, 0.49, 0.13, 1),
                          background_normal="")
        admin_btn.bind(on_release=self.open_admin)
        header.add_widget(admin_btn)
        
        sozlama_btn = Button(text="Printer", size_hint_x=0.18,
                            background_color=(0.56, 0.27, 0.68, 1),
                            background_normal="")
        sozlama_btn.bind(on_release=self.open_settings)
        header.add_widget(sozlama_btn)
        
        root.add_widget(header)
        
        # ===== GRID (scroll) =====
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=3, spacing="8dp", padding="8dp",
                              size_hint_y=None, row_default_height="110dp",
                              row_force_default=True)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        self.scroll.add_widget(self.grid)
        root.add_widget(self.scroll)
        
        # ===== STATUS =====
        self.status = Label(text="Tayyor", size_hint_y=None, height="36dp",
                           font_size="14sp", color=(0.30, 0.79, 0.94, 1))
        root.add_widget(self.status)
        
        self.refresh_grid()
        return root
    
    # ---------- DATA ----------
    
    def mahsulot_yuklash(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return STANDART_MAHSULOTLAR[:]
    
    def mahsulot_saqlash(self, lst):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(lst, f, ensure_ascii=False, indent=2)
    
    def sozlama_yuklash(self):
        if os.path.exists(self.sozlama_file):
            with open(self.sozlama_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"printer": ""}
    
    def sozlama_saqlash(self, s):
        with open(self.sozlama_file, "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False, indent=2)
    
    # ---------- GRID ----------
    
    def refresh_grid(self):
        self.grid.clear_widgets()
        for i, m in enumerate(self.mahsulot_yuklash()):
            rang = RANGLAR[i % len(RANGLAR)]
            btn = Button(text=m["nomi"],
                        font_size="15sp",
                        bold=True,
                        halign="center", valign="middle",
                        background_color=rang,
                        background_normal="")
            btn.text_size = (None, None)
            btn.bind(size=self._update_text_size)
            btn.mahsulot = m
            btn.bind(on_release=self.chop_et)
            self.grid.add_widget(btn)
    
    def _update_text_size(self, btn, size):
        btn.text_size = (size[0] - 16, None)
    
    # ---------- PRINT ----------
    
    def chop_et(self, btn):
        m = btn.mahsulot
        try:
            nusxa = max(1, int(self.nusxa_input.text or "1"))
        except ValueError:
            nusxa = 1
        
        s = self.sozlama_yuklash()
        printer = s.get("printer", "")
        
        if not printer:
            self.status.text = "Printer tanlanmagan! 'Printer' tugmasini bosing."
            self.status.color = (0.91, 0.30, 0.24, 1)
            return
        
        self.status.text = f"Chop etilmoqda: {m['nomi']}..."
        self.status.color = (0.95, 0.61, 0.07, 1)
        
        def _do_print(dt):
            protokol = s.get("protokol", "ESC/POS")
            if protokol == "TSPL":
                data = tspl_yarat(m["nomi"], nusxa)
            else:
                data = escpos_yarat(m["nomi"], nusxa)
            result = bt_chop_et(printer, data)
            if result is True:
                self.status.text = f"Chop etildi: {m['nomi']} ({nusxa} nusxa)"
                self.status.color = (0.15, 0.68, 0.38, 1)
            else:
                self.status.text = str(result)
                self.status.color = (0.91, 0.30, 0.24, 1)
        
        Clock.schedule_once(_do_print, 0.1)
    
    # ---------- SETTINGS ----------
    
    def open_settings(self, *args):
        s = self.sozlama_yuklash()
        qurilmalar = bt_qurilmalar()
        
        box = BoxLayout(orientation="vertical", spacing="10dp", padding="12dp")
        
        box.add_widget(Label(text="Bluetooth printer tanlang:\n(Avval Android Bluetooth sozlamalarida\nprinterni ulang — pair qiling)",
                            size_hint_y=None, height="80dp", font_size="14sp"))
        
        spinner = Spinner(text=s.get("printer") or "Tanlang...",
                         values=qurilmalar if qurilmalar else ["Qurilma topilmadi"],
                         size_hint_y=None, height="48dp",
                         font_size="16sp")
        box.add_widget(spinner)
        
        # Protokol tanlash
        box.add_widget(Label(text="Protokol (XP-326B uchun ESC/POS):",
                            size_hint_y=None, height="32dp", font_size="13sp"))
        protokol_spinner = Spinner(text=s.get("protokol", "ESC/POS"),
                                  values=["ESC/POS", "TSPL"],
                                  size_hint_y=None, height="48dp",
                                  font_size="16sp")
        box.add_widget(protokol_spinner)
        
        btn_box = BoxLayout(size_hint_y=None, height="48dp", spacing="8dp")
        
        save_btn = Button(text="Saqlash",
                         background_color=(0.15, 0.68, 0.38, 1),
                         background_normal="")
        cancel_btn = Button(text="Bekor",
                           background_color=(0.58, 0.65, 0.65, 1),
                           background_normal="")
        btn_box.add_widget(save_btn)
        btn_box.add_widget(cancel_btn)
        box.add_widget(btn_box)
        
        # TEST tugmasi
        test_btn = Button(text="🖨 TEST CHOP (ikkala protokolni sinash)",
                         size_hint_y=None, height="48dp",
                         background_color=(0.90, 0.49, 0.13, 1),
                         background_normal="")
        box.add_widget(test_btn)
        
        test_status = Label(text="", size_hint_y=None, height="60dp",
                           font_size="12sp")
        box.add_widget(test_status)
        box.add_widget(Label())  # spacer
        
        def _test(*a):
            if spinner.text in ("Tanlang...", "Qurilma topilmadi"):
                test_status.text = "Avval printer tanlang!"
                test_status.color = (0.91, 0.30, 0.24, 1)
                return
            printer_name = spinner.text
            test_status.text = "Yuborilmoqda..."
            test_status.color = (0.95, 0.61, 0.07, 1)
            
            def _do(dt):
                # 1) ESC/POS oddiy matn
                escpos_test = (b"\x1b@" + b"\x1ba\x01" +
                               b"=== TEST ===\n" +
                               b"ESC/POS ishladi\n\n\n")
                r1 = bt_chop_et(printer_name, escpos_test)
                _t2 = __import__("time")
                _t2.sleep(0.5)
                # 2) TSPL oddiy
                tspl_test = (
                    "SIZE 40 mm, 30 mm\r\nGAP 2 mm, 0 mm\r\nCLS\r\n"
                    'TEXT 30,80,"3",0,1,1,"TSPL TEST"\r\n'
                    "PRINT 1,1\r\n"
                ).encode("ascii")
                r2 = bt_chop_et(printer_name, tspl_test)
                
                natija = "ESC/POS: "
                natija += "OK" if r1 is True else str(r1)[:20]
                natija += "\nTSPL: "
                natija += "OK" if r2 is True else str(r2)[:20]
                natija += "\n\nQaysi biri chop chiqdi?\nShu protokolni tanlang!"
                test_status.text = natija
                test_status.color = (0.15, 0.68, 0.38, 1)
            
            from kivy.clock import Clock as _C
            _C.schedule_once(_do, 0.1)
        
        test_btn.bind(on_release=_test)
        
        popup = Popup(title=f"Printer sozlamalari  (v{VERSIYA})", content=box,
                     size_hint=(0.95, 0.85))
        
        def _save(*a):
            if spinner.text not in ("Tanlang...", "Qurilma topilmadi"):
                s["printer"] = spinner.text
            s["protokol"] = protokol_spinner.text
            self.sozlama_saqlash(s)
            self.status.text = f"Printer: {s.get('printer','—')} | {protokol_spinner.text}"
            self.status.color = (0.15, 0.68, 0.38, 1)
            popup.dismiss()
        
        save_btn.bind(on_release=_save)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()
    
    # ---------- ADMIN ----------
    
    def open_admin(self, *args):
        box = BoxLayout(orientation="vertical", spacing="8dp", padding="10dp")
        
        # Add form
        add_box = BoxLayout(size_hint_y=None, height="48dp", spacing="6dp")
        nomi_input = TextInput(hint_text="Yangi mahsulot nomi",
                              multiline=False, font_size="16sp")
        add_btn = Button(text="+", size_hint_x=0.2,
                        background_color=(0.15, 0.68, 0.38, 1),
                        background_normal="", font_size="22sp", bold=True)
        add_box.add_widget(nomi_input)
        add_box.add_widget(add_btn)
        box.add_widget(add_box)
        
        # List
        scroll = ScrollView()
        lst_grid = GridLayout(cols=1, spacing="4dp", size_hint_y=None)
        lst_grid.bind(minimum_height=lst_grid.setter("height"))
        scroll.add_widget(lst_grid)
        box.add_widget(scroll)
        
        popup = Popup(title="Admin — Mahsulotlar", content=box,
                     size_hint=(0.95, 0.9))
        
        def refresh_admin_list():
            lst_grid.clear_widgets()
            for m in self.mahsulot_yuklash():
                row = BoxLayout(size_hint_y=None, height="44dp", spacing="4dp")
                row.add_widget(Label(text=m["nomi"], font_size="14sp",
                                    halign="left", valign="middle",
                                    text_size=(None, None), size_hint_x=0.6))
                
                edit_btn = Button(text="Edit", size_hint_x=0.2,
                                 background_color=(0.20, 0.60, 0.86, 1),
                                 background_normal="")
                del_btn = Button(text="X", size_hint_x=0.15,
                                background_color=(0.91, 0.30, 0.24, 1),
                                background_normal="")
                
                edit_btn.mahsulot = m
                del_btn.mahsulot = m
                
                edit_btn.bind(on_release=lambda b: _edit(b.mahsulot))
                del_btn.bind(on_release=lambda b: _delete(b.mahsulot))
                
                row.add_widget(edit_btn)
                row.add_widget(del_btn)
                lst_grid.add_widget(row)
        
        def _add(*a):
            nomi = nomi_input.text.strip()
            if not nomi:
                return
            lst = self.mahsulot_yuklash()
            nid = max((x["id"] for x in lst), default=0) + 1
            lst.append({"id": nid, "nomi": nomi})
            self.mahsulot_saqlash(lst)
            nomi_input.text = ""
            refresh_admin_list()
            self.refresh_grid()
        
        def _delete(m):
            lst = [x for x in self.mahsulot_yuklash() if x["id"] != m["id"]]
            self.mahsulot_saqlash(lst)
            refresh_admin_list()
            self.refresh_grid()
        
        def _edit(m):
            e_box = BoxLayout(orientation="vertical", spacing="10dp",
                             padding="12dp")
            e_input = TextInput(text=m["nomi"], multiline=False,
                               font_size="16sp", size_hint_y=None,
                               height="48dp")
            e_box.add_widget(e_input)
            
            e_btns = BoxLayout(size_hint_y=None, height="48dp", spacing="8dp")
            e_save = Button(text="Saqlash",
                           background_color=(0.15, 0.68, 0.38, 1),
                           background_normal="")
            e_cancel = Button(text="Bekor",
                             background_color=(0.58, 0.65, 0.65, 1),
                             background_normal="")
            e_btns.add_widget(e_save)
            e_btns.add_widget(e_cancel)
            e_box.add_widget(e_btns)
            e_box.add_widget(Label())
            
            e_popup = Popup(title=f"Tahrirlash: {m['nomi']}",
                           content=e_box, size_hint=(0.9, 0.5))
            
            def _save_edit(*a):
                yangi = e_input.text.strip()
                if yangi:
                    lst = self.mahsulot_yuklash()
                    for x in lst:
                        if x["id"] == m["id"]:
                            x["nomi"] = yangi
                            break
                    self.mahsulot_saqlash(lst)
                    refresh_admin_list()
                    self.refresh_grid()
                e_popup.dismiss()
            
            e_save.bind(on_release=_save_edit)
            e_cancel.bind(on_release=e_popup.dismiss)
            e_popup.open()
        
        add_btn.bind(on_release=_add)
        refresh_admin_list()
        popup.open()


if __name__ == "__main__":
    MarkirovkaApp().run()
