import argparse
from camera import Camera

def parse_arguments():
    parser = argparse.ArgumentParser(description='StereoVisionProcessing ayarları')
    parser.add_argument("--video_resolution", type=str, choices=["HD2K", "HD1080", "HD720", "VGA"], 
                        default="HD2K", help="Kaydedilecek videonun çözünürlüğünü seçin. (Seçenekler: HD2K, HD1080, HD720, VGA)")
    parser.add_argument("--frame_rate", type=int, default=30, help="Kaydedilecek videonun saniyedeki kare sayısını (FPS) belirtin. (Varsayılan: 30 FPS)")
    parser.add_argument("--video_save", type=bool, default=False, help="Videoyu kaydetmek istiyorsanız True olarak ayarlayın. (Varsayılan: False)")
    parser.add_argument("--frame_save", type=bool, default=False, help="Her bir kareyi ayrı görüntü olarak kaydetmek istiyorsanız True olarak ayarlayın. (Varsayılan: False)")
    parser.add_argument("--save_time", type=int, default=5, help="Videonun kaç saniye boyunca kaydedileceğini belirtin. (Varsayılan: 5 saniye)")
    parser.add_argument("--frame_time", type=int, default=1, help="Her bir kareyi kaç saniye arayla kaydetmek istediğinizi belirtin. (Varsayılan: 1 saniye)")
    parser.add_argument("--show", type=bool, default=False, help="Görüntüler ekranda bastırılması.")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    camera = Camera(args)