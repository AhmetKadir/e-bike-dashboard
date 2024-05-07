from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
import folium
import io

screenWidth = 1024
screenHeight = 600

class MapWidget(QWidget):
    def __init__(self, parent=None):
        super(MapWidget, self).__init__(parent)
        
        latitude = 41.5
        longitude = 26.2

        self.layout = QVBoxLayout(self)

        # First map widget
        self.web_view_1 = QWebEngineView(self)

        # Second map widget (hidden)
        self.web_view_2 = QWebEngineView(self)
        self.web_view_2.hide()

        # Create initial map
        self.map = folium.Map(location=[latitude, longitude], zoom_start=15)
        self.marker = folium.Marker([latitude, longitude], popup='Current Location', tooltip='Click for more info')
        self.marker.add_to(self.map)
        self.data = io.BytesIO()
        self.map.save(self.data, close_file=False)
        self.web_view_1.setHtml(self.data.getvalue().decode())

        # Set the size of the QWebEngineViews
        self.web_view_1.setFixedSize(screenWidth, screenHeight)
        self.web_view_2.setFixedSize(screenWidth, screenHeight)
        
        self.layout.addWidget(self.web_view_1)
        self.layout.addWidget(self.web_view_2)
        
    def update_map(self, _latitude, _longitude):
        self.web_view_2.show()
        self.web_view_1.hide()
        
        self.map = folium.Map(location=[_latitude, _longitude], zoom_start=15)
        self.marker = folium.Marker([_latitude, _longitude], popup='Current Location', tooltip='Click for more info')
        self.marker.add_to(self.map)
        self.data = io.BytesIO()
        self.map.save(self.data, close_file=False)
        
        
        self.web_view_1.setHtml(self.data.getvalue().decode())
        
        self.web_view_1.show()
        self.web_view_2.hide()
