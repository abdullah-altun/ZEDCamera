import pyzed.sl as sl
import math
import numpy as np
import cv2 
import open3d as o3d

def voxel_downsample_point_cloud(xyz, colors, voxel_size=0.01):
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(xyz)
        pcd.colors = o3d.utility.Vector3dVector(colors)
        down_pcd = pcd.voxel_down_sample(voxel_size=voxel_size)
        down_xyz = np.asarray(down_pcd.points)
        down_colors = np.asarray(down_pcd.colors)

        return down_xyz, down_colors

def zed_to_open3d_pointcloud(zed_point_cloud):
    # ZED Point Cloud verisini numpy array olarak al
    point_cloud_data = zed_point_cloud.get_data()
    point_cloud_np = np.array(point_cloud_data, copy=True)

    # Geçerli noktaları seç (NaN olan noktaları filtrele)
    mask = ~np.isnan(point_cloud_np[:, :, 0])  # X ekseni için NaN kontrolü
    valid_points = point_cloud_np[mask]

    # XYZ ve RGBA değerlerini ayır
    xyz = valid_points[:, :3]  # İlk üç sütun XYZ koordinatları
    rgba = valid_points[:, 3]  # Dördüncü sütun renk bilgisi

    # Renkleri Open3D formatına dönüştür
    # rgba = rgba.astype(np.uint32)  # Renkleri uint32'ye çevir
    rgba_uint32 = np.frombuffer(rgba.astype(np.float32).tobytes(), dtype=np.uint32)
    r = ((rgba_uint32 & 0x00FF0000) >> 16) / 255.0  # Kırmızı
    g = ((rgba_uint32 & 0x0000FF00) >> 8) / 255.0   # Yeşil
    b = (rgba_uint32 & 0x000000FF) / 255.0          # Mavi
    colors = np.stack((b,g,r), axis=1)

    xyz, colors = voxel_downsample_point_cloud(xyz, colors, voxel_size=0.01)
    o3d_point_cloud = o3d.geometry.PointCloud()
    o3d_point_cloud.points = o3d.utility.Vector3dVector(xyz)
    o3d_point_cloud.colors = o3d.utility.Vector3dVector(colors)

    return o3d_point_cloud

def main():
    zed = sl.Camera()

    init_params = sl.InitParameters()
    init_params.depth_mode = sl.DEPTH_MODE.NEURAL
    init_params.coordinate_units = sl.UNIT.MILLIMETER 
    init_params.depth_minimum_distance = 0.10
    init_params.depth_maximum_distance = 10

    status = zed.open(init_params)
    if status != sl.ERROR_CODE.SUCCESS:
        print("Camera Open : "+repr(status)+". Exit program.")
        exit()

    runtime_parameters = sl.RuntimeParameters()

    image = sl.Mat()
    depth = sl.Mat()
    point_cloud = sl.Mat()

    mirror_ref = sl.Transform()
    mirror_ref.set_translation(sl.Translation(2.75,4.0,0))
    
    while True:
        frame = None
        if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
            zed.retrieve_image(image, sl.VIEW.LEFT)
            zed.retrieve_measure(depth, sl.MEASURE.DEPTH)
            zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA)
            frame = image.get_data()[:,:,:3]
            depth_image = depth.get_data()

            depth_image[np.isnan(depth_image)] = 0 
            depth_image[np.isinf(depth_image)] = 0 
            depth_image_normalized = cv2.normalize(depth_image, None, 0, 255, cv2.NORM_MINMAX)
            depth_image_normalized = depth_image_normalized.astype(np.uint8)
            depth_image_reversed = 255 - depth_image_normalized
            depth_colormap = cv2.applyColorMap(depth_image_reversed, cv2.COLORMAP_JET)
            
        if frame is not None:
            cv2.imshow("image",image.get_data()[:,:,:3])
            cv2.imshow("depth",depth_colormap)
            o3d_point_cloud = zed_to_open3d_pointcloud(point_cloud)
            o3d.visualization.draw_geometries([o3d_point_cloud], window_name="ZED Point Cloud")
            # print(point_cloud)

            if cv2.waitKey(1) == ord("q"):
                    break
        
    cv2.destroyAllWindows()
    zed.close()

if __name__ == "__main__":
    main()