import open3d as o3d
import numpy as np
import pyzed.sl as sl
import cv2

from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage

class ZEDCameraThread(QThread):
    image_signal = pyqtSignal(QImage)
    depth_signal = pyqtSignal(QImage)
    camera_selection_signal = pyqtSignal(str)
    depth_option_signal = pyqtSignal(str)

    point_cloud_signal = pyqtSignal(np.ndarray)
                                    
    def __init__(self):
        super().__init__()
        self.pointData = []

    def cameraStart(self):
        self.zed = sl.Camera()
        self.running = True
        self.camera_selection = 'Left Camera'
        self.depth_option = 'Grayscale'

        self.camera_selection_signal.connect(self.set_camera_selection)
        self.depth_option_signal.connect(self.set_depth_option)

    @pyqtSlot(str)
    def set_camera_selection(self, selection):
        self.camera_selection = selection
        print(self.camera_selection)

    @pyqtSlot(str)
    def set_depth_option(self, option):
        self.depth_option = option
        print(self.depth_option)

    def run(self):
        init_params = sl.InitParameters()
        init_params.depth_mode = sl.DEPTH_MODE.NEURAL
        init_params.coordinate_units = sl.UNIT.METER
        init_params.depth_minimum_distance = 0.4
        init_params.depth_maximum_distance = 5
        init_params.camera_resolution = sl.RESOLUTION.HD2K

        status = self.zed.open(init_params)
        if status != sl.ERROR_CODE.SUCCESS:
            print("Kamera Açılmadı: " + repr(status) + ". Programdan çıkılıyor.")
            return

        runtime_parameters = sl.RuntimeParameters()
        image = sl.Mat()
        depth = sl.Mat()
        point_cloud = sl.Mat()

        image_left = sl.Mat()
        image_right = sl.Mat()

        while self.running:
            if self.zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
                if self.camera_selection == 'Left Camera':
                    self.zed.retrieve_image(image, sl.VIEW.LEFT)
                    frame = image.get_data()[:, :, :3].copy()
                elif self.camera_selection == 'Right Camera':
                    self.zed.retrieve_image(image, sl.VIEW.RIGHT)
                    frame = image.get_data()[:, :, :3].copy()
                elif self.camera_selection == 'Both Cameras':
                    self.zed.retrieve_image(image_left, sl.VIEW.LEFT)
                    self.zed.retrieve_image(image_right, sl.VIEW.RIGHT)
                    frame_left = image_left.get_data()[:, :, :3].copy()
                    frame_right = image_right.get_data()[:, :, :3].copy()

                    # Görüntüleri Yatayda Birleştir
                    combined_frame = np.hstack((frame_left, frame_right))

                    # Yeniden Boyutlandır (Sol Kamera Boyutunda)
                    combined_frame = cv2.resize(
                        combined_frame, (frame_left.shape[1], frame_left.shape[0])
                    )
                    frame = combined_frame
                else:
                    self.zed.retrieve_image(image, sl.VIEW.LEFT)
                    frame = image.get_data()[:, :, :3].copy()

                frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)

                height, width, channel = frame.shape
                bytes_per_line = channel * width
                frame_qimage = QImage(
                    frame.data.tobytes(),
                    width,
                    height,
                    bytes_per_line,
                    QImage.Format_RGB888,
                )
                self.image_signal.emit(frame_qimage)

                self.zed.retrieve_measure(depth, sl.MEASURE.DEPTH)
                # Derinlik İşleme
                depth_data = depth.get_data().copy()
                depth_data[np.isnan(depth_data)] = 0
                depth_data[np.isinf(depth_data)] = 0
                depth_normalized = cv2.normalize(
                    depth_data, None, 0, 255, cv2.NORM_MINMAX
                )
                depth_normalized = depth_normalized.astype(np.uint8)

                if self.depth_option == 'Grayscale':
                    depth_colormap = cv2.cvtColor(depth_normalized, cv2.COLOR_GRAY2RGB)
                else:  # Colormap
                    depth_colormap = cv2.applyColorMap(
                        255 - depth_normalized, cv2.COLORMAP_JET
                    )

                height_d, width_d = depth_colormap.shape[:2]
                bytes_per_line_d = 3 * width_d
                depth_qimage = QImage(
                    depth_colormap.data.tobytes(),
                    width_d,
                    height_d,
                    bytes_per_line_d,
                    QImage.Format_RGB888,
                )
                self.depth_signal.emit(depth_qimage)

                self.zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA)

                point_cloud_data = point_cloud.get_data()
                point_cloud_np = np.array(point_cloud_data, copy=True)

                mask = ~np.isnan(point_cloud_np[:, :, 0]) 
                valid_points = point_cloud_np[mask]

                xyz = valid_points[:, :3] 
                rgba = valid_points[:, 3]

                rgba_uint32 = np.frombuffer(rgba.astype(np.float32).tobytes(), dtype=np.uint32)
                r = ((rgba_uint32 & 0x00FF0000) >> 16) / 255.0  # Kırmızı
                g = ((rgba_uint32 & 0x0000FF00) >> 8) / 255.0   # Yeşil
                b = (rgba_uint32 & 0x000000FF) / 255.0          # Mavi
                colors = np.stack((b,g,r), axis=1)

                self.pointData = [xyz,colors]
                
                down_xyz, down_colors = self.voxel_downsample_point_cloud(xyz, colors, voxel_size=0.01)
                # down_xyz, down_colors = xyz,colors
                # print(down_xyz.shape)
                # print(down_colors.shape)
                point_cloud_array = np.hstack((down_xyz, down_colors))
                self.point_cloud_signal.emit(point_cloud_array)

    def rgba_float_to_rgb(self,rgba_array):
        rgba_array_contiguous = np.ascontiguousarray(rgba_array)

        rgba_uint8 = rgba_array_contiguous.view(np.uint8).reshape(-1, 4)
        b = rgba_uint8[:, 0]
        g = rgba_uint8[:, 1]
        r = rgba_uint8[:, 2]

        rgb = np.vstack((r, g, b)).T
        rgb_normalized = rgb / 255.0

        return rgb_normalized
    
    def voxel_downsample_point_cloud(self, xyz, colors, voxel_size=0.01):
        # Create Open3D point cloud
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(xyz)
        pcd.colors = o3d.utility.Vector3dVector(colors)

        # Perform voxel downsampling
        down_pcd = pcd.voxel_down_sample(voxel_size=voxel_size)

        # Extract downsampled points and colors
        down_xyz = np.asarray(down_pcd.points)
        down_colors = np.asarray(down_pcd.colors)

        return down_xyz, down_colors


    def stop(self):
        self.running = False
        if self.zed.is_opened():
            self.zed.close()

