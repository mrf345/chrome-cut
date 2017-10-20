from sys import exit, argv
from os import name
from time import sleep
from PySide.QtGui import QWidget, QApplication, QIcon, QLineEdit
from PySide.QtGui import QFont, QToolTip, QPushButton, QMessageBox
from PySide.QtGui import QInputDialog, QListWidget, QStatusBar
from PySide.QtGui import QDesktopWidget, QPixmap, QCheckBox
from PySide.QtGui import QVBoxLayout, QHBoxLayout, QMainWindow
from PySide.QtCore import QCoreApplication, Qt, QThread, QSize, Signal, Slot
from .ex_functions import r_path
from functools import partial
from .core import get_ips, det_ccast, cancel_app, reset_cc, send_app


class CC_thread(QThread):
    somesignal = Signal(object)

    def speak_me(self):
        self.speak.emit()

    def __init__(self, todo=None, dur=None, ip=None, vidl=None):
        QThread.__init__(self)
        self.todo = todo
        self.dur = dur
        self.ip = ip
        self.vidl = vidl
        self.outp = None
        self.abo = None

    def run(self):
        counter = 0
        while self.abo is None:
            counter += 1
            self.somesignal.emit('%% looping ' + str(counter) + ' time ..')
            sleep(self.dur / 2)
            if self.vidl is None:
                ss = self.todo(self.ip)
            else:
                ss = self.todo(self.ip, ylink=self.vidl)
            if ss is None:
                self.somesignal.emit(
                    '%% chrome cast not found, waiting for it')
            else:
                self.somesignal.emit('%% chrome cast found and dealt with')
            sleep(self.dur / 2)
        self.somesignal.emit('# loop has been terminated')
        return True

    def stop(self):
        self.abo = 2
        return True


class CC_window(QWidget):
    def __init__(self):
        super(CC_window, self).__init__()
        glo = QVBoxLayout(self)
        self.Runningo = None
        self.Looping = None
        self.P = CC_thread()
        if name == 'nt':
            ficon = r_path('images\\favicon.png')
            licon = r_path('images\\logo.png')
        else:
            ficon = r_path('images/favicon.png')
            licon = r_path('images/logo.png')
        self.tf = QFont("", 13, QFont.Bold)
        self.sf = QFont("", 10, QFont.Bold)
        self.SelfIinit(QIcon(ficon))
        self.center()
        self.a_btn(licon, glo)
        self.ss_btns(glo)
        self.i_list(glo)
        self.cl_btn(glo)
        self.l_btns(glo)
        self.f_btns(glo)
        self.ds_bar(glo)
        self.setLayout(glo)
        self.activateWindow()
        self.show()

    def SelfIinit(self, icon):
        self.setWindowTitle('chrome-cut 0.1')
        self.setGeometry(300, 300, 200, 150)
        self.setMinimumWidth(600)
        self.setMaximumWidth(600)
        self.setMinimumHeight(500)
        self.setMaximumHeight(500)
        # Setting Icon
        self.setWindowIcon(icon)
        QToolTip.setFont(self.sf)

    def msgApp(self, title, msg):
        uinfo = QMessageBox.question(self, title,
                                     msg, QMessageBox.Yes | QMessageBox.No)
        if uinfo == QMessageBox.Yes:
            return 'y'
        if uinfo == QMessageBox.No:
            return 'n'

    def closeEvent(self, event=None):
        if self.P.isRunning():
            response = self.msgApp(
                "Making sure",
                "Sure, you want to exit while looping ?")
            if response == 'y':
                if event is not None:
                    event.accept()
                self.P.stop()
                exit(0)
            else:
                if event is not None:
                    event.ignore()
        else:
            if event is not None:
                event.accept()
            exit(0)

    def center(self):
        qrect = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qrect.moveCenter(cp)
        self.move(qrect.topLeft())

    def a_btn(self, icon, glo):
        def show_about():
            Amsg = "<center>All credit reserved to the author of chrome-cut "
            Amsg += " version 0.1"
            Amsg += ", This work is a free, open-source project licensed "
            Amsg += " under Mozilla Public License version 2.0 . <br><br>"
            Amsg += " visit us for more infos and how-tos :<br> "
            Amsg += "<b><a href='https://chrom-cut.github.io/'> "
            Amsg += "https://chrome-cut.github.io/ </a> </b></center>"
            Amsgb = "About chrome-cut"
            return QMessageBox.about(
                self,
                Amsgb,
                Amsg)
        self.abutton = QPushButton('', self)
        self.abutton.setIcon(QPixmap(icon))
        self.abutton.setIconSize(QSize(500, 100))
        self.abutton.setToolTip('About chrome-cut')
        self.abutton.clicked.connect(show_about)
        glo.addWidget(self.abutton)

    def ss_btns(self, glo):
        self.lebutton = QPushButton('Scan IP address', self)
        self.lebutton.setToolTip(
            'Insert and check if a specific IP is a valid chrome cast')
        self.lebutton.setFont(self.tf)
        self.lebutton.clicked.connect(self.sip_input)
        glo.addWidget(self.lebutton)

    def sip_input(self):
        self.lebutton.setEnabled(False)
        self.s_bar.setStyleSheet(self.s_norm)
        self.s_bar.showMessage('> Checking out the IP ..')
        msg = "<center>Enter suspected IP to check : <br><i><u>Usually it is "
        msg += "on 192.168.what_have_you.188</i></center>"
        text, okPressed = QInputDialog.getText(self,
                                               "Scan IP",
                                               msg)
        if okPressed and text != '':
            self.setCursor(Qt.BusyCursor)
            ch = det_ccast(text)
            if ch[0]:
                self.il_add([ch[1]])
                self.unsetCursor()
                self.lebutton.setEnabled(True)
                return True
            else:
                self.s_bar.setStyleSheet(self.s_error)
                self.s_bar.showMessage(
                    '! Error: inserted IP is not chrome cast device')
                self.unsetCursor()
                self.lebutton.setEnabled(True)
                return True
        self.s_bar.clearMessage()
        self.lebutton.setEnabled(True)
        return True

    def i_list(self, glo):
        self.ci_list = QListWidget()
        self.ci_list.setToolTip("List of discovered devices")
        self.ci_list.setEnabled(False)
        self.setFont(self.sf)
        glo.addWidget(self.ci_list)

    def cl_btn(self, glo):
        self.cle_btn = QPushButton('Clear devices list')
        self.cle_btn.setToolTip("Remove all devices from the list")
        self.cle_btn.setFont(self.sf)
        self.cle_btn.setEnabled(False)
        self.cle_btn.clicked.connect(self.il_add)
        glo.addWidget(self.cle_btn)

    def l_btns(self, glo):
        hlayout = QHBoxLayout()
        self.llo = QCheckBox("Looping")
        self.llo.setToolTip(
            'Automate repeating the smae command on the smae device selected ')
        self.llo.setEnabled(False)
        self.nlo = QLineEdit()
        self.nlo.setPlaceholderText("duration in seconds. Default is 10")
        self.nlo.setEnabled(False)
        self.nlo.setToolTip(
            "Duration of sleep after each loop")
        self.lbtn = QPushButton('Stop')
        self.lbtn.setEnabled(False)
        self.lbtn.setFont(self.tf)
        self.llo.setFont(self.sf)
        self.lbtn.setToolTip("stop on-going command or loop")
        self.llo.toggled.connect(self.loped)
        self.lbtn.clicked.connect(partial(self.inloop_state, out=True))
        hlayout.addWidget(self.llo)
        hlayout.addWidget(self.nlo)
        hlayout.addWidget(self.lbtn)
        glo.addLayout(hlayout)

    def loped(self):
        if self.Looping:
            self.Looping = None
            self.llo.setChecked(False)
            self.nlo.setEnabled(False)
        else:
            self.Looping = True
            self.llo.setChecked(True)
            self.nlo.setEnabled(True)
        return True

    def f_btns(self, glo):
        hlayout = QHBoxLayout()
        self.ksbutton = QPushButton('Kill stream', self)
        self.ksbutton.setToolTip(
            'Kill whetever been streamed')
        self.ksbutton.setFont(self.tf)
        self.ksbutton.clicked.connect(self.k_act)
        self.sbutton = QPushButton('Stream', self)
        self.sbutton.setFont(self.tf)
        self.sbutton.setToolTip('Stream a youtube video')
        self.fbutton = QPushButton('Factory reset', self)
        self.fbutton.setFont(self.tf)
        self.fbutton.setToolTip('Factory reset the device')
        self.fbutton.clicked.connect(self.fr_act)
        self.sbutton.clicked.connect(self.yv_input)
        self.ksbutton.setEnabled(False)
        self.sbutton.setEnabled(False)
        self.fbutton.setEnabled(False)
        hlayout.addWidget(self.ksbutton)
        hlayout.addWidget(self.sbutton)
        hlayout.addWidget(self.fbutton)
        glo.addLayout(hlayout)

    def k_act(self):
        if self.ci_list.count() >= 1:
            cr = self.ci_list.currentRow()
            if cr is None or cr <= 0:
                cr = 0
            ip = self.ci_list.item(cr).text()
            if self.Looping is not None:
                dur = self.nlo.text()
                if len(dur) >= 1:
                    try:
                        dur = int(dur)
                    except:
                        self.s_bar.setStyleSheet(self.s_error)
                        self.s_bar.showMessage(
                            '! Error: wrong duration entery, only integers')
                        return True
                else:
                    dur = 10
                self.P = CC_thread(cancel_app, dur, ip)
                self.P.start()
                self.P.somesignal.connect(self.handleStatusMessage)
                self.P.setTerminationEnabled(True)
                self.inloop_state()
                return True
            else:
                ch = cancel_app(ip)
                if ch is None:
                    self.s_bar.setStyleSheet(self.s_error)
                    self.s_bar.showMessage(
                        '! Error: failed to kill stream ..')
                else:
                    self.s_bar.setStyleSheet(self.s_norm)
                    self.s_bar.showMessage(
                        '# Stream got killed ')
        else:
            self.s_bar.setStyleSheet(self.s_error)
            self.s_bar.showMessage(
                '! Error: No items selected from the list')
            self.eout()
        return True

    def fr_act(self):
        if self.ci_list.count() >= 1:
            cr = self.ci_list.currentRow()
            if cr is None or cr <= 0:
                cr = 0
            ip = self.ci_list.item(cr).text()
            if self.Looping is not None:
                dur = self.nlo.text()
                if len(dur) >= 1:
                    try:
                        dur = int(dur)
                    except:
                        self.s_bar.setStyleSheet(self.s_error)
                        self.s_bar.showMessage(
                            '! Error: wrong duration entery, only integers')
                        return True
                else:
                    dur = 10
                self.P = CC_thread(reset_cc, dur, ip)
                self.P.start()
                self.P.somesignal.connect(self.handleStatusMessage)
                self.P.setTerminationEnabled(True)
                self.inloop_state()
                return True
            else:
                ch = reset_cc(ip)
                if ch is None:
                    self.s_bar.setStyleSheet(self.s_error)
                    self.s_bar.showMessage(
                        '! Error: failed to factory reset ..')
                else:
                    self.s_bar.setStyleSheet(self.s_norm)
                    self.s_bar.showMessage(
                        '# Got factory reseted ')
        else:
            self.s_bar.setStyleSheet(self.s_error)
            self.s_bar.showMessage(
                '! Error: No items selected from the list')
            self.eout()
        return True

    def y_act(self, link=None):
        if self.ci_list.count() >= 1:
            cr = self.ci_list.currentRow()
            if cr is None or cr <= 0:
                cr = 0
            ip = self.ci_list.item(cr).text()
            if self.Looping is not None:
                dur = self.nlo.text()
                if len(dur) >= 1:
                    try:
                        dur = int(dur)
                    except:
                        self.s_bar.setStyleSheet(self.s_error)
                        self.s_bar.showMessage(
                            '! Error: wrong duration entery, only integers')
                        return True
                else:
                    dur = 10
                self.P = CC_thread(send_app, dur, ip, link)
                self.P.start()
                self.P.somesignal.connect(self.handleStatusMessage)
                self.P.setTerminationEnabled(True)
                self.inloop_state()
                return True
            else:
                ch = reset_cc(ip)
                if ch is None:
                    self.s_bar.setStyleSheet(self.s_error)
                    self.s_bar.showMessage(
                        '! Error: failed to stream link ..')
                else:
                    self.s_bar.setStyleSheet(self.s_norm)
                    self.s_bar.showMessage(
                        '# Streamed the link ')
        else:
            self.s_bar.setStyleSheet(self.s_error)
            self.s_bar.showMessage(
                '! Error: No items selected from the list')
            self.eout()
        return True

    def yv_input(self):
        text, okPressed = QInputDialog.getText(
            self,
            "Stream youtube",
            "Enter youtube video link to be streamed :")
        if okPressed and text != '':
            ntext = text.split('?')
            if len(ntext) <= 1:
                self.s_bar.setStyleSheet(self.s_error)
                self.s_bar.showMessage(
                    '! Error: Invalid youtube linkd ')
                return False
            ntext = ntext[1]
            if ntext != '' and len(ntext) > 1 and "youtube" in text:
                self.y_act(ntext)
                return True
            else:
                self.s_bar.setStyleSheet(self.s_error)
                self.s_bar.showMessage(
                    '! Error: Invalid youtube linkd ')
        return False

    @Slot(object)
    def handleStatusMessage(self, message):
        self.s_bar.setStyleSheet(self.s_loop)
        self.s_bar.showMessage(message)

    def il_add(self, items=[]):
        if len(items) >= 1:
            self.s_bar.setStyleSheet(self.s_norm)
            for i in items:
                fitem = self.ci_list.findItems(i,
                                               Qt.MatchExactly)
                if len(fitem) >= 1:
                    self.s_bar.setStyleSheet(self.s_error)
                    self.s_bar.showMessage(
                        '! Error: Device exists in the list')
                else:
                    self.s_bar.setStyleSheet(self.s_norm)
                    self.ci_list.addItem(i)
                    self.s_bar.showMessage('# Device was found and added')
            if not self.P.isRunning():
                self.cle_btn.setEnabled(True)
                self.ci_list.setEnabled(True)
                self.llo.setEnabled(True)
                self.nlo.setEnabled(True)
                self.ksbutton.setEnabled(True)
                self.sbutton.setEnabled(True)
                self.fbutton.setEnabled(True)
        else:
            self.s_bar.setStyleSheet(self.s_norm)
            self.s_bar.showMessage('# Cleard devices list')
            self.ci_list.clear()
            self.cle_btn.setEnabled(False)
            self.ci_list.setEnabled(False)
            self.ksbutton.setEnabled(False)
            self.llo.setEnabled(False)
            self.nlo.setEnabled(False)
            self.sbutton.setEnabled(False)
            self.fbutton.setEnabled(False)
        return True

    def inloop_state(self, out=False):
        if not out:
            self.lbtn.setEnabled(True)
            self.cle_btn.setEnabled(False)
            self.ci_list.setEnabled(False)
            self.ksbutton.setEnabled(False)
            self.llo.setEnabled(False)
            self.nlo.setEnabled(False)
            self.sbutton.setEnabled(False)
            self.fbutton.setEnabled(False)
        else:
            if self.P.isRunning():
                self.P.stop()
            self.lbtn.setEnabled(False)
            self.cle_btn.setEnabled(True)
            self.ci_list.setEnabled(True)
            self.ksbutton.setEnabled(True)
            self.llo.setEnabled(True)
            self.nlo.setEnabled(True)
            self.sbutton.setEnabled(True)
            self.fbutton.setEnabled(True)
            self.s_bar.clearMessage()
        return True

    def ds_bar(self, glo):
        self.s_bar = QStatusBar()
        self.s_error = "QStatusBar{color:red;font-weight:1000;}"
        self.s_loop = "QStatusBar{color:black;font-weight:1000;}"
        self.s_norm = "QStatusBar{color:blue;font-style:italic;"
        self.s_norm += "font-weight:500;}"
        self.s_bar.setStyleSheet(self.s_norm)
        glo.addWidget(self.s_bar)

    def eout(self):
        msgg = "<center>"
        msgg += " Opps, a critical error has occurred, we will be "
        msgg += " grateful if you can help fixing it, by reporting to us "
        msgg += " at : <br><br> "
        msgg += "<b><a href='https://chrome-cut.github.io/'> "
        msgg += "https://chrome-cut.github.io/ </a></b> </center>"
        mm = QMessageBox.critical(
            self,
            "Critical Error",
            msgg,
            QMessageBox.Ok)
        exit(0)


def gui():
    appg = QApplication(argv)
    window = CC_window()
    QCoreApplication.processEvents()
    appg.exec_()
    exit(0)
