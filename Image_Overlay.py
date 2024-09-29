import sys
from PyQt5.QtWidgets import QApplication, QLabel, QSlider, QVBoxLayout, QWidget, QFileDialog, QPushButton
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPixmap, QImage
from PIL import Image

class ImageOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def close_program(self):
        self.close()

    def initUI(self):
        self.setWindowTitle('Image Overlay with Transparency and Resize Control')
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout()

        # Label to display image
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)

        # Slider to control transparency
        self.slider_transparency = QSlider(Qt.Horizontal, self)
        self.slider_transparency.setMinimum(0)
        self.slider_transparency.setMaximum(100)
        self.slider_transparency.setValue(100)
        self.slider_transparency.valueChanged.connect(self.changeTransparency)

        # Slider to control image size
        self.slider_size = QSlider(Qt.Horizontal, self)
        self.slider_size.setMinimum(10)
        self.slider_size.setMaximum(200)
        self.slider_size.setValue(100)
        self.slider_size.valueChanged.connect(self.changeSize)

        # Button to load image
        self.load_btn = QPushButton('Load Image', self)
        self.load_btn.clicked.connect(self.loadImage)

        # Button to close the program
        self.close_button = QPushButton('Close', self)
        self.close_button.clicked.connect(self.close_program)

        # Add widgets to layout
        layout.addWidget(self.label)
        layout.addWidget(self.slider_transparency)
        layout.addWidget(self.slider_size)
        layout.addWidget(self.load_btn)
        self.setLayout(layout)
        layout.addWidget(self.close_button)  # Add close button to layout

        # Store the original image and its size
        self.image = None
        self.original_image = None
        self.image_size_factor = 1.0
        self.drag_position = QPoint(0, 0)
        self.is_dragging = False  # To track dragging state

    def loadImage(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select an Image", "", "Image Files (*.png *.jpg *.bmp)", options=options)
        if file_path:
            self.original_image = Image.open(file_path).convert("RGBA")
            self.image = self.original_image.copy()
            self.updateImage()

    def updateImage(self):
        if self.image:
            width, height = self.image.size
            self.resize(width, height)
            qimage = QImage(self.image.tobytes(), width, height, QImage.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimage)
            self.label.setPixmap(pixmap)

    def changeTransparency(self, value):
        if self.image:
            transparency = value / 100.0
            image = self.original_image.copy()

            for y in range(image.height):
                for x in range(image.width):
                    r, g, b, a = image.getpixel((x, y))
                    image.putpixel((x, y), (r, g, b, int(a * transparency)))

            self.image = image.resize((int(self.original_image.width * self.image_size_factor), 
                                       int(self.original_image.height * self.image_size_factor)))
            self.updateImage()

    def changeSize(self, value):
        if self.original_image:
            self.image_size_factor = value / 100.0
            self.image = self.original_image.resize((int(self.original_image.width * self.image_size_factor), 
                                                     int(self.original_image.height * self.image_size_factor)))
            self.updateImage()

    # Override mouse events for dragging functionality
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self.is_dragging = True
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            event.accept()

def main():
    app = QApplication(sys.argv)
    window = ImageOverlay()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
