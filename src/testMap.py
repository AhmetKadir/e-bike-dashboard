# %%

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebChannel import QWebChannelAbstractTransport
import folium
import time

class MapWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Folium Map in PyQt5")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        self.webview = QWebEngineView()
        layout.addWidget(self.webview)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.setupMap()

    def setupMap(self):
        # Create a Folium map with initial location
        self.map = folium.Map(location=[51.5074, -0.1278], zoom_start=10)
        self.map.save("map.html")
        self.webview.load(QUrl.fromLocalFile("map.html"))

        # Connect the web channel
        self.channel = QWebChannel()
        self.channel.registerObject("MapWidget", self)
        self.webview.page().setWebChannel(self.channel)

    def updateMap(self):
        # Example code to update location (replace with your own logic)
        # For demonstration purposes, it updates the location randomly within London area
        lat = 51.5074 + (0.01 * (2 * (time.time() % 100) - 100))
        lon = -0.1278 + (0.01 * (2 * (time.time() % 100) - 100))

        # Call JavaScript function to update map location
        js_script = f"updateMapLocation({lat}, {lon})"
        self.webview.page().runJavaScript(js_script)

        # Schedule the next update after 2 seconds
        QTimer.singleShot(2000, self.updateMap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapWidget()
    window.show()
    sys.exit(app.exec_())
