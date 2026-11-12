from PIL import Image, ExifTags
from pillow_heif import register_heif_opener
from datetime import datetime
import requests
register_heif_opener()

# in C
COLD_BOUND = -5
WARM_BOUND = 30

# weights for subjective modifiers
WEATHER_REPORT_WEIGHTING = 0.25
INDOOR_BOOST = .4

def to_decimal(lat, ref):
    decimal = 0.0
    deg, mins, secs = lat[0], lat[1], lat[2]
    decimal = deg + (mins/60) + (secs/3600)

    if ref == 'S' or  ref == 'W': 
        decimal *= -1.0

    return float(decimal)
    

def get_context(path):
    img = Image.open(path)
    exif = img.getexif()

    # extract photo data if HEIC has it 
    exif_info = exif.get_ifd(ExifTags.IFD.Exif)         
    gps_info  = exif.get_ifd(ExifTags.IFD.GPSInfo) 

    # get time data
    taken   = exif_info.get(ExifTags.Base.DateTimeOriginal) 
    if taken != None: 
        taken_formatted = datetime.strptime(taken, "%Y:%m:%d %H:%M:%S")
        for_request = taken_formatted.strftime("%Y-%m-%d")
        hour = taken_formatted.hour
    else: 
        taken_formatted = for_request = hour = None
    
    # get location data
    lat = gps_info.get(ExifTags.GPS.GPSLatitude)         
    lat_ref = gps_info.get(ExifTags.GPS.GPSLatitudeRef)
    lon = gps_info.get(ExifTags.GPS.GPSLongitude)         
    lon_ref = gps_info.get(ExifTags.GPS.GPSLongitudeRef)

    # convert GPS data into decimal for accurate placement
    if lat == None or lat_ref == None: 
        lat_as_dec = None
    else: 
        lat_as_dec = to_decimal(lat, lat_ref)

    if lon == None or lon_ref == None: 
        lon_as_dec = None
    else: 
        lon_as_dec = to_decimal(lon, lon_ref)

    # request weather data from open source meterological site
    if lon_as_dec != None and lat_as_dec != None and taken_formatted != None: 
        try: 
            response = requests.get("https://archive-api.open-meteo.com/v1/archive", 
                        params={ "latitude": lat_as_dec,
                                "longitude": lon_as_dec,
                                "start_date": for_request,    
                                "end_date": for_request,    
                                "hourly": "temperature_2m,precipitation,cloud_cover",
                                "timezone": "auto", 
                                },
                        timeout=10)
            
            response.raise_for_status()
            # pull weather data needed
            # start by converting the response into readable json data
            data = response.json()

            # extract temp data (2m above ground if you care) from json data at the hour of the day photo was taken
            temp = data["hourly"]["temperature_2m"][hour]

            # mm of rain in that current moment
            percipitation = data["hourly"]["precipitation"][hour]  

            # % cloud cover
            cloud_cover = data["hourly"]["cloud_cover"][hour] 
        except (requests.exceptions.RequestException, ValueError, KeyError, IndexError):
            temp = None
            percipitation = None
            cloud_cover = None    
    else:
        temp = None
        percipitation = None
        cloud_cover = None    
          

    # package data
    context = {'datetime': taken_formatted, 
               'lat': lat_as_dec, 
               'lon': lon_as_dec, 
               'temp': temp,
               'percip': percipitation,
               'clouds': cloud_cover
            }
        
    return context

def apply_context(vector, context): 
    # context dict to vars
    timestamp, temp, percipetation, cc = (context['datetime'], 
                                          context['temp'], 
                                          context['percip'], 
                                          context['clouds'])
    
    # vibe vector to vars
    warmth, happiness, energy, outdoor = (vector['warmth'], 
                                          vector['happiness'], 
                                          vector['energy'], 
                                          vector['outdoor'])
    
    final_vector = {'warmth': round(warmth, 5), 
                    'happiness': round(happiness, 5), 
                    'energy': round(energy, 5)}

    if (temp == None):
        return final_vector

    # warmth modifiers, see report for explination
    warmth_adjustment = (temp - COLD_BOUND) / (WARM_BOUND - COLD_BOUND)
    warmth_adjustment = max(0.0, min(1.0, warmth_adjustment))
    outdoor_warmth = (1 - WEATHER_REPORT_WEIGHTING) * warmth + WEATHER_REPORT_WEIGHTING * warmth_adjustment
    indoor_warmth  = warmth + INDOOR_BOOST * (1 - warmth_adjustment) * (1 - warmth)
    final_warmth   = outdoor * outdoor_warmth + (1 - outdoor) * indoor_warmth

    final_vector = {'warmth': round(final_warmth, 5), 
                    'happiness': round(happiness, 5), 
                    'energy': round(energy, 5)}

    return final_vector

        
