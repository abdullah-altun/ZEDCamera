import pyzed.sl as sl
import os
import cv2

from datetime import datetime
import time
import numpy as np

def get_zed_resolution(resolution_str):
    resolution_map = {
        "HD2K": sl.RESOLUTION.HD2K,
        "HD1080": sl.RESOLUTION.HD1080,
        "HD720": sl.RESOLUTION.HD720,
        "VGA": sl.RESOLUTION.VGA
    }
    return resolution_map.get(resolution_str, sl.RESOLUTION.HD2K)

def get_resolution_dimensions(resolution_str):
    resolution_dimensions = {
        "HD2K": (2208, 1242),
        "HD1080": (1920, 1080),
        "HD720": (1280, 720),
        "VGA": (672, 376)
    }
    return resolution_dimensions[resolution_str]

class Camera:
    current_date = datetime.now()
    day = current_date.day
    month = current_date.month
    year = current_date.year

    record_start_time = time.time()

    def __init__(self,args):
        self.fps = args.frame_rate
        self.resolution = args.video_resolution
        self.saveVideo = args.video_save
        self.saveFrame = args.frame_save
        self.saveTime = args.save_time
        self.frameTime = args.frame_time
        self.show = args.show
        self.videoSize = get_resolution_dimensions(self.resolution)

        self.folderCreate()
        self.cameraRead()
        self.videoSave()
        
    def cameraRead(self):
        self.zed = sl.Camera()
        init_params = sl.InitParameters()
        init_params.camera_resolution = get_zed_resolution(self.resolution)
        init_params.camera_fps = self.fps

        err = self.zed.open(init_params)
        if err != sl.ERROR_CODE.SUCCESS:
            print(f"Kamerayı başlatma hatası: {err}")
            exit(-1)
        
    def videoSave(self):
        if self.saveVideo:
            path = f"images/{self.day}-{self.month}-{self.year}/video/leftCamera_{int(len(os.listdir(f'images/{self.day}-{self.month}-{self.year}/video'))/2)}.avi"
            leftCap = cv2.VideoWriter(path,
                cv2.VideoWriter_fourcc(*'XVID'),30,self.videoSize)
            path = f"images/{self.day}-{self.month}-{self.year}/video/rightCamera_{int(len(os.listdir(f'images/{self.day}-{self.month}-{self.year}/video'))/2)}.avi"
            rightCap = cv2.VideoWriter(path,
                cv2.VideoWriter_fourcc(*'XVID'),30,self.videoSize)
        
        left_image = sl.Mat()
        right_image = sl.Mat()
        self.startTime = time.time()

        while True:
            if self.zed.grab() == sl.ERROR_CODE.SUCCESS:
                self.zed.retrieve_image(left_image, sl.VIEW.LEFT)
                self.zed.retrieve_image(right_image, sl.VIEW.RIGHT)
                left_frame = left_image.get_data()
                right_frame = right_image.get_data()

                if self.saveFrame:
                    currentTime = time.time()
                    self.frameSave(left_frame,right_frame,currentTime)

                if self.saveVideo:
                    leftCap.write(left_frame[:, :, :3])
                    rightCap.write(right_frame[:, :, :3])

                    if self.record_start_time and (time.time() - self.record_start_time >= self.saveTime):
                        print(f"{self.saveTime} saniye doldu, kayıt durduruluyor....")
                        break
            
                if self.show:
                    mergeImage = np.hstack((left_frame,right_frame))
                    cv2.imshow("image",cv2.resize(mergeImage,(1920,1080)))

                    if cv2.waitKey(1) == ord("q"):
                        break
        cv2.destroyAllWindows()

    def frameSave(self,leftImage,rightImage,currentTime):
        if (currentTime - self.startTime) > self.frameTime:
            cv2.imwrite(f"images/{self.day}-{self.month}-{self.year}/left/Left_{len(os.listdir(f'images/{self.day}-{self.month}-{self.year}/left'))}.png",leftImage)
            cv2.imwrite(f"images/{self.day}-{self.month}-{self.year}/right/Right_{len(os.listdir(f'images/{self.day}-{self.month}-{self.year}/right'))}.png",rightImage)
            self.startTime = currentTime
            
    def folderCreate(self):
        if not(os.path.exists("images")):
            os.mkdir("images")
        if not(os.path.exists(f"images/{self.day}-{self.month}-{self.year}")):
            os.mkdir(f"images/{self.day}-{self.month}-{self.year}")
            os.mkdir(f"images/{self.day}-{self.month}-{self.year}/left")
            os.mkdir(f"images/{self.day}-{self.month}-{self.year}/right")
            os.mkdir(f"images/{self.day}-{self.month}-{self.year}/video")

        
        
