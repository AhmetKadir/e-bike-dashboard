from PyQt5 import QtCore, QtGui, QtWidgets
from Helper.AnalogGaugeWidget import AnalogGaugeWidget
from PyQt5.QtGui import QFont, QFontDatabase, QColor
from PyQt5.QtCore import QTimer, QTime, QDateTime, QTimeZone, QByteArray, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
import os
import sys
from sim808_reader import GpsModule
from threading import Thread

folderPath = os.path.dirname(os.path.abspath(__file__))
iconPath = folderPath + "//Icons"
fontPath  = folderPath + "//Fonts"
backGroundImagePath = iconPath + "//background_4.jpg"

myFontName = "RifficFree-Bold"
myFontsPath = "//riffic"
fullFontName =  myFontsPath + "//" + myFontName + ".ttf"

alertBatteryIconPath = iconPath + "//alertBattery2.png"
directionIconPath = iconPath + "//directionIcon.png"
clockIconPath = iconPath + "//clock_5.png"
averageSpeedBackgroundIconPath = iconPath + "//blue_1.png"

companyNameStr = "HIGHTECHMOBI Bisiklet Teknolojileri LTD.ŞTİ."
brandNameStr = "QuadSmart"

_useMap = False
_useRealData = False

screenWidth = 1024
screenHeight = 600

class Ui_MainWindow(object):

    batteryLevel = 50
    
    remainingTimeValue = QTime(0, 6, 20) # 5 minutes 20 seconds
    isBlinkStarted = False
    isBatteryBlinkStarted = False
    ledOn = False
    
    tripDistanceTotalValue = 0
    avgSpeedValue = 0
    voltageValue = 36
    
    valueFont = None
    headerFont = None

    
    def setupUi(self, MainWindow):
    
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(screenWidth, screenHeight)
        # MainWindow.showFullScreen()
        # MainWindow.setCursor(Qt.BlankCursor)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        # self.centralwidget.setMouseTracking(False);

        fontId = QFontDatabase.addApplicationFont(fontPath + fullFontName)
        if fontId < 0:
            print('font not loaded')
                        
        families = QtGui.QFontDatabase.applicationFontFamilies(fontId)
        self.valueFont = QFont(families[0])
        self.headerFont = QFont(families[0])
        
        self.headerFont.setPointSize(screenWidth // 40)
        self.valueFont.setPointSize(screenWidth // 50)
        
        self.background = QtWidgets.QLabel(self.centralwidget)
        self.background.setGeometry(QtCore.QRect(0, 0, screenWidth, screenHeight))
        self.background.setPixmap(QtGui.QPixmap(backGroundImagePath))
        self.background.setScaledContents(True)
        self.background.setObjectName("background")
        
        if _useMap == True:
            self.createMapButton(MainWindow)
            
        # self.createLeftSignal()
        # self.createRightSignal()
        
        self.createBatteryLabel()
        self.createDateTimeDisplay()

        # update battery level every 30 second
        self.timer = QtCore.QTimer(MainWindow)
        self.timer.timeout.connect(self.updateBattery)
        self.timer.start(15000)
                
        self.createRemainingTimeLabel()
        
        self.timer = QtCore.QTimer(MainWindow)
        self.timer.timeout.connect(self.updateRemainingTime)
        self.timer.start(1000)
        
        self.createAverageSpeedLabel()

        self.createTripDistanceLabel()
        
        # update trip distance every 1 second
        self.timer = QtCore.QTimer(MainWindow)
        self.timer.timeout.connect(self.updateTripDistance)
        self.timer.start(1000)
        
        companyNameFont = QFont()
        companyNameFont.setFamily(myFontName)
        companyNameFont.setPointSize(screenWidth // 70)
        
        self.createCompanyNameLabel(companyNameFont)
        
        brandNameFont = QFont()
        brandNameFont.setFamily(myFontName)
        brandNameFont.setPointSize(13)
        
        self.createBrandNameLabel()
        
        self.createLedLabels()
                
        self.timer = QtCore.QTimer(MainWindow)
        self.timer.timeout.connect(lambda: self.blinkLed(self.led_label1))
        self.timer.start(500)
        
        self.timer = QtCore.QTimer(MainWindow)
        self.timer.timeout.connect(lambda: self.blinkLed(self.led_label2))
        self.timer.start(500)
        
        self.timer = QtCore.QTimer(MainWindow)
        self.timer.timeout.connect(lambda: self.blinkLed(self.led_label3))
        self.timer.start(500)
        
        self.timer = QtCore.QTimer(MainWindow)
        self.timer.timeout.connect(lambda: self.blinkLed(self.led_label4))
        self.timer.start(500)
        
        self.createVoltageWidget(companyNameFont)
        
        self.setupSpeedWidget(myFontName)
        
        # timer : calculate average speed 
        self.timer = QtCore.QTimer(MainWindow)
        self.timer.timeout.connect(self.calculateAvgSpeed)
        self.timer.start(1000)
        
        # update speed
        self.timer = QtCore.QTimer(MainWindow)
        self.timer.timeout.connect(self.updateSpeed)
        self.timer.start(1000)
    
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def createMapButton(self, MainWindow):
        self.mapButton = QtWidgets.QPushButton("Map", self.centralwidget)
        self.mapButton.setGeometry(int(screenWidth * 0.75),
                                   int(screenHeight * 0.05),
                                      int(screenWidth * 0.1),
                                        int(screenHeight * 0.1))
        self.mapButton.setFont(self.valueFont)
        self.mapButton.clicked.connect(self.open_map_gui)
        
        # create a widget it returnPressed to mapButton.click
        returnPressedWidget = QtWidgets.QLineEdit()
        returnPressedWidget.setGeometry(QtCore.QRect(0, 0, 0, 0))
        returnPressedWidget.setObjectName("returnPressedWidget")
        returnPressedWidget.returnPressed.connect(self.mapButton.click)
        
        from mapGui import MapWidget            
        self.mapWidget = MapWidget(self.centralwidget)
        self.mapWidget.setGeometry(QtCore.QRect(0, 0, screenWidth, screenHeight))
        self.mapWidget.setObjectName("mapWidget")
        self.mapWidget.setHidden(True)
            
        self.timer = QtCore.QTimer(MainWindow)
        self.timer.timeout.connect(self.update_map)
        self.timer.start(2000)

    def setupSpeedWidget(self, myFontName):
        speedWidgetWidth = int(screenWidth * 0.3)
        speedWidgetHeight = int(screenHeight * 0.6)
        speedWidgetPositionX = int(screenWidth * 0.80) 
        speedWidgetPositionY = int((screenHeight * 0.5)  - speedWidgetHeight // 2)
        
        self.speedWidget = AnalogGaugeWidget(self.centralwidget)
        self.speedWidget.setGeometry(QtCore.QRect(speedWidgetPositionX,
                                                  speedWidgetPositionY,
                                                  speedWidgetWidth,
                                                  speedWidgetHeight))
        self.speedWidget.setObjectName("speedWidget")
        self.speedWidget.setMaxValue(50)
        self.speedWidget.updateValue(1)
        self.speedWidget.setBigScaleColor(QColor(255, 255, 255, 255))
        self.speedWidget.setFineScaleColor(QColor(255, 255, 255, 255))
        self.speedWidget.setCustomGaugeTheme(color3="#005d97", color2="#001937", color1="#001928")
        self.speedWidget.setNeedleCenterColor(color3="#004458", color2="#8c3361", color1="#8c5088")  # center of needle
        self.speedWidget.setNeedleColor(255, 255, 255, 255)
        self.speedWidget.setNeedleColorOnDrag(0, 240, 240, 200)
        self.speedWidget.setScaleValueColor(255, 255, 255, 180)
        self.speedWidget.setDisplayValueColor(0, 242, 0, 255)
        
        self.speedWidget.scale_fontsize = 2
        self.speedWidget.value_fontsize = 2
        self.speedWidget.setScalaCount(5) #how many value shown on the scale
        self.speedWidget.setTotalScaleAngleSize(145)
        self.speedWidget.setScaleFontFamily(myFontName)
        self.speedWidget.setValueFontFamily(myFontName)

    def createVoltageWidget(self, companyNameFont):
        voltageWidgetWidth = int(screenWidth * 0.2)
        voltageWidgetHeight = int(screenHeight * 0.1)
        voltageWidgetPositionX = int((screenWidth - voltageWidgetWidth) * 0.04)
        voltageWidgetPositionY = int(screenHeight * 0.85)
        
        self.voltageWidget = QtWidgets.QLabel(self.centralwidget)
        self.voltageWidget.setGeometry(QtCore.QRect(voltageWidgetPositionX,
                                                    voltageWidgetPositionY,
                                                    voltageWidgetWidth,
                                                    voltageWidgetHeight))
        self.voltageWidget.setObjectName("widget")
        self.voltageWidget.setText("voltage : " + str(self.voltageValue) + " V")
        self.voltageWidget.setFont(companyNameFont)
        self.voltageWidget.setStyleSheet("color: white;")

    def createLedLabels(self):
        led_labels_width = int(screenWidth * 0.05)
        led_labels_height = int(screenHeight * 0.05)
        led_labels_position_x = int(screenWidth * 0.05)
        led_labels_position_y = int(screenHeight * 0.4)
        
        distance_between_leds = int(screenHeight * 0.07)
        
        self.led_label1 = QtWidgets.QLabel(self.centralwidget)
        self.led_label1.setGeometry(QtCore.QRect(led_labels_position_x,
                                                 led_labels_position_y,
                                                 led_labels_width,
                                                led_labels_height))
        self.led_label1.setObjectName("led_label1")
        self.led_label1.setStyleSheet("background-color: yellow; border-radius: 10px;")
        
        
        self.led_label2 = QtWidgets.QLabel(self.centralwidget)
        self.led_label2.setGeometry(QtCore.QRect(led_labels_position_x,
                                                led_labels_position_y + distance_between_leds,
                                                led_labels_width,
                                                led_labels_height))
        self.led_label2.setObjectName("led_label2")
        self.led_label2.setStyleSheet("background-color: yellow; border-radius: 10px;")
        
        distance_between_leds = distance_between_leds + int(screenHeight * 0.07)
        
        self.led_label3 = QtWidgets.QLabel(self.centralwidget)
        self.led_label3.setGeometry(QtCore.QRect(led_labels_position_x,
                                                 led_labels_position_y + distance_between_leds,
                                                 led_labels_width,
                                                 led_labels_height))
        self.led_label3.setObjectName("led_label3")
        self.led_label3.setStyleSheet("background-color: yellow; border-radius: 10px;")
        
        distance_between_leds = distance_between_leds + int(screenHeight * 0.07)
        
        self.led_label4 = QtWidgets.QLabel(self.centralwidget)
        self.led_label4.setGeometry(QtCore.QRect(led_labels_position_x,
                                                 led_labels_position_y + distance_between_leds,
                                                 led_labels_width,
                                                 led_labels_height))
        self.led_label4.setObjectName("led_label4")
        self.led_label4.setStyleSheet("background-color: yellow; border-radius: 10px;")

    def createBrandNameLabel(self):
        brandNameTextWidth = int(screenWidth * 0.2)
        brandNameTextHeight = int(screenHeight * 0.1)
        brandNameTextPositionX = int(screenWidth * 0.5 - brandNameTextWidth * 0.5)
        brandNameTextPositionY = int(screenHeight * 0.05)
        
        self.brandName = QtWidgets.QLabel(self.centralwidget)
        self.brandName.setGeometry(QtCore.QRect(brandNameTextPositionX,
                                                brandNameTextPositionY,
                                                brandNameTextWidth,
                                                brandNameTextHeight))
        self.brandName.setFont(self.valueFont)
        self.brandName.setObjectName("brandName")
        self.brandName.setText(brandNameStr)
        self.brandName.setStyleSheet("color: #DDDDDD;")

    def createCompanyNameLabel(self, companyNameFont):
        companyNameTextWidth = int(screenWidth * 0.5)
        companyNameTextHeight = int(screenHeight * 0.1)
        companyNameTextPositionX = int(screenWidth * 0.5 - companyNameTextWidth // 2)
        companyNameTextPositionY = int(screenHeight * 0.90)
        
        self.companyNameText = QtWidgets.QLabel(self.centralwidget)
        self.companyNameText.setGeometry(QtCore.QRect(companyNameTextPositionX,
                                                        companyNameTextPositionY,
                                                      companyNameTextWidth,
                                                      companyNameTextHeight))
        self.companyNameText.setFont(companyNameFont)
        self.companyNameText.setObjectName("companyName")
        self.companyNameText.setText(companyNameStr)
        self.companyNameText.setStyleSheet("color: #DDDDDD;")

    def createTripDistanceLabel(self):
        tripDistanceWidth = int(screenWidth * 0.2)
        tripDistanceHeight = tripDistanceWidth
        tripDistancePositionX = int(screenWidth * 0.65 - tripDistanceWidth // 2)
        tripDistancePositionY = int(screenHeight * 0.35)
        
        self.tripDistanceBackground = QtWidgets.QLabel(self.centralwidget)
        self.tripDistanceBackground.setGeometry(QtCore.QRect(tripDistancePositionX,
                                                             tripDistancePositionY,
                                                             tripDistanceWidth,
                                                             tripDistanceHeight))
        self.tripDistanceBackground.setPixmap(QtGui.QPixmap(averageSpeedBackgroundIconPath))
        self.tripDistanceBackground.setObjectName("tripDistanceBackground")
        self.tripDistanceBackground.setScaledContents(True)
        
        self.tripDistanceHeader = QtWidgets.QLabel(self.centralwidget)
        self.tripDistanceHeader.setGeometry(QtCore.QRect(tripDistancePositionX + tripDistanceWidth // 2 - 80,
                                                         tripDistancePositionY - 40,
                                                         tripDistanceWidth,
                                                         tripDistanceHeight))
        self.tripDistanceHeader.setFont(self.headerFont)
        self.tripDistanceHeader.setObjectName("tripDistanceTitle")
        self.tripDistanceHeader.setText("Yolculuk")
        self.tripDistanceHeader.setStyleSheet("color: white;")
        
        self.tripDistanceText = QtWidgets.QLabel(self.centralwidget)
        self.tripDistanceText.setGeometry(QtCore.QRect(tripDistancePositionX + tripDistanceWidth // 2 - 50,
                                                       tripDistancePositionY + 20,
                                                       tripDistanceWidth,
                                                       tripDistanceHeight))
        self.tripDistanceText.setFont(self.valueFont)
        self.tripDistanceText.setObjectName("tripDistance")
        self.tripDistanceText.setText(str(self.tripDistanceTotalValue)  + " km")
        self.tripDistanceText.setStyleSheet("color: white;")

    def createAverageSpeedLabel(self):
        averageSpeedBackgroundWidth = int(screenWidth * 0.2)
        averageSpeedBackgroundHeight = averageSpeedBackgroundWidth
        averageSpeedPositionX = int(screenWidth * 0.35 - averageSpeedBackgroundWidth // 2)
        averageSpeedPositionY = int(screenHeight * 0.35)
        
        self.averageSpeedBackground = QtWidgets.QLabel(self.centralwidget)
        self.averageSpeedBackground.setGeometry(QtCore.QRect(averageSpeedPositionX,
                                                             averageSpeedPositionY,
                                                             averageSpeedBackgroundWidth,
                                                             averageSpeedBackgroundHeight))
        self.averageSpeedBackground.setObjectName("averageSpeedBackground")
        self.averageSpeedBackground.setPixmap(QtGui.QPixmap(averageSpeedBackgroundIconPath))
        self.averageSpeedBackground.setScaledContents(True)
                
        self.averageSpeedHeader = QtWidgets.QLabel(self.centralwidget)
        self.averageSpeedHeader.setGeometry(QtCore.QRect(averageSpeedPositionX + averageSpeedBackgroundWidth // 2 - 80,
                                                         averageSpeedPositionY - 40,
                                                         averageSpeedBackgroundWidth,
                                                         averageSpeedBackgroundHeight))
        self.averageSpeedHeader.setObjectName("averageSpeed")
        self.averageSpeedHeader.setText("Ort Hız")
        self.averageSpeedHeader.setFont(self.headerFont)
        self.averageSpeedHeader.setStyleSheet("color: white;")
        
        self.averageSpeedText = QtWidgets.QLabel(self.centralwidget)
        self.averageSpeedText.setGeometry(QtCore.QRect(averageSpeedPositionX + averageSpeedBackgroundWidth // 2 - 20,
                                                       averageSpeedPositionY + 20,
                                                         averageSpeedBackgroundWidth,
                                                         averageSpeedBackgroundHeight))
        self.averageSpeedText.setObjectName("averageSpeed")
        self.averageSpeedText.setText(str(self.avgSpeedValue))
        self.averageSpeedText.setFont(self.valueFont)
        self.averageSpeedText.setStyleSheet("color: white;")

    def createRemainingTimeLabel(self):
        remainingTimeTextWidth = int(screenWidth * 0.2)
        remainingTimeTextHeight = int(screenHeight * 0.1)
        
        remainingTimeIconWidth = int(screenWidth * 0.1)
        remainingTimeIconHeight = remainingTimeIconWidth
        remainingTimeIconPositionX = int(screenWidth * 0.5 - remainingTimeTextWidth // 2 - 25)
        remainingTimeIconPositionY = int(screenHeight * 0.2)
        
        self.remainingTimeIcon = QtWidgets.QLabel(self.centralwidget)
        self.remainingTimeIcon.setGeometry(QtCore.QRect(remainingTimeIconPositionX,
                                                        remainingTimeIconPositionY,
                                                        remainingTimeIconWidth,
                                                        remainingTimeIconHeight))
        self.remainingTimeIcon.setPixmap(QtGui.QPixmap(clockIconPath))
        self.remainingTimeIcon.setScaledContents(True)
        self.remainingTimeIcon.setObjectName("remainingTimeIcon")
        self.remainingTimeIcon.setStyleSheet("color: white;")
        
        remainingTimeTextPositionX = remainingTimeIconPositionX + remainingTimeIconWidth + 10
        remainingTimeTextPositionY = remainingTimeIconPositionY + remainingTimeIconHeight // 4
        
        self.remainingTimeText = QtWidgets.QLabel(self.centralwidget)
        self.remainingTimeText.setGeometry(QtCore.QRect(remainingTimeTextPositionX,
                                                        remainingTimeTextPositionY,
                                                        remainingTimeTextWidth,
                                                        remainingTimeTextHeight))
        self.remainingTimeText.setFont(self.valueFont)
        self.remainingTimeText.setObjectName("remainingTime")
        self.remainingTimeText.setText(self.remainingTimeValue.toString("mm:ss"))
        self.remainingTimeText.setStyleSheet("color: white;")
    
    def createBatteryLabel(self):
        batteryLevelBarWidth = int(screenWidth * 0.05)
        batteryLevelHeight = int(screenHeight * 0.05)
        batteryLevelBarPositionX = int(screenWidth * 0.05)
        batteryLevelBarPositionY = int(screenHeight * 0.2)
        
        self.batteryLevelBar = QtWidgets.QProgressBar(self.centralwidget)
        self.batteryLevelBar.setGeometry(QtCore.QRect(batteryLevelBarPositionX,
                                                      batteryLevelBarPositionY,
                                                      batteryLevelBarWidth,
                                                      batteryLevelHeight))
        self.batteryLevelBar.setProperty("value", self.batteryLevel)
        self.batteryLevelBar.setTextVisible(True)
        self.batteryLevelBar.setObjectName("progressBar")
        self.batteryLevelBar.setStyleSheet(
            "QProgressBar {"
            "   border: 2px solid #2196F3;"
            "   border-radius: 5px;"
            "   background-color: white;"
            "   text-align: center;"
            "}"
            "QProgressBar::chunk {"
            "   background-color: #00f200;"
            "   width: 10px; "
            "   margin: 0.5px;"
            "}"
            "QProgressBar::text {"
            "   color: white;"
            "   font-size: 12px;"
            "   font-weight: bold;"
            "}"
        )
        
        batteryIconWidth = int(screenWidth * 0.05)
        batteryIconHeight = int(screenHeight * 0.10)
        batteryIconPositionX = int(batteryLevelBarPositionX) + batteryLevelBarWidth + 10
        batteryIconPositionY = int(batteryLevelBarPositionY) - 10
        
        self.batteryLowIcon = QtWidgets.QLabel(self.centralwidget)
        self.batteryLowIcon.setGeometry(QtCore.QRect(batteryIconPositionX,
                                                    batteryIconPositionY,
                                                    batteryIconWidth,
                                                    batteryIconHeight))
        self.batteryLowIcon.setFont(self.valueFont)
        self.batteryLowIcon.setPixmap(QtGui.QPixmap(alertBatteryIconPath))
        self.batteryLowIcon.setScaledContents(True)
        self.batteryLowIcon.setObjectName("batteryIcon")
        self.batteryLowIcon.setHidden(True)

    def createDateTimeDisplay(self):
        dateTimeHeight = int(screenHeight * 0.1)
        dateTimeWidth = int(screenWidth * 0.3)
        dateTimePositionX = int((screenWidth - dateTimeWidth) // 2)
        dateTimePositionY = int(screenHeight * 0.80)
        
        self.dateTimeDisplay = QtWidgets.QLabel(self.centralwidget)
        self.dateTimeDisplay.setGeometry(QtCore.QRect(dateTimePositionX, dateTimePositionY, dateTimeWidth, dateTimeHeight)) 
        self.dateTimeDisplay.setFont(self.valueFont)
        self.dateTimeDisplay.setObjectName("dateTimeDisplay")
        self.dateTimeDisplay.setStyleSheet("color: white;")
        
        # Create a timer to update the current date and time
        self.timer = QtCore.QTimer(MainWindow)
        self.timer.timeout.connect(self.updateDateTime)
        self.timer.start(1000)  # Update every 1000 milliseconds (1 second)

    def createRightSignal(self):
        rightSignalPositionX = screenWidth * 0.90
        rightSignalPositionY = screenHeight * 0.05
        rightSignalWidth = 41
        rightSignalHeight = 41
        
        self.rightSignal = QtWidgets.QLabel(self.centralwidget)
        self.rightSignal.setGeometry(QtCore.QRect(int(rightSignalPositionX),
                                                  int(rightSignalPositionY),
                                                  rightSignalWidth,
                                                  rightSignalHeight))
        self.rightSignal.setPixmap(QtGui.QPixmap(directionIconPath))
        self.rightSignal.setScaledContents(True)
        self.rightSignal.setObjectName("rightSignal")
                
        self.timer = QtCore.QTimer(MainWindow)
        self.timer.timeout.connect(self.blinkRightSignalEveryHalfSecond)
        self.timer.start(500)

    def createLeftSignal(self):
        leftSignalPositionX = screenWidth * 0.05
        leftSignalPositionY = screenHeight * 0.05
        leftSignalWidth = 41
        leftSignalHeight = 41
         
        self.leftSignal = QtWidgets.QLabel(self.centralwidget)
        self.leftSignal.setGeometry(QtCore.QRect(int(leftSignalPositionX), int(leftSignalPositionY), leftSignalWidth, leftSignalHeight))
        self.leftSignal.setPixmap(QtGui.QPixmap(directionIconPath))
        self.leftSignal.setScaledContents(True)
        self.leftSignal.setObjectName("leftSignal")
        transform = QtGui.QTransform().rotate(180)
        rotated_pixmap = self.leftSignal.pixmap().transformed(transform, QtCore.Qt.SmoothTransformation)
        self.leftSignal.setPixmap(rotated_pixmap)
        
        self.timer = QTimer(MainWindow)
        self.timer.timeout.connect(self.blinkLeftSignalEveryHalfSecond)
        self.timer.start(500)
        
    def open_map_gui(self):
        
        if (self.mapWidget.isHidden() == False):
            self.mapWidget.setHidden(True)
            self.mapButton.setText("Map")
            return
        
        self.mapWidget.setHidden(False)
        # get map widget front of all widgets
        self.mapWidget.raise_()
        self.mapButton.raise_()
        self.mapButton.setText("Close")
        
    def update_map(self):
        self.mapWidget.update_map(float(GpsModule().get_latitude()), float(GpsModule().get_longitude()))

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.batteryLevelBar.setFormat(_translate("MainWindow", "%p%"))
        
    def updateSpeed(self):
        # Update the speed
        # if (self.speedWidget.value < 25):
        #     self.speedWidget.updateValue(self.speedWidget.value + 1)
        
        self.speedWidget.updateValue(float(GpsModule().get_speed()))
        
    def updateDateTime(self):
        # Update the QDateTimeEdit with the current date and time
        iana_id_bytes = QByteArray(b"Europe/Istanbul")

        # Get the current UTC date and time
        current_utc_datetime = QDateTime.currentDateTimeUtc()

        # Set the time zone to Turkey
        turkey_time_zone = QTimeZone(iana_id_bytes)
        current_turkey_datetime = QDateTime(current_utc_datetime)
        current_turkey_datetime.setTimeZone(turkey_time_zone)

        # self.dateTimeDisplay.setText(str(QDate.currentDate().toString("d/M/yyyy")) + " " + str(QTime.currentTime().toString("h:mm AP")))
        self.dateTimeDisplay.setText(current_turkey_datetime.toString("d/M/yyyy h:mm AP"))
  
    def updateBattery(self):
        # Update the battery level
        self.batteryLevel = getBatteryLevel(self.batteryLevel)
        self.batteryLevelBar.setValue(self.batteryLevel)
        
        if (self.batteryLevel < 25 and self.isBatteryBlinkStarted == False):
            self.isBatteryBlinkStarted = True
            self.batteryLowIcon.setHidden(False)

            self.blinkBattery()
        
        if (self.batteryLevel < 1):
            exit()
            
    def blinkBattery(self):
        # create time 0,5 seconds
        self.timer = QtCore.QTimer(MainWindow)
        self.timer.timeout.connect(self.blinkBatteryEveryHalfSecond)
        self.timer.start(500)
        
    def blinkBatteryEveryHalfSecond(self):
        if (self.batteryLowIcon.isHidden() == True):
            self.batteryLowIcon.setHidden(False)
        else :
            self.batteryLowIcon.setHidden(True)
        
    def updateRemainingTime(self):
        # Update the remaining time
        self.remainingTimeValue = self.remainingTimeValue.addSecs(-1)
        self.remainingTimeText.setText(self.remainingTimeValue.toString("mm:ss"))
        
        if (self.remainingTimeValue < QTime(0, 5, 0) and self.isBlinkStarted == False):
            self.isBlinkStarted = True
            self.blinkRemainingTime()

    def blinkRemainingTime(self):
        # create time 0,5 seconds
        self.timer = QtCore.QTimer(MainWindow)
        self.timer.timeout.connect(self.blinkRemainingTimeEveryHalfSecond)
        self.timer.start(500)
            
    def blinkRemainingTimeEveryHalfSecond(self):
        if (self.remainingTimeIcon.isHidden() == True):
            self.remainingTimeIcon.setHidden(False)
            self.remainingTimeText.setHidden(False)
        else :
            self.remainingTimeIcon.setHidden(True) 
            self.remainingTimeText.setHidden(True)  
        
    def updateTripDistance(self):
        # calculate trip distance using speed
        currentSpeed = self.speedWidget.value
        self.tripDistanceTotalValue = self.tripDistanceTotalValue + (((currentSpeed) / 60) / 60)
        self.tripDistanceText.setText(str(round(self.tripDistanceTotalValue, 1)) + " km")
        
    def blinkLeftSignalEveryHalfSecond(self):
        if (self.leftSignal.isHidden() == True):
            self.leftSignal.setHidden(False)
        else :
            self.leftSignal.setHidden(True)
            
    def blinkRightSignalEveryHalfSecond(self):
        if (self.rightSignal.isHidden() == True):
            self.rightSignal.setHidden(False)
        else :
            self.rightSignal.setHidden(True)
    
    def calculateAvgSpeed(self):
        currentSpeed = self.speedWidget.value
        self.avgSpeedValue = (self.avgSpeedValue + currentSpeed) / 2
        self.averageSpeedText.setText(str(round(self.avgSpeedValue, 1)))
        
    def blinkLed(self, led):
        if (led.isEnabled() == True):
            led.setStyleSheet("background-color: yellow; border-radius: 10px;")
            led.setEnabled(False)
        else:
            led.setStyleSheet("background-color: black; border-radius: 10px;")
            led.setEnabled(True)
   
def getBatteryLevel(batteryLevel):
    # first get battery level 
    # use dummy value for now
    # decrement battery level by 1
    return batteryLevel - 1

def run_gps_module():
    gps_instance = GpsModule()  # Instantiate a new instance of GpsModule
    gps_instance.run_sim808(_useRealData)

class StartScreen(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Start Screen')
        self.showFullScreen()
        self.resize(screenWidth, screenHeight)
        self.setCursor(Qt.BlankCursor)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        
        layout = QtWidgets.QGridLayout()
        
        title_label = QtWidgets.QLabel('Enter The Bike Id')
        title_label.setStyleSheet("color: white; font-family: Arial; font-size: 35px")
        title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        bike_id_edit = QtWidgets.QLineEdit()
        bike_id_edit.setStyleSheet("font-family: Arial; font-size: 20px")
        # set input center
        bike_id_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        start_button = QtWidgets.QPushButton('Start')
        start_button.setStyleSheet("font-family: Arial; font-size: 20px")
        start_button.clicked.connect(self.start_gui)
        bike_id_edit.returnPressed.connect(start_button.click)

        
        # Add widgets to the grid layout at specific row and column positions
        layout.addWidget(title_label, 25, 17, 2, 1)
        layout.addWidget(bike_id_edit, 53, 15, 5, 5) 
        layout.addWidget(start_button, 55, 17, 5, 1)  
        
        # Set distance between widgets
        layout.setSpacing(0)
        layout.setContentsMargins(200, 200, 200, 200)
        
        self.setLayout(layout)

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QtGui.QColor(50, 50, 50))
        self.setPalette(p)

    def start_gui(self):
        ui = Ui_MainWindow()
        ui.setupUi(MainWindow)
        MainWindow.showFullScreen()
        # wait 10 seconds then hide this widget
        QtCore.QTimer.singleShot(1000, self.close)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <arg1> <arg2>")
        print("arg1: _useRealData, arg2: _useMap")
        sys.exit(1)
    
    _useRealData = sys.argv[1].lower() == 'true'
    _useMap = sys.argv[2].lower() == 'true'
    
    app = QtWidgets.QApplication(sys.argv)
    
    gps_thread = Thread(target=run_gps_module)
    gps_thread.daemon = True
    gps_thread.start()
    
    MainWindow = QtWidgets.QMainWindow()
    
    start_screen = StartScreen()
    # MainWindow.show()
    sys.exit(app.exec_())
