import sys
from asyncio import Task, base_events
from http import HTTPStatus, client
from json import loads
from math import sqrt
from operator import contains, methodcaller
from threading import Thread
from time import sleep
from types import CodeType, FunctionType, TracebackType
from typing import cast
from urllib.parse import urlencode

from PyQt5.QtCore import (QCoreApplication, QEvent, QObject,
                          QPoint, QRect, QSize, Qt, QThread, QThreadPool,
                          QTimer, QtSystemMsg)
from PyQt5.QtGui import (QCursor, QHoverEvent, QIcon, QKeyEvent, QKeySequence,
                         QMouseEvent, QTextCursor)
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow,
                             QMessageBox, QPlainTextEdit, QTextEdit, QWidget,
                             qApp)
from requests import *


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
        self.qtimer = QTime(self)
        self.qtimer.setTimerType(Qt.PreciseTimer)
        self.qtimer.start(100)
        QApplication.processEvents()
        self.t = Thread(target=self.getData,group=None)
        self.t.start()
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
        if self.updatesCount > 10 and modifiers &\
        Qt.AltModifier == Qt.AltModifier and self.geometry().contains(QCursor.pos()):
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

    def getData(self):
        while True:
            sleep(5)
            keyword=QTextCursor().selectedText()
            keyword="help"
            if keyword != '':
                url="https://www.googleapis.com"
                params={'key':'AIzaSyAYXbklVtZ3YfXrwMqRxNeIgVJjcYQhD4Q','cx':'dd135e2427e2fe0e6','q':'{0} ext:py'.format(keyword)}
                url = url + "/customsearch/v1?" + urlencode(params)
                req = get(url)
                while req is None or req.status_code != 200:
                    pass
                html=['<a href="' + x["link"]+ '">' + x["htmlSnippet"]  + "/>" for x in dict(loads(req.text))["items"]]
                self.textEdit.setHtml(("<html></body>" + "<br/><br/>".join(html)+ "</body></html>").replace("\n","<br\>"))
                


    def enterEvent(self,e):
        # movedown=((self.x()-self.width()) / QApplication.desktop().width()) < 0.005
        # moveleft=((self.y()+self.height()) / QApplication.desktop().height()) < 0.005
        # pX=-1
        # pY=-1
        # if moveleft:
        #     pX=1
        # if movedown:
        #     pY=1
        # self.move(QCursor.pos().x()+(pX*50),QCursor.pos().y() + (pY *50))
       
        e.ignore()
        return super(MainWindow,self).enterEvent(e)

    def mouseMoveEvent(self,e):
        if self.geometry().contains(QCursor.pos()) and self.mapFromGlobal(QCursor.pos()).y() < (self.height()/4):
             if QApplication.mouseButtons() == Qt.LeftButton > 0:
                oldPos = QCursor.pos()
                while QApplication.mouseButtons() & Qt.LeftButton != 0:
                    self.move(QCursor.pos()-oldPos)
                e.accept()
    
    #        

    #         self.parent().setGeometry(QCursor.pos().x(),QCursor.pos().y(),self.parent().width(), self.parent().height())
    #         self.parent().show()
    #         QApplication.processEvents()
    

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

   
        


    # def event(self, e):
    #     print(e.type())
    #     if (not isinstance(e,QChildEvent)) and (e.type() & QEvent.KeyPress != 0):
    #         print(type(e))
    #         try:
    #             key = QKeyEvent(e).key()
    #             if (key == Qt.Key_Alt):
    #                 if (e.type() & QEvent.MouseMove) +\
    #                 (e.type() &  QEvent.HoverEnter) +\
    #                 (e.type() &  QEvent.HoverMove) > 0:
    #                     if isinstance(app.mainWin,MainWindow):
    #                         app.mainWin.setWindowFlags(QMainWindow().windowFlags() | Qt.WindowActive | Qt.WindowStaysOnTopHint)
    #                         app.mainWin.setFocus()
    #                         app.mainWin.show()
    #                         app.processEvents()
    #                         e.ignore()
    #                         return True        
    #         except TypeError as ex:
    #             ex.with_traceback(None)
    #     return super().event(e)
    


def reverseFocusPolicy(window=None,focusPolicy=Qt.StrongFocus):
    focus=lambda f=Qt.StrongFocus: Qt.StrongFocus if f == Qt.NoFocus else Qt.NoFocus
    return (focus(focusPolicy) if not isinstance(window,MainWindow) else focus(window.focusPolicy()))

    

    

if __name__ == '__main__':
    app = MyQApplication(sys.argv)
    app.mainWin = MainWindow()
    app.mainWin.setMouseTracking(True)
    [w.setMouseTracking(True) for w in app.mainWin.children() if 'setMouseTracking' in w.__dir__()]
    #[setattr(c,'',lambda e: mouseMoveEvent(e,c) and c.setMouseTracking(True)) for c in mainWin.children() if 'mouseMoveEvent' in c.__dir__()]
    app.mainWin.show()
    sys.exit(app.exec_())

