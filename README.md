# ZEDStereoCamera,
Bu proje, ZED stereo kamera kullanarak video ve görüntü işleme işlemleri gerçekleştirmek için bir Python betiği sağlar. Çözünürlük, FPS, video kaydı ve görüntü kaydı gibi ayarları komut satırı argümanlarıyla özelleştirebilirsiniz.

## Özellikler

- **Video Kaydı**: Belirtilen çözünürlük ve FPS değerlerinde video kaydı.
- **Kare Kaydı**: Her bir kareyi ayrı bir görüntü olarak kaydetme.
- **Ekranda Görüntüleme**: İşlenen görüntüleri ekranda görselleştirme.
- **Esnek Ayarlar**: Çözünürlük, FPS, kayıt süresi ve diğer parametreler komut satırı üzerinden özelleştirilebilir.

---

## Gereksinimler

Bu projeyi çalıştırmadan önce aşağıdaki gereksinimlerin karşılandığından emin olun:

- **Python 3.6+**
- **OpenCV**
- **ZED SDK** ve Python bağımlılıkları
- **argparse** (Python'da varsayılan olarak bulunur)

### Kurulum

Gerekli bağımlılıkları yüklemek için:

```bash
pip install opencv-python opencv-python-headless
```

## Kullanım

Betik, komut satırı argümanları alarak çalışır. Argümanlar ile çözünürlük, FPS ve kayıt süresi gibi parametreleri ayarlayabilirsiniz.

### Komut Satırı Argümanları

| Argüman              | Tip    | Varsayılan | Açıklama                                                                 |
|----------------------|--------|------------|-------------------------------------------------------------------------|
| `--video_resolution` | `str`  | `HD2K`     | Kaydedilecek videonun çözünürlüğü. (Seçenekler: `HD2K`, `HD1080`, `HD720`, `VGA`) |
| `--frame_rate`       | `int`  | `30`       | Saniyedeki kare sayısı (FPS).                                           |
| `--video_save`       | `bool` | `False`    | Videoyu kaydetmek istiyorsanız `True`.                                 |
| `--frame_save`       | `bool` | `False`    | Her kareyi ayrı dosya olarak kaydetmek istiyorsanız `True`.            |
| `--save_time`        | `int`  | `5`        | Videonun kaç saniye boyunca kaydedileceği.                             |
| `--frame_time`       | `int`  | `1`        | Her bir kareyi kaç saniye arayla kaydetmek istediğiniz.                |
| `--show`             | `bool` | `False`    | Görüntülerin ekranda gösterilip gösterilmeyeceği.                      |

---

### Örnek Kullanımlar

#### Video Kaydı

Videoyu `HD1080` çözünürlükte, 30 FPS ile 10 saniye boyunca kaydetmek için:

```bash
python main.py --video_resolution HD1080 --frame_rate 30 --video_save True --save_time 10
```