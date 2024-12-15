import sys
import open3d as o3d
import numpy as np
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QSplitter,
    QPushButton,
    QFrame,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QVector3D
from PyQt5.QtGui import QPixmap
from ZEDCamera import ZEDCameraThread
import pyqtgraph.opengl as gl

class EnhancedMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced GUI with Open3D")
        self.setGeometry(100, 100, 1600, 900)
        self.showMaximized()

        # Main widget and layout
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        # Initialize top control panel and main content
        self.init_top_control_panel()
        self.init_main_content()

        # Initialize ZED camera thread
        self.camera_thread = ZEDCameraThread()
        self.camera_thread.image_signal.connect(self.update_camera_display)
        self.camera_thread.depth_signal.connect(self.update_depth_display)
        self.camera_thread.point_cloud_signal.connect(self.update_point_cloud_display)
        self.camera_running = False  # Kamera başlangıçta kapalı

        self.camera_selector.currentTextChanged.connect(self.camera_selection_changed)
        self.depth_option_selector.currentTextChanged.connect(self.depth_selection_changed)

    def init_top_control_panel(self):
        """Initialize the top control panel with a toggle button, two combo boxes and a save button."""
        self.control_panel = QFrame()
        self.control_panel.setStyleSheet(
            "background-color: #1c1c1c; border-bottom: 2px solid #444;"
        )
        self.control_layout = QHBoxLayout()
        self.control_panel.setLayout(self.control_layout)

        # Bağlan/Kopar düğmesi
        self.toggle_button = QPushButton("Disconnected")
        self.toggle_button.setStyleSheet(
            "padding: 10px; color: #ffffff; background-color: #DC3545; border: none; font-size: 14px;"
        )
        self.toggle_button.clicked.connect(self.toggle_camera)
        self.control_layout.addWidget(self.toggle_button)

        # Birinci ComboBox
        self.combo_box_1 = QComboBox()
        self.combo_box_1.addItems(["Option 1", "Option 2", "Option 3"])
        self.combo_box_1.setStyleSheet(
            "padding: 5px; color: #ffffff; background-color: #333;"
        )
        self.combo_box_1.currentTextChanged.connect(self.on_combo_box_1_changed)
        self.control_layout.addWidget(self.combo_box_1)

        # İkinci ComboBox
        self.combo_box_2 = QComboBox()
        self.combo_box_2.addItems(["Option A", "Option B", "Option C"])
        self.combo_box_2.setStyleSheet(
            "padding: 5px; color: #ffffff; background-color: #333;"
        )
        self.combo_box_2.currentTextChanged.connect(self.on_combo_box_2_changed)
        self.control_layout.addWidget(self.combo_box_2)

        # Kaydet Butonu
        self.save_button = QPushButton("Save")
        self.save_button.setStyleSheet(
            "padding: 10px; color: #ffffff; background-color: #007BFF; border: none; font-size: 14px;"
        )
        self.save_button.clicked.connect(self.on_save_button_clicked)
        self.control_layout.addWidget(self.save_button)

        self.main_layout.addWidget(self.control_panel)

    def on_combo_box_1_changed(self, text):
        """Birinci ComboBox'un değeri değiştiğinde yapılacak işlemler."""
        print("Combo Box 1 seçimi değişti:", text)
        # Buraya metni kullanarak gerekli mantığı ekleyebilirsiniz.

    def on_combo_box_2_changed(self, text):
        """İkinci ComboBox'un değeri değiştiğinde yapılacak işlemler."""
        print("Combo Box 2 seçimi değişti:", text)
        # Buraya metni kullanarak gerekli mantığı ekleyebilirsiniz.

    def on_save_button_clicked(self):
        """Save butonuna tıklandığında yapılacak işlemler."""
        print("Save butonuna tıklandı.")
        # Burada seçimleri bir dosyaya kaydetme veya başka bir işlem gerçekleştirebilirsiniz.


    def init_main_content(self):
        """Initialize the main content with left panel and 3D point cloud display."""
        self.content_layout = QHBoxLayout()

        # Initialize left panel
        self.init_left_panel()

        # Initialize point cloud widget
        self.init_point_cloud_widget()

        self.content_layout.addWidget(self.left_splitter)
        self.content_layout.addWidget(self.gl_widget)
        self.content_layout.setStretch(0, 2)
        self.content_layout.setStretch(1, 3)

        self.main_layout.addLayout(self.content_layout)

    def init_left_panel(self):
        """Initialize the left panel with camera and option selectors."""
        self.left_splitter = QSplitter(Qt.Vertical)
        self.left_splitter.setChildrenCollapsible(False)

        # Camera Selection Section
        self.camera_selection_widget = QWidget()
        self.camera_selection_layout = QVBoxLayout()
        self.camera_selection_widget.setLayout(self.camera_selection_layout)
        self.camera_selection_widget.setStyleSheet(
            "background-color: #1c1c1c; border: 1px solid #444; padding: 10px;"
        )

        camera_row_layout = QHBoxLayout()
        camera_label = QLabel("Camera:")
        camera_label.setStyleSheet("color: #ffffff; font-size: 12px; margin-right: 10px;")
        self.camera_selector = QComboBox()
        self.camera_selector.addItems(["Left Camera", "Right Camera", "Both Cameras"])
        self.camera_selector.setStyleSheet(
            "min-width: 150px; max-width: 200px; padding: 5px; color: #ffffff; background-color: #333;"
        )
        camera_row_layout.addWidget(camera_label)
        camera_row_layout.addWidget(self.camera_selector)

        self.camera_display_area = QLabel("Camera Display Area")
        self.camera_display_area.setStyleSheet(
            "background-color: #2c2c2c; border: 1px solid #444; min-height: 150px; color: #aaaaaa;"
        )
        self.camera_selection_layout.addLayout(camera_row_layout)
        self.camera_selection_layout.addWidget(self.camera_display_area)

        # Option Selection Section
        self.option_selection_widget = QWidget()
        self.option_selection_layout = QVBoxLayout()
        self.option_selection_widget.setLayout(self.option_selection_layout)
        self.option_selection_widget.setStyleSheet(
            "background-color: #1c1c1c; border: 1px solid #444; padding: 10px;"
        )

        option_row_layout = QHBoxLayout()
        option_label = QLabel("Depth Option:")
        option_label.setStyleSheet("color: #ffffff; font-size: 12px; margin-right: 10px;")
        self.depth_option_selector = QComboBox()
        self.depth_option_selector.addItems(["Grayscale", "Colormap"])
        self.depth_option_selector.setStyleSheet(
            "min-width: 150px; max-width: 200px; padding: 5px; color: #ffffff; background-color: #333;"
        )
        option_row_layout.addWidget(option_label)
        option_row_layout.addWidget(self.depth_option_selector)

        self.depth_display_area = QLabel("Option Display Area")
        self.depth_display_area.setStyleSheet(
            "background-color: #2c2c2c; border: 1px solid #444; min-height: 150px; color: #aaaaaa;"
        )
        self.option_selection_layout.addLayout(option_row_layout)
        self.option_selection_layout.addWidget(self.depth_display_area)

        self.left_splitter.addWidget(self.camera_selection_widget)
        self.left_splitter.addWidget(self.option_selection_widget)

    def init_point_cloud_widget(self):
        """Initialize the 3D point cloud display area."""
        # Create a GLViewWidget for 3D visualization
        self.gl_widget = gl.GLViewWidget()
        self.gl_widget.setCameraPosition(distance=10)
        self.gl_widget.opts['distance'] = 20
        # Add a grid for reference
        grid = gl.GLGridItem()
        grid.scale(2, 2, 1)
        self.gl_widget.addItem(grid)

        # Initialize the scatter plot item for point cloud
        self.scatter = gl.GLScatterPlotItem()
        self.gl_widget.addItem(self.scatter)

    def toggle_camera(self):
        """Toggle the camera state between connected and disconnected."""
        if self.camera_running:
            self.stop_camera()
        else:
            self.start_camera()

    def start_camera(self):
        """Start the ZED camera thread."""
        if not self.camera_thread.isRunning():
            self.camera_thread.start()
        self.camera_thread.cameraStart()
        self.camera_running = True
        self.toggle_button.setText("Connected")
        self.toggle_button.setStyleSheet(
            "padding: 10px; color: #ffffff; background-color: #28A745; border: none; font-size: 14px;"
        )

    def stop_camera(self):
        """Stop the ZED camera thread."""
        if self.camera_thread.isRunning():
            self.camera_thread.stop()  # Kamerayı güvenli şekilde durdur
        self.camera_running = False
        self.toggle_button.setText("Disconnected")
        self.toggle_button.setStyleSheet(
            "padding: 10px; color: #ffffff; background-color: #DC3545; border: none; font-size: 14px;"
        )
        
    def update_camera_display(self, qimage):
        """Update the camera display with the latest frame."""
        if self.camera_running:
            self.camera_display_area.setPixmap(
                QPixmap.fromImage(qimage).scaled(
                    self.camera_display_area.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
            )

    def update_depth_display(self, qimage):
        """Update the depth display with the selected option."""
        if self.camera_running:
            self.depth_display_area.setPixmap(
                QPixmap.fromImage(qimage).scaled(
                    self.depth_display_area.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
            )

    def update_point_cloud_display(self, point_cloud_data):
        if self.camera_running:

            xyz = point_cloud_data[:, :3]
            colors = point_cloud_data[:, 3:]
            
            alpha = np.ones((colors.shape[0], 1))
            colors = np.hstack((colors, alpha))

            self.scatter.setData(pos=xyz, color=colors, size=2, pxMode=True)

    def camera_selection_changed(self, selection):
        self.camera_thread.camera_selection_signal.emit(selection)
    
    def depth_selection_changed(self, selection):
        self.camera_thread.depth_option_signal.emit(selection)

    def closeEvent(self, event):
        """Handle the close event to stop the camera thread."""
        if self.camera_thread.isRunning():
            self.camera_thread.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = EnhancedMainWindow()
    main_window.show()
    sys.exit(app.exec_())
