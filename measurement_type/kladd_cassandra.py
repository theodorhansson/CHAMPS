
import sys
import time
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QImage, QColor, QPainter
from pylablib.devices import Andor

N_peaks = 4


# -------------------------- ANALYSIS FUNCTIONS -------------------------------

def find_brightest_horizontal_line(img, window_width=100, threshold_ratio=0.5):
    """
    Finds the brightest horizontal line in the image and returns the row and left/right edges.
    """
    row_sums = img.sum(axis=1)
    brightest_row = np.argmax(row_sums)

    stripe = img[brightest_row, :]
    smooth = np.convolve(stripe, np.ones(window_width)/window_width, mode='same')
    threshold = smooth.max() * threshold_ratio
    bright_indices = np.where(smooth > threshold)[0]

    if bright_indices.size > 0:
        left_edge = bright_indices[0]
        right_edge = bright_indices[-1]
    else:
        left_edge = right_edge = 0

    return brightest_row, left_edge, right_edge


# Placeholder for future SPR dip analysis
def find_spr_dip(img, roi=None):
    # TODO: implement SPR dip detection
    return None



def find_brightest_horizontal_lines(img, num_peaks=1, window_width=100, threshold_ratio=0.5, min_distance=50):
    """
    Finds the N brightest horizontal lines (rows) in the image.
    Returns a list of tuples: [(row, left_edge, right_edge), ...]
    """
    row_sums = img.sum(axis=1)
    
    # Find the N brightest rows, ensuring they’re not too close together
    sorted_indices = np.argsort(row_sums)[::-1]
    peaks = []
    for idx in sorted_indices:
        if all(abs(idx - p[0]) > min_distance for p in peaks):  # avoid duplicates
            stripe = img[idx, :]
            smooth = np.convolve(stripe, np.ones(window_width)/window_width, mode='same')
            threshold = smooth.max() * threshold_ratio
            bright_indices = np.where(smooth > threshold)[0]
            if bright_indices.size > 0:
                left_edge = bright_indices[0]
                right_edge = bright_indices[-1]
                peaks.append((idx, left_edge, right_edge))
            if len(peaks) >= num_peaks:
                break

    return peaks



# ---------------------------- GUI CLASS -------------------------------------

class CameraGUI(QMainWindow):
    def __init__(self, camera_idx=0, exposure_time=0.01, update_interval_ms=100):
        super().__init__()
        self.setWindowTitle("Live Camera Viewer")
        self.resize(1000, 1000)
        self.camera_idx = camera_idx
        self.exposure_time = exposure_time
        self.update_interval_ms = update_interval_ms

        # Layout
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setScaledContents(True)
        self.setFixedSize(1000, 1000)

        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Signals
        self.start_button.clicked.connect(self.start_camera)
        self.stop_button.clicked.connect(self.stop_camera)

        # Timer for updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # Camera object
        self.cam = None

    def start_camera(self):
        try:
            self.cam = Andor.AndorSDK3Camera(idx=self.camera_idx)
            self.cam.set_exposure(self.exposure_time)
            self.cam.set_roi(0, 2048, 0, 2048, hbin=2, vbin=2)
            self.cam.start_acquisition()  # if needed
        except Exception as e:
            print("Error opening camera:", e)
            return

        self.timer.start(self.update_interval_ms)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_camera(self):
        self.timer.stop()
        if self.cam is not None:
            try:
                self.cam.close()
            except:
                pass
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def update_frame(self):
        if self.cam is None:
            return

        try:
            img_array = self.cam.grab(1)[0]
        except Exception as e:
            print("Error grabbing frame:", e)
            self.stop_camera()
            return

        # Convert to QImage
        img_array_8bit = np.clip(img_array / img_array.max() * 255, 0, 255).astype(np.uint8)
        height, width = img_array_8bit.shape
        qimg = QImage(img_array_8bit.data, width, height, width, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimg)

        peaks = find_brightest_horizontal_lines(img_array_8bit, num_peaks=N_peaks, window_width=100)

        painter = QPainter(pixmap)
        for row, left, right in peaks:
            # Center line (red)
            painter.setPen(QColor(255, 0, 0))
            painter.drawLine(left, row, right, row)
        
            # Edges (green)
            half_width = 15
            top_row = max(0, row - half_width)
            bottom_row = min(img_array_8bit.shape[0] - 1, row + half_width)
            painter.setPen(QColor(0, 255, 0))
            painter.drawLine(left, top_row, right, top_row)
            painter.drawLine(left, bottom_row, right, bottom_row)

        
        painter.end()


        self.label.setPixmap(pixmap)


# --------------------------- MAIN FUNCTION -----------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = CameraGUI(camera_idx=0, exposure_time=0.01, update_interval_ms=100)
    gui.show()
    sys.exit(app.exec())

