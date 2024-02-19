from PyQt5 import QtCore, QtGui, QtWidgets
from Helper.AnalogGaugeWidget import AnalogGaugeWidget
from PyQt5.QtGui import QFont, QFontDatabase, QColor
from PyQt5.QtCore import QTimer, QTime, QDateTime, QTimeZone, QByteArray
import os
from sim808_reader import GpsModule
from threading import Thread
from mapGui import MapWidget

folderPath = os.path.dirname(os.path.abspath(__file__))
iconPath = folderPath + "//Icons"
fontPath  = folderPath + "//Fonts"
backGroundImagePath = iconPath + "//background_4.jpg"

alertBatteryIconPath = iconPath + "//alertBattery2.png"
directionIconPath = iconPath + "//directionIcon.png"
clock4IconPath = iconPath + "//clock_4.png"
averageSpeedBackgroundIconPath = iconPath + "//blue.png"

companyNameStr = "HIGHTECHMOBI Bisiklet Teknolojileri LTD.ŞTİ."
brandNameStr = "QuadSmart"

class Ui_MainWindow(object):

    batteryLevel = 15
    
    remainingTimeValue = QTime(0, 5, 20) # 5 minutes 20 seconds
    screenWidth = 480
    screenHeight = 320
    
    isBlinkStarted = False
    isBatteryBlinkStarted = False
    ledOn = False
    
    tripDistanceTotalValue = 0
    avgSpeedValue = 0
    voltageValue = 36

    
    def setupUi(self, MainWindow):
        
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(480, 320)
        MainWindow.showFullScreen()
        # MainWindow.setCursor(Qt.BlankCursor)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setMouseTracking(False);
        
        myFontName = "RifficFree-Bold"
        myFontsPath = "//riffic"
        fullFontName =  myFontsPath + "//" + myFontName + ".ttf"

        fontId = QFontDatabase.addApplicationFont(fontPath + fullFontName)
        if fontId < 0:
            print('font not loaded')
                        
        families = QtGui.QFontDatabase.applicationFontFamilies(fontId)
        valueFont = QFont(families[0])
        headerFont = QFont(families[0])
        
        headerFont.setPointSize(10)
        valueFont.setPointSize(18)
        
        self.background = QtWidgets.QLabel(self.centralwidget)
        self.background.setGeometry(QtCore.QRect(0, 0, 480, 320))
        self.background.setPixmap(QtGui.QPixmap(backGroundImagePath))
        self.background.setScaledContents(True)
        self.background.setObjectName("background")
        
        self.mapButton = QtWidgets.QPushButton("Map", self.centralwidget)
        self.mapButton.setGeometry(340, int(self.screenHeight * 0.05), 45, 30) 
        self.mapButton.setFont(headerFont)
        self.mapButton.clicked.connect(self.open_map_gui)
        
        self.mapWidget = MapWidget(self.centralwidget)
        self.mapWidget.setGeometry(QtCore.QRect(0, 0, 480, 320))
        self.mapWidget.setObjectName("mapWidget")
        self.mapWidget.setHidden(True)
        
        self.timer = QtCore.QTimer(MainWindow)
        self.timer.timeout.connect(self.update_map)
        self.timer.start(2000)
        
        self.leftSignal = QtWidgets.QLabel(self.centralwidget)
        self.leftSignal.setGeometry(QtCore.QRect(20, 10, 41, 41))
        self.leftSignal.setPixmap(QtGui.QPixmap(directionIconPath))
        self.leftSignal.setScaledContents(True)
        self.leftSignal.setObjectName("leftSignal")
        transform = QtGui.QTransform().rotate(180)
        rotated_pixmap = self.leftSignal.pixmap().transformed(transform, QtCore.Qt.SmoothTransformation)
        self.leftSignal.setPixmap(rotated_pixmap)
        
        self.timer = QTimer(MainWindow)
        self.timer.timeout.connect(self.blinkLeftSignalEveryHalfSecond)
        self.timer.start(500)
        
        self.rightSignal = QtWidgets.QLabel(self.centralwidget)
        self.rightSignal.setGeometry(QtCore.QRect(420, 10, 41, 41))
        self.rightSignal.setPixmap(QtGui.QPixmap(directionIconPath))
        self.rightSignal.setScaledContents(True)
        self.rightSignal.setObjectName("rightSignal")
        
        # blink every half second
        self.timer = QtCore.QTimer(MainWindow)
        self.timer.timeout.connect(self.blinkRightSignalEveryHalfSecond)
        self.timer.start(500)
        
        dateTimeHeight = 35
        dateTimeWidth = 240
        dateTimePositionX = int((self.screenWidth - dateTimeWidth) // 2)
        dateTimePositionY = int(self.screenHeight * 0.80)

        
        # self.dateTimeDisplay = QtWidgets.QDateTimeEdit(self.centralwidget)
        self.dateTimeDisplay = QtWidgets.QLabel(self.centralwidget)
        self.dateTimeDisplay.setGeometry(QtCore.QRect(dateTimePositionX, dateTimePositionY, dateTimeWidth, dateTimeHeight)) 
        self.dateTimeDisplay.setFont(valueFont)
        self.dateTimeDisplay.setObjectName("dateTimeDisplay")
        self.dateTimeDisplay.setStyleSheet("color: white;")
        
        available_time_zones = QTimeZone.availableTimeZoneIds()

        # Specify the file path where you want to write the time zone identifiers
        file_path = 'time_zones.txt'

        # Write the time zone identifiers to the file
        with open(file_path, 'w') as file:
            for time_zone_id in available_time_zones:
                zoneId = str(time_zone_id) + '\n'
                file.write(zoneId)
        
        # # Create a timer to update the current date and time
        self.timer = QtCore.QTimer(MainWindow)
        self.timer.timeout.connect(self.updateDateTime)
        self.timer.start(1000)  # Update every 1000 milliseconds (1 second)
        
        # update battery level every 30 second
        self.timer = QtCore.QTimer(MainWindow)
        self.timer.timeout.connect(self.updateBattery)
        self.timer.start(15000)
        
        batteryLevelBarPositionX = 20
        batteryLevelBarPositionY = 20
        
        self.batteryLevelBar = QtWidgets.QProgressBar(self.centralwidget)
        self.batteryLevelBar.setGeometry(QtCore.QRect(batteryLevelBarPositionX, batteryLevelBarPositionY + 40, 50, 21))
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
        
        self.batteryIcon = QtWidgets.QLabel(self.centralwidget)
        self.batteryIcon.setGeometry(QtCore.QRect(batteryLevelBarPositionX + 0, 95, 40, 40))
        self.batteryIcon.setFont(valueFont)
        self.batteryIcon.setPixmap(QtGui.QPixmap(alertBatteryIconPath))
        self.batteryIcon.setScaledContents(True)
        self.batteryIcon.setObjectName("batteryIcon")
        self.batteryIcon.setHidden(True)
        
        remainingTimePositionX = batteryLevelBarPositionX + 150
        remainingTimePositionY = batteryLevelBarPositionY + 40
        
        self.remainingTimeIcon = QtWidgets.QLabel(self.centralwidget)
        self.remainingTimeIcon.setGeometry(QtCore.QRect(remainingTimePositionX, remainingTimePositionY, 41, 41))
        self.remainingTimeIcon.setPixmap(QtGui.QPixmap(clock4IconPath))
        self.remainingTimeIcon.setScaledContents(True)
        self.remainingTimeIcon.setObjectName("remainingTimeIcon")
        self.remainingTimeIcon.setStyleSheet("color: white;")
        
        self.remainingTimeText = QtWidgets.QLabel(self.centralwidget)
        self.remainingTimeText.setGeometry(QtCore.QRect(remainingTimePositionX + 50, remainingTimePositionY + 10, 75, 25))
        self.remainingTimeText.setFont(valueFont)
        self.remainingTimeText.setObjectName("remainingTime")
        self.remainingTimeText.setText(self.remainingTimeValue.toString("mm:ss"))
        self.remainingTimeText.setStyleSheet("color: white;")
        
        # update remaining time every 1 second
        self.timer = QtCore.QTimer(MainWindow)
        self.timer.timeout.connect(self.updateRemainingTime)
        self.timer.start(1000)
        
        # add average speed
        averageSpeedPositionX = remainingTimePositionX - 50
        averageSpeedPositionY = remainingTimePositionY + 80
        
        self.averageSpeedBackground = QtWidgets.QLabel(self.centralwidget)
        self.averageSpeedBackground.setGeometry(QtCore.QRect(averageSpeedPositionX, averageSpeedPositionY, 90, 90))
        self.averageSpeedBackground.setObjectName("averageSpeedBackground")
        self.averageSpeedBackground.setPixmap(QtGui.QPixmap(averageSpeedBackgroundIconPath))
        self.averageSpeedBackground.setScaledContents(True)
        
        self.averageSpeedHeader = QtWidgets.QLabel(self.centralwidget)
        self.averageSpeedHeader.setGeometry(QtCore.QRect(averageSpeedPositionX + 20, averageSpeedPositionY + 10, 80, 25))
        self.averageSpeedHeader.setObjectName("averageSpeed")
        self.averageSpeedHeader.setText("Ort Hız")
        self.averageSpeedHeader.setFont(headerFont)
        self.averageSpeedHeader.setStyleSheet("color: white;")
        
        self.averageSpeedText = QtWidgets.QLabel(self.centralwidget)
        self.averageSpeedText.setGeometry(QtCore.QRect(averageSpeedPositionX + 25, averageSpeedPositionY + 40, 250, 25))
        self.averageSpeedText.setObjectName("averageSpeed")
        self.averageSpeedText.setText(str(self.avgSpeedValue))
        self.averageSpeedText.setFont(valueFont)
        self.averageSpeedText.setStyleSheet("color: white;")

        # add trip distance
        tripDistancePositionX = averageSpeedPositionX + 100
        tripDistancePositionY = averageSpeedPositionY
        
        self.tripDistanceBackground = QtWidgets.QLabel(self.centralwidget)
        self.tripDistanceBackground.setGeometry(QtCore.QRect(tripDistancePositionX, tripDistancePositionY, 90, 90))
        self.tripDistanceBackground.setPixmap(QtGui.QPixmap(averageSpeedBackgroundIconPath))
        self.tripDistanceBackground.setObjectName("tripDistanceBackground")
        self.tripDistanceBackground.setScaledContents(True)
        
        self.tripDistanceHeader = QtWidgets.QLabel(self.centralwidget)
        self.tripDistanceHeader.setGeometry(QtCore.QRect(tripDistancePositionX + 20, tripDistancePositionY + 10, 80, 25))
        self.tripDistanceHeader.setFont(headerFont)
        self.tripDistanceHeader.setObjectName("tripDistanceTitle")
        self.tripDistanceHeader.setText("Yolculuk")
        self.tripDistanceHeader.setStyleSheet("color: white;")
        
        self.tripDistanceText = QtWidgets.QLabel(self.centralwidget)
        self.tripDistanceText.setGeometry(QtCore.QRect(tripDistancePositionX + 5, tripDistancePositionY + 40, 80, 25))
        self.tripDistanceText.setFont(valueFont)
        self.tripDistanceText.setObjectName("tripDistance")
        self.tripDistanceText.setText(str(self.tripDistanceTotalValue)  + " km")
        self.tripDistanceText.setStyleSheet("color: white;")
        
        # update trip distance every 1 second
        self.timer = QtCore.QTimer(MainWindow)
        self.timer.timeout.connect(self.updateTripDistance)
        self.timer.start(1000)
        
        companyNameFont = QFont()
        companyNameFont.setFamily(myFontName)
        companyNameFont.setPointSize(7)
        
        companyNameTextWidth = 200
        companyNameTextHeight = 35
        
        self.companyNameText = QtWidgets.QLabel(self.centralwidget)
        self.companyNameText.setGeometry(QtCore.QRect(int((self.screenWidth - companyNameTextWidth) // 2), int(self.screenHeight * 0.9), companyNameTextWidth, companyNameTextHeight))
        self.companyNameText.setFont(companyNameFont)
        self.companyNameText.setObjectName("companyName")
        self.companyNameText.setText(companyNameStr)
        self.companyNameText.setStyleSheet("color: #DDDDDD;")
        
        brandNameFont = QFont()
        brandNameFont.setFamily(myFontName)
        brandNameFont.setPointSize(13)
        
        brandNameTextWidth = 120
        brandNameTextHeight = 35
        
        self.brandName = QtWidgets.QLabel(self.centralwidget)
        self.brandName.setGeometry(QtCore.QRect(int((self.screenWidth - brandNameTextWidth) // 2), int(self.screenHeight * 0.05), brandNameTextWidth, brandNameTextHeight))
        self.brandName.setFont(valueFont)
        self.brandName.setObjectName("brandName")
        self.brandName.setText(brandNameStr)
        self.brandName.setStyleSheet("color: #DDDDDD;")
        
        led_labels_position_x = 20
        led_labels_position_y = 150
        
        self.led_label1 = QtWidgets.QLabel(self.centralwidget)
        self.led_label1.setGeometry(QtCore.QRect(led_labels_position_x, led_labels_position_y, 40, 20))
        self.led_label1.setObjectName("led_label1")
        self.led_label1.setStyleSheet("background-color: yellow; border-radius: 10px;")
        
        self.led_label2 = QtWidgets.QLabel(self.centralwidget)
        self.led_label2.setGeometry(QtCore.QRect(led_labels_position_x, led_labels_position_y + 30, 40, 20))
        self.led_label2.setObjectName("led_label2")
        self.led_label2.setStyleSheet("background-color: yellow; border-radius: 10px;")
        
        self.led_label3 = QtWidgets.QLabel(self.centralwidget)
        self.led_label3.setGeometry(QtCore.QRect(led_labels_position_x, led_labels_position_y + 60, 40, 20))
        self.led_label3.setObjectName("led_label3")
        self.led_label3.setStyleSheet("background-color: yellow; border-radius: 10px;")
        
        self.led_label4 = QtWidgets.QLabel(self.centralwidget)
        self.led_label4.setGeometry(QtCore.QRect(led_labels_position_x, led_labels_position_y + 90, 40, 20))
        self.led_label4.setObjectName("led_label4")
        self.led_label4.setStyleSheet("background-color: yellow; border-radius: 10px;")
                
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
        
        voltageWidgetWidth = 90
        voltageWidgetHeight = 30
        voltageWidgetPositionX = int((self.screenWidth - voltageWidgetWidth) * 0.04)
        voltageWidgetPositionY = int(self.screenHeight * 0.85)
        
        self.voltageWidget = QtWidgets.QLabel(self.centralwidget)
        self.voltageWidget.setGeometry(QtCore.QRect(voltageWidgetPositionX, voltageWidgetPositionY, voltageWidgetWidth, voltageWidgetHeight))
        self.voltageWidget.setObjectName("widget")
        self.voltageWidget.setText("voltage : " + str(self.voltageValue) + " V")
        self.voltageWidget.setFont(headerFont)
        self.voltageWidget.setStyleSheet("color: white;")
        
        self.speedWidget = AnalogGaugeWidget(self.centralwidget)
        self.speedWidget.setGeometry(QtCore.QRect(300, 60, 282, 210))
        self.speedWidget.setObjectName("speedWidget")
        self.speedWidget.setMaxValue(50)
        self.speedWidget.updateValue(1)
        
        # timer : calculate average speed 
        self.timer = QtCore.QTimer(MainWindow)
        self.timer.timeout.connect(self.calculateAvgSpeed)
        self.timer.start(1000)
        
        # update speed
        self.timer = QtCore.QTimer(MainWindow)
        self.timer.timeout.connect(self.updateSpeed)
        self.timer.start(1000)
        
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
    
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
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
            self.batteryIcon.setHidden(False)

            self.blinkBattery()
        
        if (self.batteryLevel < 1):
            exit()
            
    def blinkBattery(self):
        # create time 0,5 seconds
        self.timer = QtCore.QTimer(MainWindow)
        self.timer.timeout.connect(self.blinkBatteryEveryHalfSecond)
        self.timer.start(500)
        
    def blinkBatteryEveryHalfSecond(self):
        if (self.batteryIcon.isHidden() == True):
            self.batteryIcon.setHidden(False)
        else :
            self.batteryIcon.setHidden(True)
        
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
    gps_instance.run_sim808()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    
    gps_thread = Thread(target=run_gps_module)
    gps_thread.daemon = True
    gps_thread.start()
    
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
