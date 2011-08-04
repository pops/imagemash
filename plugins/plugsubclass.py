#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
#Copyright pops (pops451@gmail.com), 2010-2011
#
#This file is part of imagemash.
#
#    imagemash is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    imagemash is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with imagemash.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import division
from PyQt4 import QtGui
from PyQt4 import QtCore


class Viewer(QtGui.QScrollArea):
    """ Class doc """
    zoomOut = QtCore.pyqtSignal()
    zoomIn = QtCore.pyqtSignal()
    
    def __init__ (self, parent=None):
        QtGui.QScrollArea.__init__(self, parent)
        self.parent = parent
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.wheelEvent = self.wheel
        
    def wheel(self, event):
        """ send a zoom in or out signal """
        if event.delta() > 0:
            self.zoomIn.emit()
        elif event.delta() < 0:
            self.zoomOut.emit()
    
    # bof
    def zoom(self, n):
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() * n)
        self.verticalScrollBar().setValue(self.verticalScrollBar().value() * n)
        
    def event(self, event):
        """ capture middle mouse event to move the view """
        # clic millieu: on memorise l'endroit pour le drag
        if (event.type()==QtCore.QEvent.MouseButtonPress) and (event.button()==QtCore.Qt.MidButton):
            self.mouseX = event.x()
            self.mouseY = event.y()
            return True
            
        # drag millieu: on se deplace dans l'image
        elif (event.type()==QtCore.QEvent.MouseMove) and (event.buttons()==QtCore.Qt.MidButton):
            diffX = event.x() - self.mouseX
            self.mouseX = event.x()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - diffX)
            diffY = event.y() - self.mouseY
            self.mouseY = event.y()
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - diffY)
            return True
        return QtGui.QScrollArea.event(self, event)


class Painting(QtGui.QWidget):
    """ preview of the image and interation with the mouse
    """
    clicSignal = QtCore.pyqtSignal(tuple) # x, y, zoom
    moveSignal = QtCore.pyqtSignal(tuple) # x, y, zoom
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        
        self.isFig = False
        
        self.zoomN = 1
        self.imOri = QtGui.QImage()
        
    def set_fig(self, fig, color=QtGui.QColor(0, 0, 0)):
        """ set a figure to draw on the image
        """
        self.fig = fig
        self.isFig = True
        self.color = color
        self.fig.figChanged.connect(self.draw)
        
    def paintEvent(self, ev):
        p = QtGui.QPainter()
        p.begin(self)
        p.drawImage(QtCore.QPoint(0, 0), self.imQPainter)
        p.end()
            
    def draw(self):
        """ draw the image and the figure if any
        """
        p = QtGui.QPainter()
        p.begin(self.imQPainter)
        p.drawImage(QtCore.QPoint(0, 0), self.imOriZoomed)
        if self.isFig:
            for i in self.fig.to_draw(self.zoomN, self.zImW, self.zImH):
                if i[0] == "cadre":
                    p.setPen(QtGui.QPen(self.color, 1, QtCore.Qt.SolidLine))
                    alpha = self.color
                    alpha.setAlpha(100)
                    p.setBrush(alpha)
                    p.drawPath(i[1])
                if i[0] == "ligne":
                    p.setPen(QtGui.QPen(self.color, 1, QtCore.Qt.SolidLine))
                    p.drawPath(i[1])
                if i[0] == "poignee":
                    p.setPen(QtGui.QPen(self.color, 1, QtCore.Qt.SolidLine))
                    p.setBrush(QtGui.QColor(255, 255, 255, 255))
                    p.drawPath(i[1])
        p.end()
        self.update()
        
    def zoom(self, n=1):
        if n == 0:
            self.zoomN = 1
        else:
            self.zoomN = self.zoomN * n
        self.zImH = self.imH * self.zoomN
        self.zImW = self.imW * self.zoomN
        self.imOriZoomed = self.imOri.scaled(self.zImW, self.zImH)
        self.imQPainter = self.imOri.scaled(self.zImW, self.zImH)
        self.setFixedSize(self.zImW, self.zImH)
        self.draw()
                
    def change_image(self, image, code=""):
        self.imOri.load(image)
        code = code.replace("$i", "self.imOri")
        exec(code)
        self.imH = self.imOri.height()
        self.imW = self.imOri.width()
        self.zoom()
        
    def apply_code(self, code):
        code = code.replace("$i", "self.imOri")
        exec(code)
        self.imH = self.imOri.height()
        self.imW = self.imOri.width()
		
    def event(self, event):
        ### clic ###
        if   (event.type() == QtCore.QEvent.MouseButtonPress and 
              event.button() == QtCore.Qt.LeftButton):
            self.clicSignal.emit(event.x(), event.y(), self.zoomN)
            return True
        ### move ###
        elif (event.type() == QtCore.QEvent.MouseMove and 
              event.buttons() == QtCore.Qt.LeftButton):
            self.moveSignal.emit(event.x(), event.y(), self.zoomN)
            self.draw()
            return True
        return QtGui.QWidget.event(self, event)
        
