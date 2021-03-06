﻿#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 骆克云
# @Date:   2015-10-03 20:47:24
# @Last Modified by:   骆克云
# @Last Modified time: 2015-10-11 14:49:09

from PyQt4 import QtCore,QtGui
from pymongo import MongoClient
import subprocess
import os
import datetime

import Scraper_rc

class ConfigurationPage(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ConfigurationPage, self).__init__(parent)

        configGroup = QtGui.QGroupBox(u"网站设置")

        #项目名称
        projectLabel = QtGui.QLabel(u"项目名称:")
        projectEdit = QtGui.QLineEdit()
        projectEdit.setText(u"上海市政府信息采购网站爬取")
        projectEdit.setReadOnly(True)

        #网址
        serverLabel = QtGui.QLabel(u"网址:")
        serverCombo = QtGui.QComboBox()
        serverCombo.addItem("http://www.shzfcg.gov.cn:8090/new_web/cjxx/center_hz_zb.jsp")

        #爬取模块
        spiderLabel=QtGui.QLabel(u"爬取模块:")
        spiderEdit=QtGui.QLineEdit()
        spiderEdit.setText("shzfcgSpider")
        spiderEdit.setReadOnly(True)
        
        #布局设置
        projectLayout=QtGui.QGridLayout()
        projectLayout.addWidget(projectLabel,0,0)
        projectLayout.addWidget(projectEdit,0,1)
        projectLayout.addWidget(serverLabel,1,0)
        projectLayout.addWidget(serverCombo,1,1)
        projectLayout.addWidget(spiderLabel,2,0)
        projectLayout.addWidget(spiderEdit,2,1)

        configGroup.setLayout(projectLayout)

        #网站分析
        parameterGroup=QtGui.QGroupBox(u"参数分析-域设置")
    
        fieldList= QtGui.QListWidget()
    
        projNameItem=QtGui.QListWidgetItem(fieldList)
        projNameItem.setText("projName")
        merchantItem=QtGui.QListWidgetItem(fieldList)
        merchantItem.setText("merchant")
        dateItem=QtGui.QListWidgetItem(fieldList)
        dateItem.setText("date")
        priceItem=QtGui.QListWidgetItem(fieldList)
        priceItem.setText("price")

        parameterLayout= QtGui.QVBoxLayout()
        parameterLayout.addWidget(fieldList)
        parameterGroup.setLayout(parameterLayout)

        #数据库设置
        dataBaseGroup=QtGui.QGroupBox(u"MongoDB数据库")
        staticData=(("MONGODB_SERVER","localhost"),("MONGODB_PORT","27017"),("MONGODB_DB","shzfcg"),("MONGODB_COLLECTION","caigou"),)

        tableWidget = QtGui.QTableWidget(4, 2)
        headerLabels = (u"MongoDB参数", u"值")
        tableWidget.setHorizontalHeaderLabels(headerLabels)

        for row,(mongoParameter,mongoValue) in enumerate(staticData):
            item0=QtGui.QTableWidgetItem(mongoParameter)
            item1=QtGui.QTableWidgetItem(mongoValue)
            tableWidget.setItem(row,0,item0)
            tableWidget.setItem(row,1,item1)

        tableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        mongoDBLayout=QtGui.QVBoxLayout()
        mongoDBLayout.addWidget(tableWidget)
        dataBaseGroup.setLayout(mongoDBLayout)

        #主布局设计
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(configGroup)
        mainLayout.addWidget(parameterGroup)
        mainLayout.addWidget(dataBaseGroup)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)


class CrawlPage(QtGui.QWidget):
    def __init__(self, parent=None):
        super(CrawlPage, self).__init__(parent)
        self.success=True
        #爬虫布局
        crawlGroup = QtGui.QGroupBox(u"爬虫")
        startButton=QtGui.QPushButton(u"开始")
        self.textEdit = QtGui.QTextEdit()
        self.textEdit.setMaximumHeight(100)
        self.textEdit.setReadOnly(True)

        startButton.clicked.connect(self.crawl)
        
        crawlLayout = QtGui.QVBoxLayout()
        crawlLayout.addWidget(startButton)
        crawlLayout.addWidget(self.textEdit)
        crawlGroup.setLayout(crawlLayout)

        #结果布局
        resultGroup=QtGui.QGroupBox(u"爬虫结果")
        self.table=QtGui.QTableWidget(0,4)
        self.table.setMinimumHeight(450)
        #设置标题头
        headerLabels = (u"项目名称", u"成交供应商",u"采购日期",u"成交金额")
        self.table.setHorizontalHeaderLabels(headerLabels)
       # self.table.resizeColumnsToContents()
       # self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.table.setColumnWidth(0,400)
        self.table.setColumnWidth(1,200)
        #改变颜色
        self.table.setAlternatingRowColors(True)
        resultLayout=QtGui.QVBoxLayout()
        resultLayout.addWidget(self.table)
        resultGroup.setLayout(resultLayout)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(crawlGroup)
        mainLayout.addWidget(resultGroup)
        mainLayout.addSpacing(12)
        mainLayout.addStretch(1)

        self.showResult(False)
        
        self.setLayout(mainLayout)

    def crawl(self):

        self.success=True
        #删除原有数据
        client=MongoClient()
        db=client.shzfcg
        db.caigou.drop()
        
        self.table.clearContents()

        if os.path.exists("./Scraper.py"):
            os.chdir("shzfcg/")

        p=subprocess.Popen("scrapy crawl shzfcgSpider",shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        self.textEdit.clear()
        cursor = self.textEdit.textCursor()
        for line in p.stdout.readlines():
            cursor.insertText(line)
            if line.find("DNS lookup failed"):
                1
                #self.success=False
        retval=p.wait()
        if p.returncode!=0:
            cursor.insertText("error!")
            return -1
        self.showResult(self.success)
        client.close()
        

    def showResult(self,isShow):
        if not isShow:
            return
        client=MongoClient()
        db=client.shzfcg
        collection=db.caigou
        self.table.setRowCount(collection.count())
        row=0
        for p in collection.find():
            item0=QtGui.QTableWidgetItem(p.get("projName","-1"))
            item1=QtGui.QTableWidgetItem(p.get("merchant","-1"))
            item2=QtGui.QTableWidgetItem(p.get("date","-1"))
            item3=QtGui.QTableWidgetItem(unicode(str(p.get("price","-1")))) #utf-8-->unicode
            #print "p.get(price):", p.get("price","-1")
            self.table.setItem(row,0,item0)
            self.table.setItem(row,1,item1)
            self.table.setItem(row,2,item2)
            self.table.setItem(row,3,item3)
            row=row+1
        client.close()
       


class QueryPage(QtGui.QWidget):
    def __init__(self, parent=None):
        super(QueryPage, self).__init__(parent)

        packagesGroup = QtGui.QGroupBox(u"查询")

        merchantLabel = QtGui.QLabel(u"供应商:")
        self.merchantEdit = QtGui.QLineEdit()

        projLabel = QtGui.QLabel(u"项目名称:")
        self.projEdit = QtGui.QLineEdit()

        self.fromDateEdit = QtGui.QDateEdit()
        self.fromDateEdit.setDate(QtCore.QDate(2015, 1, 1))
        self.fromDateEdit.setCalendarPopup(True)
        fromLabel = QtGui.QLabel(u"时间起始:")
        fromLabel.setBuddy(self.fromDateEdit)
        self.toDateEdit = QtGui.QDateEdit()
        self.toDateEdit.setDate(QtCore.QDate.currentDate())
        self.toDateEdit.setCalendarPopup(True)
        toLabel = QtGui.QLabel(u"截至:")
        toLabel.setBuddy(self.toDateEdit)

        priceLabel=QtGui.QLabel(u"金额:")
        self.priceLowSpinBox = QtGui.QSpinBox()
        self.priceLowSpinBox.setPrefix(u"金额下限: ")
        self.priceLowSpinBox.setSuffix(u" 元")
        self.priceLowSpinBox.setSpecialValueText(u"金额下限: 0 元")
        self.priceLowSpinBox.setMinimum(0)
        self.priceLowSpinBox.setMaximum(1000000)
        self.priceLowSpinBox.setSingleStep(100)


        self.priceHighSpinBox = QtGui.QSpinBox()
        self.priceHighSpinBox.setPrefix(u"金额上限: ")
        self.priceHighSpinBox.setSuffix(u" 万元")
        self.priceHighSpinBox.setSpecialValueText(u"金额上限: 1000000 万元")
        self.priceHighSpinBox.setMinimum(0)
        self.priceHighSpinBox.setMaximum(1000000)
        self.priceHighSpinBox.setValue(10000)
        self.priceHighSpinBox.setSingleStep(100)


        startQueryButton = QtGui.QPushButton(u"开始查询")
        clearQueryButton=QtGui.QPushButton(u"清除结果")

         #结果布局
        resultGroup=QtGui.QGroupBox(u"爬虫结果")
        self.table=QtGui.QTableWidget(0,4)
        self.table.setMinimumHeight(450)
        headerLabels = (u"项目名称", u"成交供应商",u"采购日期",u"成交金额")
        self.table.setHorizontalHeaderLabels(headerLabels)
        self.table.setColumnWidth(0,400)
        self.table.setColumnWidth(1,200)
        #改变颜色
        self.table.setAlternatingRowColors(True)
        #self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        resultLayout=QtGui.QVBoxLayout()
        resultLayout.addWidget(self.table)
        resultGroup.setLayout(resultLayout)

        packagesLayout = QtGui.QGridLayout()
        packagesLayout.addWidget(projLabel, 0, 0)
        packagesLayout.addWidget(self.projEdit, 0, 1)
        packagesLayout.addWidget(merchantLabel, 0, 2)
        packagesLayout.addWidget(self.merchantEdit, 0, 3)
        packagesLayout.addWidget(fromLabel, 1, 0)
        packagesLayout.addWidget(self.fromDateEdit, 1, 1, 1, 1)
        packagesLayout.addWidget(toLabel, 1, 2)
        packagesLayout.addWidget(self.toDateEdit, 1, 3, 1, 1)
        packagesLayout.addWidget(priceLabel,2,0)
        packagesLayout.addWidget(self.priceLowSpinBox, 2, 1, 1, 1)
        packagesLayout.addWidget(self.priceHighSpinBox, 2, 3, 1, 1)
        packagesLayout.addWidget(startQueryButton,3,1)
        packagesLayout.addWidget(clearQueryButton,3,3)
        
        packagesGroup.setLayout(packagesLayout)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(packagesGroup)
        mainLayout.addWidget(resultGroup)
        mainLayout.addSpacing(12)
        mainLayout.addStretch(1)

        self.showResult(False,queryCollection=[])
        startQueryButton.clicked.connect(self.queryResult)
        clearQueryButton.clicked.connect(self.clearResult)       
        self.setLayout(mainLayout)

    def queryResult(self):
        projName=unicode(self.projEdit.text())
        merchant=unicode(self.merchantEdit.text())
        fromDate=unicode(self.fromDateEdit.date().toString("yyyy-MM-dd"))
        toDate=unicode(self.toDateEdit.date().toString("yyyy-MM-dd"))
        lowPrice=unicode(self.priceLowSpinBox.value())

        lowPrice=lowPrice.encode("utf-8")
        highPrice=unicode(self.priceHighSpinBox.value()*10000)
        highPrice=highPrice.encode("utf-8")
        
        client=MongoClient()
        db=client.shzfcg
        collection=db.caigou
        highPrice=int(highPrice)-1
        if projName!="" and merchant=="":
            queryCollection=collection.find({"date":{"$gte":str(fromDate),"$lte":str(toDate)},"projName":{"$regex":projName},"price":{"$gte":float(lowPrice),"$lte":float(highPrice)}})
        elif projName !="" and merchant!="":
            queryCollection=collection.find({"date":{"$gte":str(fromDate),"$lte":str(toDate)},"projName":{"$regex":projName},"merchant":{"$regex":merchant},"price":{"$gte":float(lowPrice),"$lte":float(highPrice)}})
        elif projName=="" and merchant!="":
            queryCollection=collection.find({"date":{"$gte":str(fromDate),"$lte":str(toDate)},"merchant":{"$regex":merchant},"price":{"$gte":float(lowPrice),"$lte":float(highPrice)}})
        else:
            queryCollection=collection.find({"date":{"$gte":str(fromDate),"$lte":str(toDate)},"price":{"$gte":float(lowPrice),"$lte":float(highPrice)}})
        self.showResult(True,queryCollection)
        client.close()

    def clearResult(self):
        self.table.clearContents()

    def showResult(self,isShow,queryCollection):
        if not isShow:
            return
       
        self.table.setRowCount(queryCollection.count())
        row=0
        for p in queryCollection:
            item0=QtGui.QTableWidgetItem(p.get("projName","-1"))
            item1=QtGui.QTableWidgetItem(p.get("merchant","-1"))
            item2=QtGui.QTableWidgetItem(p.get("date","-1"))
            item3=QtGui.QTableWidgetItem(unicode(str(p.get("price","-1")))) #utf-8-->unicode
            self.table.setItem(row,0,item0)
            self.table.setItem(row,1,item1)
            self.table.setItem(row,2,item2)
            self.table.setItem(row,3,item3)
            row=row+1


class ConfigDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(ConfigDialog, self).__init__(parent)
        self.setFixedSize(1024,705)
        self.contentsWidget = QtGui.QListWidget()
        self.contentsWidget.setViewMode(QtGui.QListView.IconMode)
        self.contentsWidget.setIconSize(QtCore.QSize(96, 84))
        self.contentsWidget.setMovement(QtGui.QListView.Static)
        self.contentsWidget.setMaximumWidth(128)
        self.contentsWidget.setSpacing(12)

        self.pagesWidget = QtGui.QStackedWidget()
        self.pagesWidget.addWidget(ConfigurationPage())
        self.pagesWidget.addWidget(CrawlPage())
        self.pagesWidget.addWidget(QueryPage())

        closeButton = QtGui.QPushButton(u"关闭")

        self.createIcons()
        self.contentsWidget.setCurrentRow(1)

        closeButton.clicked.connect(self.close)

        horizontalLayout = QtGui.QHBoxLayout()
        horizontalLayout.addWidget(self.contentsWidget)
        horizontalLayout.addWidget(self.pagesWidget, 1)

        buttonsLayout = QtGui.QHBoxLayout()
        buttonsLayout.addStretch(1)
        buttonsLayout.addWidget(closeButton)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addLayout(horizontalLayout)
        mainLayout.addStretch(1)
        mainLayout.addSpacing(12)
        mainLayout.addLayout(buttonsLayout)

        self.setLayout(mainLayout)

        self.setWindowTitle(u"上海政府采购网爬虫")


    def changePage(self, current, previous):
        if not current:
            current = previous

        self.pagesWidget.setCurrentIndex(self.contentsWidget.row(current))

    def createIcons(self):
        configButton = QtGui.QListWidgetItem(self.contentsWidget)
        configButton.setIcon(QtGui.QIcon(u':/images/配置.png'))
        configButton.setText(u"配置")
        configButton.setTextAlignment(QtCore.Qt.AlignHCenter)
        configButton.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        updateButton = QtGui.QListWidgetItem(self.contentsWidget)
        updateButton.setIcon(QtGui.QIcon(u':/images/爬取.png'))
        updateButton.setText(u"爬取")
        updateButton.setTextAlignment(QtCore.Qt.AlignHCenter)
        updateButton.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        queryButton = QtGui.QListWidgetItem(self.contentsWidget)
        queryButton.setIcon(QtGui.QIcon(u':/images/查询.png'))
        queryButton.setText(u"查询")
        queryButton.setTextAlignment(QtCore.Qt.AlignHCenter)
        queryButton.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        self.contentsWidget.currentItemChanged.connect(self.changePage)


if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    dialog = ConfigDialog()
    sys.exit(dialog.exec_()) 
