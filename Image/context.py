from PIL import Image, ExifTags
from pillow_heif import register_heif_opener

register_heif_opener()

def context_of_photo(path):
    img = Image.open(path)
    exif = img.getexif()

    # extract photo data if HEIC has it 
    exif_info = exif.get_ifd(ExifTags.IFD.Exif)         
    gps_info  = exif.get_ifd(ExifTags.IFD.GPSInfo) 

    taken   = exif_info.get(ExifTags.Base.DateTimeOriginal) 
    lat     = gps_info.get(ExifTags.GPS.GPSLatitude)         
    lat_ref = gps_info.get(ExifTags.GPS.GPSLatitudeRef)

    print(taken, lat, lat_ref)


context_of_photo('test4.jpg')