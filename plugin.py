# -*- coding: utf-8 -*-
# модули Qt4
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# сама Quantum GIS
from qgis.core import *

# почему-то половина методов не работает без такого объявления
from PyQt4 import QtGui,QtCore

# инициализируем ресурсы Qt из файла resouces.py
import resources

# подгружаем форму
from form import Ui_Dialog

# библиотеки CVLib
from opencv.cv import *
from opencv.highgui import *

# работа с shapefile
#from shapefil import makeShapefile

# математические функции
from math import sin,cos

#class Window(QtGui.QWidget):
class Window(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

def makeVecLayer(vl,lines):
    pr = vl.dataProvider()

    fet = QgsFeature()
    for line in lines:
        ptF = QgsPoint(line[0].x,-line[0].y)
        ptT = QgsPoint(line[1].x,-line[1].y)
        fet.setGeometry(QgsGeometry.fromPolyline([ptF,ptT]))
        pr.addFeatures([fet])

class HoughTransform():
    def __init__(self,iface):
        """Инициализирует класс"""
        self.iface = iface # сохраним ссылку на интерфейс QGIS

    def initGui(self):
        """Инициализирует графический интерфейс пользователя"""
        # создадим действие, которое будет запускать конфигурацию расширения
        self.action = QAction(QIcon(":/plugins/testplugin/icon.png"), "Hough Tranformation", self.iface.mainWindow())
        self.action.setWhatsThis("Proceeding the hough transformation")
        self.action.setStatusTip("Hough transformation")

        # соединяем действие с методом run
        QObject.connect(self.action, SIGNAL("activated()"), self.run)

        # добавляем кнопку на панель инструментов
        self.iface.addToolBarIcon(self.action)

        # добавляет новый элемент главного меню
        self.iface.addPluginToMenu("Hough transformation", self.action)

    def unload(self):
        """Действия при дизактивации плагина"""
        # удаляем иконку из панели и запись в меню
        self.iface.removePluginMenu("Hough transformation",self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        """ Запуск плагина """
        win = Window()
        # Составляю список растровых слоев
        mc = self.iface.mapCanvas()
        nLayers = mc.layerCount()
        for l in range(nLayers):
            layer = mc.layer(l)
            if layer.type() == 1: # raster layer
                win.ui.cbRast.addItem(layer.name())
            if layer.type() == 0:
                win.ui.cbVect.addItem(layer.name())
        # Показываю форму и жду
        win.show()
        result = win.exec_()
    
        if result == 1: # пользователь нажал OK
            c1 = int(win.ui.canny1.text())
            c2 = int(win.ui.canny2.text())
            p1 = int(win.ui.param1.text())
            p2 = int(win.ui.param2.text())

            # ищем какой слой выбрал пользователь
            nLayers = mc.layerCount()
            for l in range(nLayers):
                layer = mc.layer(l)
                if layer.name() == win.ui.cbRast.currentText():
                    cur_layer = mc.layer(l)
                if layer.name() == win.ui.cbVect.currentText():
                    vl = mc.layer(l)
    
            # подготовка к преобразованию Хафа
            src = cvLoadImage(str(cur_layer.source().toLocal8Bit()),0)
            if not src:
                QMessageBox.information(self.iface.mainWindow(),"Error","Error opening image")
            dst = cvCreateImage(cvGetSize(src),8,1)
            
            storage = cvCreateMemStorage(0)
            lines = 0
            cvCanny(src,dst,c1,c2,3)
            
            # если пользователь выбрал probabilistic метод
            if win.ui.cbMetod.currentIndex() == 0:
                lines = cvHoughLines2(dst,storage, CV_HOUGH_PROBABILISTIC, 1, CV_PI/180, 50, p1,p2)
                makeVecLayer(vl,lines)
            
            # если пользователь выбрал стандартный метод
            if win.ui.cbMetod.currentIndex() == 1:
                n_lines = tuple()
                lines = cvHoughLines2( dst, storage, CV_HOUGH_STANDARD, 1, CV_PI/180, 100, 0, 0 )
                
                for i in range(min(lines.total, 100)):
                    line = lines[i]
                    rho = line[0]
                    theta = line[1]
                    pt1 = CvPoint()
                    pt2 = CvPoint()
                    a = cos(theta)
                    b = sin(theta)
                    x0 = a*rho 
                    y0 = b*rho
                    pt1.x = cvRound(x0 + 1500*(-b))
                    pt1.y = cvRound(y0 + 1500*(a))
                    pt2.x = cvRound(x0 - 1500*(-b))
                    pt2.y = cvRound(y0 - 1500*(a))
                    n_lines = n_lines[:i]+((pt1,pt2),)
                    makeVecLayer(vl,lines)
            vl.updateExtents()
