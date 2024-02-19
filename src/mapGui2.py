import io
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QVBoxLayout, QWidget
import folium

class MapWidget(QWidget):
    def __init__(self, parent=None):
        super(MapWidget, self).__init__(parent)
        
        latitude = 41.5
        longitude = 26.2

        self.layout = QVBoxLayout(self)
        self.map = folium.Map(location=[latitude, longitude], zoom_start=14)
        self.marker = folium.Marker([latitude, longitude], popup='Current Location', tooltip='Click for more info')
        self.marker.add_to(self.map)
        
        self.data = io.BytesIO()
        self.map.save(self.data, close_file=False)

        self.web_view = QWebEngineView(self)
        self.web_view.setHtml(self.data.getvalue().decode())

        # Set the size of the QWebEngineView
        self.web_view.setFixedSize(480, 320)

        self.layout.addWidget(self.web_view)
        
    # def update_map(self, latitude, longitude):
    #     # Update marker's position
    #     self.marker.location = [latitude, longitude]
        
    #     # Save the updated map as HTML
    #     self.data.seek(0)
    #     self.data.truncate()
    #     self.map.save(self.data, close_file=False)
        
    #     # Load the updated HTML content into QWebEngineView
    #     self.web_view.setHtml(self.data.getvalue().decode())
        
    def update_map(self, _latitude, _longitude):
        self.map = folium.Map(location=[_latitude, _longitude], zoom_start=12)
        self.marker = folium.Marker([_latitude, _longitude], popup='Current Location', tooltip='Click for more info')
        
        self.marker.add_to(self.map)
        self.data = io.BytesIO()
        
        self.map.save(self.data, close_file=False)
        self.web_view.setHtml(self.data.getvalue().decode())

    # def update_map(self, _latitude, _longitude):
    #     # Create a copy of the keys before iterating over them
    #     children_keys = list(self.map._children.keys())
        
    #     # Clear existing markers from the map
    #     for child_key in children_keys:
    #         self.map._children.pop(child_key)

    #     # Create a new marker with the updated location
    #     self.marker = folium.Marker([_latitude, _longitude], popup='Current Location', tooltip='Click for more info')
    #     self.marker.add_to(self.map)
        
    #     # Save the map to a BytesIO object
    #     self.data = io.BytesIO()
    #     self.map.save(self.data, close_file=False)
        
    #     # Update the QWebEngineView content
    #     self.web_view.setHtml(self.data.getvalue().decode())



if __name__ == "__main__":
    # Replace these with actual latitude and longitude values from your GPS data
    current_latitude = 40.998330
    current_longitude = 28.653713
