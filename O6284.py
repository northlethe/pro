import sys
import zipfile
import os
import tempfile
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, 
                             QPushButton, QCheckBox, QTextEdit, QGroupBox, QGridLayout, QComboBox,
                             QDateEdit, QTabWidget, QStyledItemDelegate, QStyleOptionViewItem, QScrollArea)
from PyQt6.QtCore import Qt, QDate, QSize, QEvent
from PyQt6.QtGui import QFont, QTextOption, QFontMetrics

class WordWrapDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        option.textElideMode = Qt.TextElideMode.ElideNone
        option.features |= QStyleOptionViewItem.ViewItemFeature.WrapText
        super().paint(painter, option, index)

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        text = index.data(Qt.ItemDataRole.DisplayRole)
        width = option.rect.width()
        font = QFont()
        font.setPointSize(10)
        metrics = QFontMetrics(font)
        height = metrics.boundingRect(0, 0, width, 1000, Qt.TextFlag.TextWordWrap, text).height()
        return QSize(width, height + 10)

class UDFGeneratorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('UDF Generator')
        self.setGeometry(100, 100, 800, 600)
        layout = QVBoxLayout()
                
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        self.tab_widget = QTabWidget()
        self.emniyet_onama_tab = QWidget()
        self.bireysel_talep_tab = QWidget()
        self.kisisel_esya_teslimi_tab = QWidget()
        self.zorlama_hapsi_tab = QWidget()
        self.ihlal_tensibi_tab = QWidget()
        self.tab_widget.addTab(self.emniyet_onama_tab, "Emniyet Onama")
        self.tab_widget.addTab(self.bireysel_talep_tab, "Bireysel Talep")
        self.tab_widget.addTab(self.kisisel_esya_teslimi_tab, "Kişisel Eşya Teslimi")
        self.tab_widget.addTab(self.zorlama_hapsi_tab, "Zorlama Hapsi")
        self.tab_widget.addTab(self.ihlal_tensibi_tab, "İhlal Tensibi")

        self.create_emniyet_onama_tab()
        self.create_bireysel_talep_tab()
        self.create_kisisel_esya_teslimi_tab()
        self.create_zorlama_hapsi_tab()
        self.create_ihlal_tensibi_tab()

        layout.addWidget(self.tab_widget)

        self.setLayout(layout)

        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Wheel:
            focused_widget = QApplication.focusWidget()
            if isinstance(focused_widget, QDateEdit):
                return True
        return super().eventFilter(obj, event)

    def create_date_edit(self):
        date_edit = QDateEdit()
        date_edit.setDate(QDate.currentDate())
        date_edit.setCalendarPopup(True)
        date_edit.setDisplayFormat("dd.MM.yyyy")
        date_edit.setFixedWidth(100)
        return date_edit

    def create_emniyet_onama_tab(self):
        layout = QVBoxLayout()

        date_number_layout = QGridLayout()
        date_number_layout.addWidget(QLabel('Havale Tarihi:'), 0, 0)
        self.havale_tarih = self.create_date_edit()
        date_number_layout.addWidget(self.havale_tarih, 0, 1)
        
        sayi_label = QLabel('Sayı:')
        sayi_label.setFixedWidth(40)
        date_number_layout.addWidget(sayi_label, 0, 2)
        self.sayili = QLineEdit()
        date_number_layout.addWidget(self.sayili, 0, 3)
        
        date_number_layout.addWidget(QLabel('Olay Tarihi:'), 1, 0)
        self.olay_tarihi = self.create_date_edit()
        date_number_layout.addWidget(self.olay_tarihi, 1, 1)
        layout.addLayout(date_number_layout)
        
        eylemler_group = QGroupBox("Eylemler")
        eylemler_layout = QGridLayout()
        self.eylemler = {}
        eylemler_list = ["Tehdit", "Hakaret", "Mala Zarar Verme", "Şantaj", "Yaralama", "Israrlı Takip", "Cinsel Taciz"]
        for i, eylem in enumerate(eylemler_list):
            self.eylemler[eylem] = QCheckBox(eylem)
            eylemler_layout.addWidget(self.eylemler[eylem], i // 3, i % 3)
        eylemler_group.setLayout(eylemler_layout)
        layout.addWidget(eylemler_group)

        emniyet_group = QGroupBox("Emniyetin Verdiği Maddeler")
        emniyet_layout = QGridLayout()
        self.emniyet_maddeleri = {}
        for i, harf in enumerate('abcdefgh'):
            self.emniyet_maddeleri[harf] = QCheckBox(f'5/1-{harf}')
            if harf in 'acd':
                self.emniyet_maddeleri[harf].setChecked(True)
            emniyet_layout.addWidget(self.emniyet_maddeleri[harf], i // 4, i % 4)
        emniyet_group.setLayout(emniyet_layout)
        layout.addWidget(emniyet_group)

        mahkeme_group = QGroupBox("Mahkemenin Vereceği Maddeler")
        mahkeme_layout = QGridLayout()
        self.emniyet_mahkeme_maddeleri = {}
        for i, harf in enumerate('abcdefgh'):
            self.emniyet_mahkeme_maddeleri[harf] = QCheckBox(f'5/1-{harf}')
            if harf in 'acd':
                self.emniyet_mahkeme_maddeleri[harf].setChecked(True)
            mahkeme_layout.addWidget(self.emniyet_mahkeme_maddeleri[harf], i // 4, i % 4)
        mahkeme_group.setLayout(mahkeme_layout)
        layout.addWidget(mahkeme_group)

        layout.addWidget(QLabel('Şüpheli:'))
        self.emniyet_supheli = QLineEdit()
        layout.addWidget(self.emniyet_supheli)

        layout.addWidget(QLabel('Mağdur:'))
        self.emniyet_magdur = QLineEdit()
        layout.addWidget(self.emniyet_magdur)

        layout.addWidget(QLabel('Tedbir Gün:'))
        self.emniyet_tedbir_gun = QComboBox()
        self.emniyet_tedbir_gun.addItems(['30 GÜN', '60 GÜN', '90 GÜN', '180 GÜN'])
        layout.addWidget(self.emniyet_tedbir_gun)

        layout.addWidget(QLabel('Mağdur Beyanı:'))
        self.emniyet_magdur_beyani = QTextEdit()
        self.emniyet_magdur_beyani.setText("Talep edenin kolluk beyanında, kendisine yönelik olarak ... şeklinde ifadeler kullandığını bu nedenle karşı taraf hakkında önleyici tedbir kararı verilmesini talep etmiştir.")
        self.emniyet_magdur_beyani.setMinimumHeight(150)
        font = QFont()
        font.setPointSize(11)
        self.emniyet_magdur_beyani.setFont(font)
        layout.addWidget(self.emniyet_magdur_beyani)

        self.emniyet_create_button = QPushButton('UDF Oluştur')
        self.emniyet_create_button.clicked.connect(self.create_emniyet_udf)
        layout.addWidget(self.emniyet_create_button)

        self.emniyet_onama_tab.setLayout(layout)

    def create_bireysel_talep_tab(self):
        layout = QVBoxLayout()

        date_layout = QGridLayout()
        date_layout.addWidget(QLabel('Başvuru Tarihi:'), 0, 0)
        self.basvuru_tarih = self.create_date_edit()
        date_layout.addWidget(self.basvuru_tarih, 0, 1)
        date_layout.setColumnStretch(2, 1)  # Add stretch to push the date field to the left
        layout.addLayout(date_layout)

        mahkeme_group = QGroupBox("Mahkemenin Vereceği Maddeler")
        mahkeme_layout = QGridLayout()
        self.bireysel_mahkeme_maddeleri = {}
        for i, harf in enumerate('abcdefgh'):
            self.bireysel_mahkeme_maddeleri[harf] = QCheckBox(f'5/1-{harf}')
            if harf in 'acd':
                self.bireysel_mahkeme_maddeleri[harf].setChecked(True)
            mahkeme_layout.addWidget(self.bireysel_mahkeme_maddeleri[harf], i // 4, i % 4)
        mahkeme_group.setLayout(mahkeme_layout)
        layout.addWidget(mahkeme_group)

        layout.addWidget(QLabel('Şüpheli:'))
        self.bireysel_supheli = QLineEdit()
        layout.addWidget(self.bireysel_supheli)

        layout.addWidget(QLabel('Mağdur:'))
        self.bireysel_magdur = QLineEdit()
        layout.addWidget(self.bireysel_magdur)

        layout.addWidget(QLabel('Tedbir Gün:'))
        self.bireysel_tedbir_gun = QComboBox()
        self.bireysel_tedbir_gun.addItems(['30 GÜN', '60 GÜN', '90 GÜN', '180 GÜN'])
        layout.addWidget(self.bireysel_tedbir_gun)

        layout.addWidget(QLabel('Mağdur Beyanı:'))
        self.bireysel_magdur_beyani = QTextEdit()
        self.bireysel_magdur_beyani.setText("Talep edenin dilekçesinde, karşı tarafın kendisine yönelik olarak ... şeklinde ifadeler kullandığını bu nedenle karşı taraf hakkında önleyici tedbir kararı verilmesini talep etmektedir.")
        self.bireysel_magdur_beyani.setFixedHeight(100)  # Set a fixed height to make it smaller
        layout.addWidget(self.bireysel_magdur_beyani)

        self.bireysel_create_button = QPushButton('UDF Oluştur')
        self.bireysel_create_button.clicked.connect(self.create_bireysel_udf)
        layout.addWidget(self.bireysel_create_button)

        layout.addStretch(1)  # Add stretch at the end to push everything up

        self.bireysel_talep_tab.setLayout(layout)

    def create_kisisel_esya_teslimi_tab(self):
        layout = QVBoxLayout()

        date_layout = QGridLayout()
        date_layout.addWidget(QLabel('Tarih:'), 0, 0)
        self.kisisel_esya_tarih = self.create_date_edit()
        date_layout.addWidget(self.kisisel_esya_tarih, 0, 1)
        date_layout.setColumnStretch(2, 1)  # Add stretch to push the date field to the left
        layout.addLayout(date_layout)

        layout.addWidget(QLabel('Adres:'))
        self.kisisel_esya_adres = QLineEdit()
        layout.addWidget(self.kisisel_esya_adres)

        layout.addWidget(QLabel('Mağdur:'))
        self.kisisel_esya_magdur = QLineEdit()
        layout.addWidget(self.kisisel_esya_magdur)

        layout.addWidget(QLabel('Eşyalar:'))
        self.kisisel_esya_esyalar = QTextEdit()
        self.kisisel_esya_esyalar.setFixedHeight(100)  # Set a fixed height to make it smaller
        layout.addWidget(self.kisisel_esya_esyalar)

        self.kisisel_esya_create_button = QPushButton('UDF Oluştur')
        self.kisisel_esya_create_button.clicked.connect(self.create_kisisel_esya_udf)
        layout.addWidget(self.kisisel_esya_create_button)

        layout.addStretch(1)  # Add stretch at the end to push everything up

        self.kisisel_esya_teslimi_tab.setLayout(layout)
    def create_zorlama_hapsi_tab(self):
        layout = QVBoxLayout()

        date_number_layout = QGridLayout()
        date_number_layout.addWidget(QLabel('Tarih:'), 0, 0)
        self.zh_tarih = self.create_date_edit()
        date_number_layout.addWidget(self.zh_tarih, 0, 1)
        
        date_number_layout.addWidget(QLabel('Sayı:'), 0, 2)
        self.zh_sayi = QLineEdit()
        date_number_layout.addWidget(self.zh_sayi, 0, 3)
        
        layout.addLayout(date_number_layout)

        layout.addWidget(QLabel('Emniyet:'))
        self.zh_emniyet = QLineEdit('Sapanca')
        layout.addWidget(self.zh_emniyet)

        layout.addWidget(QLabel('Karar Tarihi:'))
        self.zh_karar_tarih = self.create_date_edit()
        layout.addWidget(self.zh_karar_tarih)

        layout.addWidget(QLabel('Muhalefet Tarihi:'))
        self.zh_muhalefet_tarih = self.create_date_edit()
        layout.addWidget(self.zh_muhalefet_tarih)

        layout.addWidget(QLabel('Muhalif Olan Kişi:'))
        self.zh_muhalif_kisi = QLineEdit()
        layout.addWidget(self.zh_muhalif_kisi)

        layout.addWidget(QLabel('Karar Tebliğ Tarihi:'))
        self.zh_karar_teblig_tarih = self.create_date_edit()
        layout.addWidget(self.zh_karar_teblig_tarih)

        layout.addWidget(QLabel('Savcılık Yazı Tarihi:'))
        self.zh_savcilik_yazi_tarih = self.create_date_edit()
        layout.addWidget(self.zh_savcilik_yazi_tarih)

        layout.addWidget(QLabel('Savcılık Esas:'))
        self.zh_savcilik_esas = QLineEdit()
        layout.addWidget(self.zh_savcilik_esas)

        layout.addWidget(QLabel('Muhalif Olan Kişi TC:'))
        self.zh_muhalif_kisi_tc = QLineEdit()
        layout.addWidget(self.zh_muhalif_kisi_tc)

        layout.addWidget(QLabel('Hapis Günü:'))
        self.zh_hapis_gunu = QLineEdit('3')
        layout.addWidget(self.zh_hapis_gunu)

        layout.addWidget(QLabel('İhlal Edilen Tedbir:'))
        self.zh_ihlal_edilen_tedbir = QComboBox()
        self.zh_ihlal_edilen_tedbir.setFixedWidth(200)
        
        tedbir_items = [
            ("6284 sayılı yasanın 5/1-a maddesi", "Şiddet mağduruna yönelik olarak şiddet tehdidi, hakaret, aşağılama veya küçük düşürmeyi içeren söz ve davranışlarda bulunmaması tedbirini"),
            ("6284 sayılı yasanın 5/1-b maddesi", "Müşterek konuttan veya bulunduğu yerden derhal uzaklaştırılması ve müşterek konutun korunan kişiye tahsis edilmesinin tedbirini"),
            ("6284 sayılı yasanın 5/1-c maddesi", "Korunan kişilere, bu kişilerin bulundukları konuta, okula ve işyerine yaklaşmaması tedbirini"),
            ("6284 sayılı yasanın 5/1-d maddesi", "Korunan kişinin, şiddete uğramamış olsa bile yakınlarına, tanıklarına ve kişisel ilişki kurulmasına ilişkin hâller saklı kalmak üzere çocuklarına yaklaşmaması tedbirini"),
            ("6284 sayılı yasanın 5/1-e maddesi", "Korunan kişinin şahsi eşyalarına ve ev eşyalarına zarar vermemesi tedbirini"),
            ("6284 sayılı yasanın 5/1-f maddesi", "Korunan kişiyi iletişim araçlarıyla veya sair surette rahatsız etmemesi tedbirini"),
            ("6284 sayılı yasanın 5/1-g maddesi", "Bulundurulması veya taşınmasına kanunen izin verilen silahları kolluğa teslim etmesi tedbirini"),
            ("6284 sayılı yasanın 5/1-h maddesi", "Korunan kişilerin bulundukları yerlerde alkol ya da uyuşturucu veya uyarıcı madde kullanmaması ya da bu maddelerin etkisinde iken korunan kişilere ve bunların bulundukları yerlere yaklaşmaması, bağımlılığının olması hâlinde, hastaneye yatmak dâhil, muayene ve tedavisinin sağlanması tedbirini")
        ]
        
        for short_text, full_text in tedbir_items:
            self.zh_ihlal_edilen_tedbir.addItem(short_text, full_text)
        
        layout.addWidget(self.zh_ihlal_edilen_tedbir)

        layout.addWidget(QLabel('Karar Tipi:'))
        self.zh_karar_tipi = QComboBox()
        self.zh_karar_tipi.addItems(["Kabul", "Ret"])
        layout.addWidget(self.zh_karar_tipi)

        self.zh_create_button = QPushButton('UDF Oluştur')
        self.zh_create_button.clicked.connect(self.create_zorlama_hapsi_udf)
        layout.addWidget(self.zh_create_button)

        self.zorlama_hapsi_tab.setLayout(layout)

    def create_ihlal_tensibi_tab(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel('Savcılık Adı:'))
        self.ihlal_savcilik_adi = QLineEdit()
        layout.addWidget(self.ihlal_savcilik_adi)

        layout.addWidget(QLabel('Savcılık Esas:'))
        self.ihlal_savcilik_esas = QLineEdit()
        layout.addWidget(self.ihlal_savcilik_esas)

        layout.addWidget(QLabel('Mahkeme Esas No:'))
        self.ihlal_mahkeme_esas_no = QLineEdit()
        layout.addWidget(self.ihlal_mahkeme_esas_no)

        layout.addWidget(QLabel('Mahkeme Karar No:'))
        self.ihlal_mahkeme_karar_no = QLineEdit()
        layout.addWidget(self.ihlal_mahkeme_karar_no)

        layout.addWidget(QLabel('Mahkeme Karar Tarihi:'))
        self.ihlal_mahkeme_karar_tarihi = self.create_date_edit()
        layout.addWidget(self.ihlal_mahkeme_karar_tarihi)

        layout.addWidget(QLabel('Karar İhlal Tarihi:'))
        self.ihlal_karar_ihlal_tarihi = self.create_date_edit()
        layout.addWidget(self.ihlal_karar_ihlal_tarihi)

        layout.addWidget(QLabel('Kararı İhlal Eden Kişi:'))
        self.ihlal_karari_ihlal_eden_kisi = QLineEdit()
        layout.addWidget(self.ihlal_karari_ihlal_eden_kisi)

        self.ihlal_create_button = QPushButton('UDF Oluştur')
        self.ihlal_create_button.clicked.connect(self.create_ihlal_tensibi_udf)
        layout.addWidget(self.ihlal_create_button)

        self.ihlal_tensibi_tab.setLayout(layout)

    def create_emniyet_udf(self):
        xhavaletarih = self.havale_tarih.date().toString("dd.MM.yyyy")
        xsayili = self.sayili.text()
        xolaytarihi = self.olay_tarihi.date().toString("dd.MM.yyyy")
        xeylemler = ', '.join([eylem for eylem, checkbox in self.eylemler.items() if checkbox.isChecked()])
        xemniyetmaddeleriharfler = ','.join([harf for harf, checkbox in self.emniyet_maddeleri.items() if checkbox.isChecked()])
        xmahkememaddeleriharfler = ','.join([harf for harf, checkbox in self.emniyet_mahkeme_maddeleri.items() if checkbox.isChecked()])
        xsupheli = self.emniyet_supheli.text()
        xmagdur = self.emniyet_magdur.text()
        xtedbirgunGUN = self.emniyet_tedbir_gun.currentText()
        xmagdurbeyanı = self.emniyet_magdur_beyani.toPlainText()

        xmahkememaddelerigenişletilmiş = self.get_extended_mahkeme_maddeleri(self.emniyet_mahkeme_maddeleri)

        create_emniyet_udf_content(xhavaletarih, xsayili, xolaytarihi, xeylemler, xemniyetmaddeleriharfler, 
                                   xmahkememaddeleriharfler, xsupheli, xmagdur, xtedbirgunGUN, xmagdurbeyanı,
                                   xmahkememaddelerigenişletilmiş)

    def create_bireysel_udf(self):
        xbasvurutarihi = self.basvuru_tarih.date().toString("dd.MM.yyyy")
        xmahkememaddeleriharfler = ','.join([harf for harf, checkbox in self.bireysel_mahkeme_maddeleri.items() if checkbox.isChecked()])
        xsupheli = self.bireysel_supheli.text()
        xmagdur = self.bireysel_magdur.text()
        xtedbirgunGUN = self.bireysel_tedbir_gun.currentText()
        xmagdurbeyanı = self.bireysel_magdur_beyani.toPlainText()

        xmahkememaddelerigenişletilmiş = self.get_extended_mahkeme_maddeleri(self.bireysel_mahkeme_maddeleri)

        create_bireysel_udf_content(xbasvurutarihi, xmahkememaddeleriharfler, xsupheli, xmagdur, xtedbirgunGUN, xmagdurbeyanı,
                                    xmahkememaddelerigenişletilmiş)

    def create_kisisel_esya_udf(self):
        xtarihli = self.kisisel_esya_tarih.date().toString("dd.MM.yyyy")
        xadres = self.kisisel_esya_adres.text()
        xmagdur = self.kisisel_esya_magdur.text()
        xesyalar = self.kisisel_esya_esyalar.toPlainText()

        create_kisisel_esya_udf_content(xtarihli, xadres, xmagdur, xesyalar)

    def create_zorlama_hapsi_udf(self):
        xtarih = self.zh_tarih.date().toString("dd.MM.yyyy")
        xsayi = self.zh_sayi.text()
        xemniyet = self.zh_emniyet.text()
        xkarartarih = self.zh_karar_tarih.date().toString("dd.MM.yyyy")
        xmualefettarihi = self.zh_muhalefet_tarih.date().toString("dd.MM.yyyy")
        xmualifolankisi = self.zh_muhalif_kisi.text()
        xkarartebligtarihi = self.zh_karar_teblig_tarih.date().toString("dd.MM.yyyy")
        xsavcilikyazitarihi = self.zh_savcilik_yazi_tarih.date().toString("dd.MM.yyyy")
        xsavcilikesası = self.zh_savcilik_esas.text()
        xmualifolankisiTcno = self.zh_muhalif_kisi_tc.text()
        xhapisgünü = self.zh_hapis_gunu.text()
        xihlaledilentedbir = self.zh_ihlal_edilen_tedbir.currentData()

        karar_tipi = self.zh_karar_tipi.currentText().upper()

        create_zorlama_hapsi_udf_content(xtarih, xsayi, xemniyet, xkarartarih, xmualefettarihi, xmualifolankisi,
                                         xkarartebligtarihi, xsavcilikyazitarihi, xsavcilikesası, xmualifolankisiTcno,
                                         xhapisgünü, xihlaledilentedbir, karar_tipi)

    def create_ihlal_tensibi_udf(self):
        xsavcilikadi = self.ihlal_savcilik_adi.text()
        xsavcilikesas = self.ihlal_savcilik_esas.text()
        xmahkemeesasno = self.ihlal_mahkeme_esas_no.text()
        xmahkemekararno = self.ihlal_mahkeme_karar_no.text()
        xmahkemekarartarihi = self.ihlal_mahkeme_karar_tarihi.date().toString("dd.MM.yyyy")
        xkararihlaltarihi = self.ihlal_karar_ihlal_tarihi.date().toString("dd.MM.yyyy")
        xkararıihlaledenkisi = self.ihlal_karari_ihlal_eden_kisi.text()

        create_ihlal_tensibi_udf_content(xsavcilikadi, xsavcilikesas, xmahkemeesasno, xmahkemekararno,
                                         xmahkemekarartarihi, xkararihlaltarihi, xkararıihlaledenkisi)

    def get_extended_mahkeme_maddeleri(self, mahkeme_maddeleri):
        extended_maddeleri = []
        madde_aciklamalari = {
            'a': "6284 sayılı yasanın 5/1-a maddesi: Şiddet mağduruna yönelik olarak şiddet tehdidi, hakaret, aşağılama veya küçük düşürmeyi içeren söz ve davranışlarda bulunmaması UYGULANMASINA,",
            'b': "6284 sayılı yasanın 5/1-b maddesi: Müşterek konuttan veya bulunduğu yerden derhal uzaklaştırılması ve müşterek konutun korunan kişiye tahsis edilmesi UYGULANMASINA,",
            'c': "6284 sayılı yasanın 5/1-c maddesi: Korunan kişilere, bu kişilerin bulundukları konuta, okula ve işyerine yaklaşmaması UYGULANMASINA,",
            'd': "6284 sayılı yasanın 5/1-d maddesi: Çocuklarla kişisel ilişkinin refakatçi eşliğinde yapılması, kişisel ilişkinin sınırlanması ya da tümüyle kaldırılması UYGULANMASINA,",
            'e': "6284 sayılı yasanın 5/1-e maddesi: Korunan kişinin şahsi eşyalarına ve ev eşyalarına zarar vermemesi UYGULANMASINA,",
            'f': "6284 sayılı yasanın 5/1-f maddesi: Korunan kişiyi iletişim araçlarıyla veya sair surette rahatsız etmemesi UYGULANMASINA,",
            'g': "6284 sayılı yasanın 5/1-g maddesi: Bulundurulması veya taşınmasına kanunen izin verilen silahları kolluğa teslim etmesi UYGULANMASINA,",
            'h': "6284 sayılı yasanın 5/1-h maddesi: Silah taşıması zorunlu olan bir kamu görevi ifa etse bile bu görevi nedeniyle zimmetinde bulunan silahı kurumuna teslim etmesi UYGULANMASINA,"
        }
        
        for harf, checkbox in mahkeme_maddeleri.items():
            if checkbox.isChecked():
                extended_maddeleri.append(madde_aciklamalari[harf])
        
        return extended_maddeleri
    
def create_emniyet_udf_content(xhavaletarih, xsayili, xolaytarihi, xeylemler, xemniyetmaddeleriharfler, 
                               xmahkememaddeleriharfler, xsupheli, xmagdur, xtedbirgunGUN, xmagdurbeyanı,
                               xmahkememaddelerigenişletilmiş):
    content = ""
    elements = []

    def add_text_with_formatting(text, bold_words=[], underline_words=[], alignment=3, space_above=1.0, left_indent=0.0, right_indent=0.0, first_line_indent=35.4375, line_spacing=0.0, space_below=1.0):
        nonlocal content
        start_offset = len(content)
        parts = []
        last_end = 0

        all_words = list(set(bold_words + underline_words))
        all_words.sort(key=lambda w: text.lower().find(w.lower()))

        for word in all_words:
            try:
                word_start = text.lower().index(word.lower(), last_end)
                word_end = word_start + len(word)

                if word_start > last_end:
                    parts.append(f'<content startOffset="{start_offset + last_end}" length="{word_start - last_end}" />')
                
                attributes = []
                if word in bold_words:
                    attributes.append('bold="true"')
                if word in underline_words:
                    attributes.append('underline="true"')
                
                parts.append(f'<content {" ".join(attributes)} startOffset="{start_offset + word_start}" length="{len(word)}" />')
                last_end = word_end
            except ValueError:
                print(f"Uyarı: '{word}' kelimesi metinde bulunamadı.")

        if last_end < len(text):
            parts.append(f'<content startOffset="{start_offset + last_end}" length="{len(text) - last_end}" />')

        # Paragraf sonuna boş karakter ekle
        text += " "
        parts.append(f'<content startOffset="{start_offset + len(text) - 1}" length="1" />')

        elements.append(f'<paragraph Alignment="{alignment}" SpaceAbove="{space_above}" LeftIndent="{left_indent}" RightIndent="{right_indent}" FirstLineIndent="{first_line_indent}" LineSpacing="{line_spacing}" SpaceBelow="{space_below}">{"".join(parts)}</paragraph>')
        content += text

    # Her madde için ayrı metin, bold kelimeler, altı çizili kelimeler ve hizalama özellikleri
    texts_and_formatting = [
        ("Kollluk amirince verilen geçici tedbir kararının onanması talep edilmiş olmakla;", [], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        ("GEREĞİ DÜŞÜNÜLDÜ:", ["GEREĞİ DÜŞÜNÜLDÜ:"], ["GEREĞİ DÜŞÜNÜLDÜ:"], 3, 1.0, 0.0, 0.0, 35.714287, 0.0, 1.0),
        (f"Sapanca İlçe Emniyet Müdürlüğünün {xhavaletarih} havale tarihli ve {xsayili} sayılı yazısı ile; {xolaytarihi} tarihinde meydana gelen {xeylemler} olayı ile ilgili olarak talep eden müraacaatı üzerine karşı taraf hakkında Sapanca İlçe Emniyet Müdürlüğünce gecikilmesinde sakınca bulunan hal kapsamında re'sen verilen tedbir kararının onanması talep edilmiştir.", [], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        (f"Tutanak ve ekleri incelendiğinde; Talep edenin Sapanca İlçe Emniyet Müdürlüğüne müraacaat ettiği, mağdurun müraacaatı üzerine kolluk amirince 6284. Sayılı yasanın 5/1-{xemniyetmaddeleriharfler} maddesine göre karşı taraf hakkında tedbir kararı verildiği anlaşılmıştır. {xmagdurbeyanı}", [], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        (f"Mahkememizce tüm dosya içeriğinin incelenmesi sonucu yapılan değerlendirmede 6284. Sayılı yasanın 5/1-{xmahkememaddeleriharfler} maddelerinin usul ve yasaya uygun ve de olay ile ölçülü olacağı değerlendirilerek aşağıdaki şekilde hüküm kurulmuştur.", [], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),

        ("HÜKÜM:Ayrıntısı yukarıda açıklandığı üzere:", ["HÜKÜM:Ayrıntısı yukarıda açıklandığı üzere:"], ["HÜKÜM:Ayrıntısı yukarıda açıklandığı üzere:"], 3, 1.0, 0.0, 0.0, 35.714287, 0.0, 1.0),
        
        ("1-Talebin KABULÜ ile,", ["1-Talebin KABULÜ ile,"], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        
        (f"2-Karşı taraf {xsupheli}'nin mağdur {xmagdur}'a karşı;", [f"2-Karşı taraf {xsupheli}'nin mağdur {xmagdur}'a karşı;"], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
    ]

    # Genişletilmiş tedbir maddelerini ekle
    for madde in xmahkememaddelerigenişletilmiş:
        bold_words = [madde.split(':')[0], "UYGULANMASINA,"]
        texts_and_formatting.append((madde, bold_words, [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0))

    # Diğer maddeleri ekle
    texts_and_formatting.extend([
        (f"3-Geçici tedbir kararının süresi {xtedbirgunGUN} olarak belirlenmek suretiyle ONANMASINA, (kararın şiddet uygulayan tarafından tebliği alındığı tarihten itibaren geçerli sayılmasına,)", [f"{xtedbirgunGUN}", "ONANMASINA, (kararın şiddet uygulayan tarafından tebliği alındığı tarihten itibaren geçerli sayılmasına,)"], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        
        (f"4-Tedbir kararının tebliğ işlemlerinde, tedbir kararına aykırılık hâlinde şiddet uygulayan hakkında 6284 sayılı yasanın 13/1 maddesi uyarınca 3 ila 10 gün arasında ZORLAMA HAPSİ UYGULANACAĞININ KARŞI TARAF {xsupheli}'e İHTARINA, (kararın tebliği ile ihtar edilmiş sayılmasına)", [f"ZORLAMA HAPSİ UYGULANACAĞININ KARŞI TARAF {xsupheli}'e İHTARINA, (kararın tebliği ile ihtar edilmiş sayılmasına)"], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        
        ("5-Kararın bir suretinin Sapanca İlamat ve İnfaz Bürosuna gönderilmesine,", [], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        
        ("6-Kararın kolluk marifeti ile taraflara tebliğine,", [], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        
        ("Dair, 6284 SY'nın 9. Maddesi gereğince kararın tebliğinden itibaren 2 HAFTA süre içerisinde EN YAKIN AİLE MAHKEMESİNE İTİRAZI kabil olmak üzere dosya üzerinde yapılan inceleme sonunda karar verildi.", ["2 HAFTA", "EN YAKIN AİLE MAHKEMESİNE İTİRAZI"], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0)
    ])

    # Her maddeyi ekle
    for text, bold_words, underline_words, *formatting in texts_and_formatting:
        add_text_with_formatting(text, bold_words, underline_words, *formatting)

    create_udf_file(content, elements, "emniyet_onama.udf")

def create_bireysel_udf_content(xbasvurutarihi, xmahkememaddeleriharfler, xsupheli, xmagdur, xtedbirgunGUN, xmagdurbeyanı,
                                xmahkememaddelerigenişletilmiş):
    content = ""
    elements = []

    def add_text_with_formatting(text, bold_words=[], underline_words=[], alignment=3, space_above=1.0, left_indent=0.0, right_indent=0.0, first_line_indent=35.4375, line_spacing=0.0, space_below=1.0):
        nonlocal content
        start_offset = len(content)
        parts = []
        last_end = 0

        all_words = list(set(bold_words + underline_words))
        all_words.sort(key=lambda w: text.lower().find(w.lower()))

        for word in all_words:
            try:
                word_start = text.lower().index(word.lower(), last_end)
                word_end = word_start + len(word)

                if word_start > last_end:
                    parts.append(f'<content startOffset="{start_offset + last_end}" length="{word_start - last_end}" />')
                
                attributes = []
                if word in bold_words:
                    attributes.append('bold="true"')
                if word in underline_words:
                    attributes.append('underline="true"')
                
                parts.append(f'<content {" ".join(attributes)} startOffset="{start_offset + word_start}" length="{len(word)}" />')
                last_end = word_end
            except ValueError:
                print(f"Uyarı: '{word}' kelimesi metinde bulunamadı.")

        if last_end < len(text):
            parts.append(f'<content startOffset="{start_offset + last_end}" length="{len(text) - last_end}" />')

        # Paragraf sonuna boş karakter ekle
        text += " "
        parts.append(f'<content startOffset="{start_offset + len(text) - 1}" length="1" />')

        elements.append(f'<paragraph Alignment="{alignment}" SpaceAbove="{space_above}" LeftIndent="{left_indent}" RightIndent="{right_indent}" FirstLineIndent="{first_line_indent}" LineSpacing="{line_spacing}" SpaceBelow="{space_below}">{"".join(parts)}</paragraph>')
        content += text

    # Her madde için ayrı metin, bold kelimeler, altı çizili kelimeler ve hizalama özellikleri
    texts_and_formatting = [
        (f"Tedbir isteyen {xmagdur} {xbasvurutarihi} tarihli dilekçesi ile lehine 6284 Sayılı Kanuna göre tedbir talepli evrakı gelmekle; kaydedildi, evrak kapsamı incelendi.", [], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        ("GEREĞİ DÜŞÜNÜLDÜ:", ["GEREĞİ DÜŞÜNÜLDÜ:"], ["GEREĞİ DÜŞÜNÜLDÜ:"], 3, 1.0, 0.0, 0.0, 35.714287, 0.0, 1.0),
        (f"Tedbir isteyen {xmagdur} {xbasvurutarihi} tarihli dilekçesi ile şiddet uygulayan hakkında, 6284 Sayılı Ailenin Korunması ve Kadına Karşı Şiddetin Önlenmesine Dair Kanun'un 5. Maddesinde yazılı tedbir veya tedbirlere karar verilmesini talep etmiştir.", [], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        ("Talep 6284 Sayılı Kanun uyarınca önleyici tedbir isteminden ibarettir.", [], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        ("6284 sayılı Kanunun 1. Maddesinde kanunun amacı şiddete uğrayan veya şiddete uğrama tehlikesi bulunan kadınların, çocukların. Aile bireylerinin ve tek taraflı ısrarlı takip mağduru olan kişilerin korunması ve bu kişilere yönelik şiddetin önlenmesi olarak belirlenmiştir.", [], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        ("Kanuna göre şiddet kişinin, fiziksel cinsel, psikolojik veya ekonomik açıdan zarar görmesiyle veya acı çekmesiyle sonuçlanan veya sonuçlanması muhtemel hareketleri, buna yönelik tehdit ve baskıyı ya da özgürlüğün keyfi engellenmesini de içeren, toplumsal, kamusal veya özel alanda meydana gelen fiziksel, cinsel, psikolojik, sözlü veya ekonomik her türlü tutum ve davranış olarak tanımlanmaştır.", [], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        (f"{xmagdurbeyanı}", [], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        (f'6284 sayılı yasanın 8/3 maddesine göre" Koruyucu tedbir kararı verilebilmesi için şiddetin uygulandığı hususunda delil veya belge aranmaz. Önleyici tedbir kararı, geciktirilmeksizin verilir. Bu kararın verilmesi, bu Kanun amacını gerçekleştirmeyi tehlikeye sokabilecek şekilde geciktirilemez. " hükmü gözetilerek, 6284 Sayılı Yasanın 5/1-{xmahkememaddeleriharfler} maddeleri uyarınca karşı taraf hakkında önleyici tedbir uygulanmasına karar vermek gerektiği sonucuna ulaşılmıştır.', [], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        ("HÜKÜM:Ayrıntısı yukarıda açıklandığı üzere:", ["HÜKÜM:Ayrıntısı yukarıda açıklandığı üzere:"], ["HÜKÜM:Ayrıntısı yukarıda açıklandığı üzere:"], 3, 1.0, 0.0, 0.0, 35.714287, 0.0, 1.0),
        ("1-Talebin KABULÜ ile,", ["1-Talebin KABULÜ ile,"], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        (f"2-Karşı taraf {xsupheli}'nin mağdur {xmagdur}'a karşı;", [f"2-Karşı taraf {xsupheli}'nin mağdur {xmagdur}'a karşı;"], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
    ]

    # Genişletilmiş tedbir maddelerini ekle
    for madde in xmahkememaddelerigenişletilmiş:
        bold_words = [madde.split(':')[0], "UYGULANMASINA,"]
        texts_and_formatting.append((madde, bold_words, [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0))

    # Diğer maddeleri ekle
    texts_and_formatting.extend([
        (f"3-Geçici tedbir kararının süresi {xtedbirgunGUN} olarak belirlenmesine,", [f"{xtedbirgunGUN}"], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        (f"4-Tedbir kararının tebliğ işlemlerinde, tedbir kararına aykırılık hâlinde şiddet uygulayan hakkında 6284 sayılı yasanın 13/1 maddesi uyarınca 3 ila 10 gün arasında ZORLAMA HAPSİ UYGULANACAĞININ KARŞI TARAF {xsupheli}'e İHTARINA, (kararın tebliği ile ihtar edilmiş sayılmasına)", [f"ZORLAMA HAPSİ UYGULANACAĞININ KARŞI TARAF {xsupheli}'e İHTARINA, (kararın tebliği ile ihtar edilmiş sayılmasına)"], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        ("5-Kararın bir suretinin Sapanca İlamat ve İnfaz Bürosuna gönderilmesine,", [], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        ("6-Kararın kolluk marifeti ile taraflara tebliğine,", [], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        ("Dair, 6284 SY'nın 9. Maddesi gereğince kararın tebliğinden itibaren 2 HAFTA süre içerisinde EN YAKIN AİLE MAHKEMESİNE İTİRAZI kabil olmak üzere dosya üzerinde yapılan inceleme sonunda karar verildi.", ["2 HAFTA", "EN YAKIN AİLE MAHKEMESİNE İTİRAZI"], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0)
    ])

    # Her maddeyi ekle
    for text, bold_words, underline_words, *formatting in texts_and_formatting:
        add_text_with_formatting(text, bold_words, underline_words, *formatting)

    create_udf_file(content, elements, "bireysel_talep.udf")

def create_kisisel_esya_udf_content(xtarihli, xadres, xmagdur, xesyalar):
    content = ""
    elements = []

    def add_text_with_formatting(text, bold_words=[], underline_words=[], alignment=3, space_above=1.0, left_indent=0.0, right_indent=0.0, first_line_indent=35.4375, line_spacing=0.0, space_below=1.0):
        nonlocal content
        start_offset = len(content)
        parts = []
        last_end = 0

        all_words = list(set(bold_words + underline_words))
        all_words.sort(key=lambda w: text.lower().find(w.lower()))

        for word in all_words:
            try:
                word_start = text.lower().index(word.lower(), last_end)
                word_end = word_start + len(word)

                if word_start > last_end:
                    parts.append(f'<content startOffset="{start_offset + last_end}" length="{word_start - last_end}" />')
                
                attributes = []
                if word in bold_words:
                    attributes.append('bold="true"')
                if word in underline_words:
                    attributes.append('underline="true"')
                
                parts.append(f'<content {" ".join(attributes)} startOffset="{start_offset + word_start}" length="{len(word)}" />')
                last_end = word_end
            except ValueError:
                print(f"Uyarı: '{word}' kelimesi metinde bulunamadı.")

        if last_end < len(text):
            parts.append(f'<content startOffset="{start_offset + last_end}" length="{len(text) - last_end}" />')

        # Paragraf sonuna boş karakter ekle
        text += " "
        parts.append(f'<content startOffset="{start_offset + len(text) - 1}" length="1" />')

        elements.append(f'<paragraph Alignment="{alignment}" SpaceAbove="{space_above}" LeftIndent="{left_indent}" RightIndent="{right_indent}" FirstLineIndent="{first_line_indent}" LineSpacing="{line_spacing}" SpaceBelow="{space_below}">{"".join(parts)}</paragraph>')
        content += text

    # Her madde için ayrı metin, bold kelimeler, altı çizili kelimeler ve hizalama özellikleri
    texts_and_formatting = [
        (f"Tedbir talep eden {xtarihli} dilekçesi ile kişisel eşyalarının kolluk nezaretinde teslim almak istediğini bildirir dilekçesini mahkememize sunmuştur.", ["Tedbir talep eden", "dilekçesi ile kişisel eşyalarının  kolluk nezaretinde teslim almak istediğini bildirir dilekçesini mahkememize sunmuştur."], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        ("GEREĞİ DÜŞÜNÜLDÜ:", ["GEREĞİ DÜŞÜNÜLDÜ:"], ["GEREĞİ DÜŞÜNÜLDÜ:"], 3, 1.0, 0.0, 0.0, 35.714287, 0.0, 1.0),
        (f"Tedbir isteyen can güvenliğinden endişe duyması nedeniyle, {xadres} adreste bulunan evdeki eşyalarının kolluk nezaretinde teslim almak istediğini talep etmiştir.", [], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        (f"Talep incelendiğinde; Talep edenin usul ve yasaya uygun ve de olay ile ölçülü olduğu anlaşıldığından talebin kabulü ile karşı taraf hakkında 6284 Sayılı Yasanın 8/7 maddesi ve Uygulama Yönetmeliğinin ilgili maddeleri uyarınca, korunan kişinin kişisel eşya ve belgelerinin {xadres} adresinde bulunan kolluk marifetiyle teslimi önleyici tedbir uygulanmasına karar vermek gerektiği sonucuna ulaşılmıştır.", [], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        ("KARAR:Yukarıda gerekçesi açıklandığı üzere;", ["KARAR:Yukarıda gerekçesi açıklandığı üzere;"], ["KARAR:Yukarıda gerekçesi açıklandığı üzere;"], 3, 1.0, 0.0, 0.0, 35.714287, 0.0, 1.0),
        ("1-Talebin KABULÜNE,", ["1-Talebin KABULÜNE,"], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        (f"2-6284 sayılı yasanın 8/7. Maddesi gereğince; talep eden {xmagdur}'a ait {xadres} adresindeki ilk bakışta kendisine ait olduğu anlaşılan kişisel eşyalarının ({xesyalar}) kolluk marifetiyle teslimine,", [], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        ("3-Kararın kolluk marifeti ile taraflara tebliğine, tedbir kararının tebliğ veya tefhim edilmemesinin kararın uygulanmasına engel oluşturmayacağının bildirilmesine,", [], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        ("4-Kararın bir suretinin Sapanca İlamat ve İnfaz Bürosuna gönderilmesine,", [], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        ("5-İş bu ara kararın vekillere tebliğine,", [], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        ("6-6284 Sayılı yasanın 20/(1) maddesi uyarınca harç alınmasına yer olmadığına,", [], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0),
        ("Dair, hükmün infazına engel olmamak koşuluyla ilgilinin tebliğinden itibaren 2 HAFTA süre içerisinde EN YAKIN AİLE MAHKEMESİNE İTİRAZI kabil olmak üzere dosya üzerinde yapılan inceleme sonunda karar verildi.", ["2 HAFTA", "EN YAKIN AİLE MAHKEMESİNE İTİRAZI"], [], 3, 1.0, 0.0, 0.0, 35.4375, 0.0, 1.0)
    ]

    # Her maddeyi ekle
    for text, bold_words, underline_words, *formatting in texts_and_formatting:
        add_text_with_formatting(text, bold_words, underline_words, *formatting)

    create_udf_file(content, elements, "kisisel_esya_teslimi.udf")

def create_zorlama_hapsi_udf_content(xtarih, xsayi, xemniyet, xkarartarih, xmualefettarihi, xmualifolankisi,
                                     xkarartebligtarihi, xsavcilikyazitarihi, xsavcilikesası, xmualifolankisiTcno,
                                     xhapisgünü, xihlaledilentedbir, karar_tipi):
    content = ""
    elements = []

    def add_text_with_formatting(text, bold_words=[], underline_words=[], alignment=3, space_above=1.0, left_indent=0.0, right_indent=0.0, first_line_indent=35.4375, line_spacing=0.0, space_below=1.0):
        nonlocal content
        start_offset = len(content)
        parts = []
        last_end = 0

        all_words = list(set(bold_words + underline_words))
        all_words.sort(key=lambda w: text.lower().find(w.lower()))

        for word in all_words:
            try:
                word_start = text.lower().index(word.lower(), last_end)
                word_end = word_start + len(word)

                if word_start > last_end:
                    parts.append(f'<content startOffset="{start_offset + last_end}" length="{word_start - last_end}" />')
                
                attributes = []
                if word in bold_words:
                    attributes.append('bold="true"')
                if word in underline_words:
                    attributes.append('underline="true"')
                
                parts.append(f'<content {" ".join(attributes)} startOffset="{start_offset + word_start}" length="{len(word)}" />')
                last_end = word_end
            except ValueError:
                print(f"Uyarı: '{word}' kelimesi metinde bulunamadı.")

        if last_end < len(text):
            parts.append(f'<content startOffset="{start_offset + last_end}" length="{len(text) - last_end}" />')

        # Paragraf sonuna boş karakter ekle
        text += " "
        parts.append(f'<content startOffset="{start_offset + len(text) - 1}" length="1" />')

        elements.append(f'<paragraph Alignment="{alignment}" SpaceAbove="{space_above}" LeftIndent="{left_indent}" RightIndent="{right_indent}" FirstLineIndent="{first_line_indent}" LineSpacing="{line_spacing}" SpaceBelow="{space_below}">{"".join(parts)}</paragraph>')
        content += text

    # Duruşma Şablonu
    add_text_with_formatting(f"DURUŞMA ŞABLONU {karar_tipi}", ["DURUŞMA ŞABLONU", karar_tipi], ["DURUŞMA ŞABLONU", karar_tipi])
    
    # DURUŞMA ŞABLONU'ndan sonra 3 boş satır ekle
    for _ in range(3):
        add_text_with_formatting(" ", [], [], 3, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0)

    add_text_with_formatting(f"{xemniyet} Emniyet Müdürlüğünün {xtarih} tarih {xsayi} sayılı yazısı ile mahkememizin {xkarartarih} tarihli kararına {xmualefettarihi} tarihinde karşı taraf {xmualifolankisi} muhalefetinden bahisle ihlal talepli yazısı ve ekleri okundu dosyasına konuldu.")
    add_text_with_formatting(f"Mahkememiz önleyici tedbir kararının {xkarartarih} tarihinde verildiği Sapanca Cumhuriyet Başsavcılığı İlamat ve İnfaz Bürosunun {xsavcilikyazitarihi} tarih ve {xsavcilikesası} tedbir sayılı yazıları ile karşı taraf {xmualifolankisi} {xkarartebligtarihi} tarihinde tebliğ edildiği anlaşıldı.")
    add_text_with_formatting(f"Karşı taraf {xmualifolankisi} soruldu;  , dedi beyanı okundu imzası alındı.")
    add_text_with_formatting(f"                                                                                                       {xmualifolankisi}")

    add_text_with_formatting(" ")
    add_text_with_formatting("Dosya incelendi. Araştırılacak başkaca husus kalmadığından açık yargılamaya son verildi.")
    add_text_with_formatting("G.D: Gerekçesi ileride açıklanacağı üzere:", ["G.D: Gerekçesi ileride açıklanacağı üzere:"])

    if karar_tipi == "RET":
        add_text_with_formatting(f"1-Karşı taraf {xmualifolankisi} 6284 sayılı yasa kapsamında tedbiri ihlal etmediği kanaati oluştuğundan talebinin REDDİNE,", ["REDDİNE,"])
    else:
        add_text_with_formatting(f"1-Aleyhine tedbir kararı verilen {xmualifolankisiTcno} T.C. Kimlik numaralı {xmualifolankisi} 6284 sayılı yasanın 13/1 maddesi gereğince takdiren {xhapisgünü} GÜN SÜRE İLE ZORLAMA HAPSİNE TABİ TUTULMASINA,", [f"{xhapisgünü} GÜN SÜRE İLE ZORLAMA HAPSİNE TABİ TUTULMASINA,"])

    add_text_with_formatting("2-Sair hususların gerekçeli kararda yazılmasına,")
    add_text_with_formatting("Dair, karşı tarafın yüzüne karşı, mağdurun yokluğunda, 6284 SY'nın 9. Maddesi gereğince kararın tebliğinden itibaren 2 HAFTA süre içerisinde EN YAKIN AİLE MAHKEMESİNE İTİRAZI kabil olmak üzere dosya üzerinde yapılan inceleme sonunda karar verildi.", ["2 HAFTA", "EN YAKIN AİLE MAHKEMESİNE İTİRAZI"])
    # KARAR ŞABLONU öncesinde 3 boş satır ekle
    for _ in range(3):
        add_text_with_formatting(" ", [], [], 3, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0)

    # Karar Şablonu
    add_text_with_formatting("KARAR ŞABLONU", ["KARAR ŞABLONU"], ["KARAR ŞABLONU"])
    
    # KARAR ŞABLONU'ndan sonra 3 boş satır ekle
    for _ in range(3):
        add_text_with_formatting(" ", [], [], 3, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0)

    add_text_with_formatting(f"{xemniyet} Emniyet Müdürlüğünün {xtarih} tarih {xsayi} sayılı yazısı tedbir ihlali sayılı yazısı incelendi.")
    add_text_with_formatting("GEREĞİ DÜŞÜNÜLDÜ:", ["GEREĞİ DÜŞÜNÜLDÜ:"], ["GEREĞİ DÜŞÜNÜLDÜ:"])
    add_text_with_formatting(f"{xemniyet} Emniyet Müdürlüğünün {xtarih} tarih {xsayi} sayılı yazısı yazısı ile; mahkememizce verilen {xkarartarih} tarihli kararı ile karşı taraf {xmualifolankisi} hakkında tedbir kararı verildiği, {xemniyet} Müdürlüğünün {xtarih} tarihli ve {xsayi} sayılı yazısı ile; {xmualifolankisi} tedbir kararını ihlal ettiği anlaşılmış olup zorlama hapsine tabi tutulmasını talep etmiştir.")

    if karar_tipi == "RET":
        add_text_with_formatting(f"İncelenen evrak kapsamı itibariyle; Karşı taraf {xmualifolankisi} 6284 sayılı yasa kapsamındatedbiri ihlal etmediği kanaati oluştuğundan talebinin reddine karar vermek gerekmiştir.")
    else:
        add_text_with_formatting(f"İncelenen evrak kapsamı itibariyle; {xihlaledilentedbir} ihlal ettiği değerlendirilmekle {xmualifolankisi} hakkında zorlama hapsi verilmesine dair karar verilerek aşağıdaki şekilde hüküm kurulmuştur.")

    add_text_with_formatting("Dosya incelendi. Araştırılacak başkaca husus kalmadığından açık yargılamaya son verildi.")
    add_text_with_formatting("HÜKÜM:Ayrıntısı yukarıda açıklandığı üzere:", ["HÜKÜM:Ayrıntısı yukarıda açıklandığı üzere:"], ["HÜKÜM:Ayrıntısı yukarıda açıklandığı üzere:"])

    if karar_tipi == "RET":
        add_text_with_formatting(f"1-Karşı taraf {xmualifolankisi}'in 6284 sayılı yasa kapsamında tedbiri ihlal etmediği kanaati oluştuğundan talebinin REDDİNE,", ["REDDİNE,"])
    else:
        add_text_with_formatting(f"1-Aleyhine tedbir kararı verilen {xmualifolankisiTcno} T.C. Kimlik numaralı {xmualifolankisi} 6284 sayılı yasanın 13/1 maddesi gereğince takdiren {xhapisgünü} GÜN SÜRE İLE ZORLAMA HAPSİNE TABİ TUTULMASINA,", [f"{xhapisgünü} GÜN SÜRE İLE ZORLAMA HAPSİNE TABİ TUTULMASINA,"])
    add_text_with_formatting("2-Kararın bir örneğinin karşı tarafa tebliğine,")
    add_text_with_formatting("3-Karar kesinleştiğinde infazı için Sapanca Cumhuriyet Başsavcılığına gönderilmesine,")
    add_text_with_formatting("Dair, karşı tarafın yüzüne karşı, mağdurun yokluğunda, 6284 SY'nın 9. Maddesi gereğince kararın tebliğinden itibaren 2 HAFTA süre içerisinde EN YAKIN AİLE MAHKEMESİNE İTİRAZI kabil olmak üzere dosya üzerinde yapılan inceleme sonunda karar verildi.", ["2 HAFTA", "EN YAKIN AİLE MAHKEMESİNE İTİRAZI"])

    create_udf_file(content, elements, "zorlama_hapsi.udf")

def create_ihlal_tensibi_udf_content(xsavcilikadi, xsavcilikesas, xmahkemeesasno, xmahkemekararno,
                                     xmahkemekarartarihi, xkararihlaltarihi, xkararıihlaledenkisi):
    content = ""
    elements = []

    def add_text_with_formatting(text, bold_words=[], underline_words=[], alignment=3, space_above=1.0, left_indent=0.0, right_indent=0.0, first_line_indent=35.4375, line_spacing=0.0, space_below=1.0):
        nonlocal content
        start_offset = len(content)
        parts = []
        last_end = 0

        all_words = list(set(bold_words + underline_words))
        all_words.sort(key=lambda w: text.lower().find(w.lower()))

        for word in all_words:
            try:
                word_start = text.lower().index(word.lower(), last_end)
                word_end = word_start + len(word)

                if word_start > last_end:
                    parts.append(f'<content startOffset="{start_offset + last_end}" length="{word_start - last_end}" />')
                
                attributes = []
                if word in bold_words:
                    attributes.append('bold="true"')
                if word in underline_words:
                    attributes.append('underline="true"')
                
                parts.append(f'<content {" ".join(attributes)} startOffset="{start_offset + word_start}" length="{len(word)}" />')
                last_end = word_end
            except ValueError:
                print(f"Uyarı: '{word}' kelimesi metinde bulunamadı.")

        if last_end < len(text):
            parts.append(f'<content startOffset="{start_offset + last_end}" length="{len(text) - last_end}" />')

        # Paragraf sonuna boş karakter ekle
        text += " "
        parts.append(f'<content startOffset="{start_offset + len(text) - 1}" length="1" />')

        elements.append(f'<paragraph Alignment="{alignment}" SpaceAbove="{space_above}" LeftIndent="{left_indent}" RightIndent="{right_indent}" FirstLineIndent="{first_line_indent}" LineSpacing="{line_spacing}" SpaceBelow="{space_below}">{"".join(parts)}</paragraph>')
        content += text

    # Şablonu ekle
    add_text_with_formatting(f"Mahkememize tevzi edilen dava dilekçesi mahkememiz esasının yukarıda belirtilen sırasına kaydı yapıldı. {xsavcilikadi} Cumhuriyet Başsavcılığının {xsavcilikesas} sayılı yazısı ile Mahkememizin {xmahkemeesasno}Esas {xmahkemekararno}D.iş, {xmahkemekarartarihi} tarihli kararınına {xkararihlaltarihi} tarihinde karşı taraf {xkararıihlaledenkisi} muhalefeti bahsiyle;")
    add_text_with_formatting("Dosya incelendi.")
    add_text_with_formatting("GEREĞİ DÜŞÜNÜLDÜ:", ["GEREĞİ DÜŞÜNÜLDÜ:"], ["GEREĞİ DÜŞÜNÜLDÜ:"])
    add_text_with_formatting(f"1-Karşı taraf {xkararıihlaledenkisi}'nın beyanının tespiti ve duruşmada hazır edilmesi için kolluk birimine müzekkere yazılmasına,")

    create_udf_file(content, elements, "ihlal_tensibi.udf")

def create_udf_file(content, elements, file_name):
    # UDF template yapısı
    udf_template = f'''<?xml version="1.0" encoding="UTF-8" ?>
<template format_id="1.8">
<content><![CDATA[{content}]]></content>
<properties>
    <pageFormat mediaSizeName="1" leftMargin="42.525000000000006" rightMargin="42.525000000000006" topMargin="42.525000000000006" bottomMargin="42.52500000000006" paperOrientation="1" headerFOffset="20.0" footerFOffset="20.0" />
</properties>
<elements resolver="hvl-default">
    {''.join(elements)}
</elements>
<styles>
    <style name="default" description="Geçerli" family="Times New Roman" size="12" bold="false" italic="false" />
    <style name="hvl-default" family="Times New Roman" size="12" description="Gövde" />
</styles>
</template>'''

    # Geçici klasörde dosya oluştur
    temp_dir = tempfile.gettempdir()
    content_xml_path = os.path.join(temp_dir, 'content.xml')
    udf_file_path = os.path.join(temp_dir, file_name)

    with open(content_xml_path, 'w', encoding='utf-8') as file:
        file.write(udf_template)

    # content.xml'i udf zip dosyası olarak kaydet
    with zipfile.ZipFile(udf_file_path, 'w') as zipf:
        zipf.write(content_xml_path, 'content.xml')

    # content.xml dosyasını sil
    os.remove(content_xml_path)

    print(f"UDF dosyası oluşturuldu: {udf_file_path}")
    
    open_udf_file(udf_file_path)

def open_udf_file(file_path):
    if sys.platform.startswith('darwin'):  # macOS
        os.system(f'open "{file_path}"')
    elif sys.platform.startswith('win'):   # Windows
        os.startfile(file_path)
    else:  # Linux ve diğer platformlar
        os.system(f'xdg-open "{file_path}"')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = UDFGeneratorGUI()
    ex.show()
    sys.exit(app.exec())
    app = QApplication(sys.argv)
    ex = UDFGeneratorGUI()
    ex.show()
    sys.exit(app.exec())