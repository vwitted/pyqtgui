import sys
from json import loads
from math import sqrt
from threading import Thread
from time import sleep
from urllib.parse import urlencode

from PyQt5.QtCore import (QObject,
                          Qt, QTimer, pyqtSignal)
from PyQt5.QtGui import (QCursor, QTextCursor)
from PyQt5.QtWidgets import (QApplication, QMainWindow,
                             QTextEdit, qApp)
from requests import *


class Worker(QObject):
    htmlChanged = pyqtSignal(str)
    def execute(self):
        Thread(target=self.getData, daemon=True).start()

    def getData(self):
        while True:
            sleep(5)
            keyword=QTextCursor().selectedText()
            if keyword != '':
                url="https://www.googleapis.com"
                params={'key':'AIzaSyAYXbklVtZ3YfXrwMqRxNeIgVJjcYQhD4Q','cx':'dd135e2427e2fe0e6','q':'{0} ext:py'.format(keyword)}
                url = url + "/customsearch/v1?" + urlencode(params)
                req = get(url)
                while req is None or req.status_code != 200:
                    pass
                html=['<a href="' + x["link"]+ '">' + x["htmlSnippet"]  + "/>" for x in dict(loads(req.text))["items"]]
                html=("<html></body>" + "<br/><br/>".join(html) + "</body></html>").replace("\n","<br\>")  
                self.htmlChanged.emit(html)


class MainWindow(QMainWindow):

    def __init__(self,focusPolicy=None):
        super(MainWindow, self).__init__()
        self.updatesCount = 0
        self.istransparent=False
        self.setStyleSheet("background-color:gray")
        if focusPolicy != Qt.StrongFocus:
            self.setFocusPolicy(Qt.NoFocus)
            self.setWindowFlags(self.windowFlags() | Qt.WindowTransparentForInput | Qt.WindowStaysOnTopHint)
            self.istransparent=True
        else:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint | Qt.WindowActive)
            self.setFocusPolicy(Qt.StrongFocus)
            self.istransparent=False
        self.textEdit = QTextEdit(self)
        self.textEdit.setGeometry(int(QApplication.desktop().width()/2),int(QApplication.desktop().height()/2),50,50)
        self.setCentralWidget(self.textEdit)
        self.setProperty("windowOpacity", 0.5)
        self.textEdit.setMouseTracking(True)
        self.textEdit.setFontPointSize(20)
        self.qtimer = QTime(self)
        self.qtimer.setTimerType(Qt.PreciseTimer)
        self.qtimer.start(100)
        QApplication.processEvents()
        worker = Worker(self)
        worker.htmlChanged.connect(self.textEdit.setHtml)
        worker.execute()
        self.show()

    def onUpdate(self):
        self.updatesCount +=1
        if self.istransparent:                
            a=abs(QCursor.pos().x()-self.geometry().center().x())
            b=abs(QCursor.pos().y()-self.geometry().center().y())
            distance = sqrt((pow(a,2)) +  pow(b,2))
            edgedistance=distance - self.width()/2
            screendiag=sqrt(pow(qApp.desktop().width(),2) + pow(qApp.desktop().height(),2))
            reldist= (edgedistance / screendiag) + 0.4
            if reldist > 0.1:
                self.setProperty('windowOpacity',reldist)    #reldist=1-(reldist/(1.5+reldist))
            else:
                self.setProperty('windowOpacity',0.08)
        else:
            self.setProperty('windowOpacity',0.8)
        modifiers = qApp.queryKeyboardModifiers()
        if (self.updatesCount > 10) and (modifiers == Qt.AltModifier) and self.geometry().contains(QCursor.pos()):
            self.updatesCount = 0
        
            if self.istransparent:
                # & removes bitwise flag
                self.setWindowFlags(QMainWindow().windowFlags() | Qt.WindowStaysOnTopHint)
                self.setFocusPolicy(Qt.StrongFocus)
                self.setFocus()
                self.show()
                QApplication.processEvents()
                self.istransparent=False
            else:
                self.setWindowFlags(QMainWindow().windowFlags()  | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput)
                self.setFocusPolicy(Qt.NoFocus)
                self.istransparent=True
         
    def mouseMoveEvent(self,e):
        if self.geometry().contains(QCursor.pos()) and self.mapFromGlobal(QCursor.pos()).y() < (self.height()/4):
             if QApplication.mouseButtons() == Qt.LeftButton > 0:
                oldPos = QCursor.pos()
                while QApplication.mouseButtons() & Qt.LeftButton != 0:
                    self.move(QCursor.pos()-oldPos)
                e.accept()         


class QTime(QTimer):

    def __init__(self, window, parent=None):
        super().__init__(parent)
        self.window = window
    
    def timerEvent(self, e):
        self.window.onUpdate()
        QApplication.processEvents()
        self.window.show()
        return super().timerEvent(e)

            
class MyQApplication(QApplication):

    def ___init__(self,argv):
        super(MyQApplication,self).__init__(argv)
    

def reverseFocusPolicy(window=None,focusPolicy=Qt.StrongFocus):
    focus=lambda f=Qt.StrongFocus: Qt.StrongFocus if f == Qt.NoFocus else Qt.NoFocus
    return (focus(focusPolicy) if not isinstance(window,MainWindow) else focus(window.focusPolicy()))

if __name__ == '__main__':
    app = MyQApplication(sys.argv)
    app.mainWin = MainWindow()
    app.mainWin.setMouseTracking(True)
    [w.setMouseTracking(True) for w in app.mainWin.children() if 'setMouseTracking' in w.__dir__()]
    app.mainWin.show()
    sys.exit(app.exec_())

