# -*- coding: utf-8 -*-
mVersion = "0.2"
def name():
  return "Hough transformation2"
def description():
  return "Proceeding the hough transformation."
def qgisMinimumVersion(): 
  return "1.0" 
def version():
  return mVersion
def authorName():
  return "Alexandr Leuschenko"
def classFactory(iface):
  from plugin import HoughTransform
  return HoughTransform(iface)
