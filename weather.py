# This is a heavily modified version of e_paper_weather_display
# All data has been tweaked to be pulled from TempestWX

#Global settings:
station = 'STATION ID HERE'
token = 'API TOKEN HERE'
nwszone = 'NWS COUNTY CODE HERE'
memes = 1 #Enter 1 for on, 0 (zero, not the letter O) for off if you hate kittens
wind_thresh = 15 #Wind gust speed to trigger windy icon

#API URLs
URL = 'https://swd.weatherflow.com/swd/rest/better_forecast?station_id=' + station + '&units_temp=f&units_wind=mph&units_pressure=inhg&units_precip=in&units_distance=mi&token=' + token
nws_url = 'https://api.weather.gov/alerts/active?zone=' + nwszone

import sys
import os
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
icondir = os.path.join(picdir, 'icon')
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'font')

# Search lib folder for display driver modules
sys.path.append('lib')

#Import drivers for 7.5" e-ink display
from waveshare_epd import epd7in5_V2
epd = epd7in5_V2.EPD()

from datetime import datetime
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

import requests, urllib.request, json
from io import BytesIO

# define funciton for writing image and sleeping for 5 min.
def write_to_screen(image, sleep_seconds):
    print('Writing to screen.')
    # Write to screen
    h_image = Image.new('1', (epd.width, epd.height), 255)
    # Open the template
    screen_output_file = Image.open(os.path.join(picdir, image))
    # Initialize the drawing context with template as background
    h_image.paste(screen_output_file, (0, 0))
    epd.init()
    epd.display(epd.getbuffer(h_image))
    # Sleep
    time.sleep(2)
    epd.sleep()
    print('Sleeping for ' + str(sleep_seconds) +'.')
    time.sleep(sleep_seconds)

# define function for displaying error
def display_error(error_source):
    # Display an error
    print('Error in the', error_source, 'request.')
    # Initialize drawing
    error_image = Image.open(os.path.join(picdir, 'error_template.png'))
    # Initialize the drawing
    draw = ImageDraw.Draw(error_image)
    current_time = datetime.now().strftime('%H:%M')
    draw.text((590, 430), 'Last Refresh: ' + str(current_time), font = font23, fill=black)
    # Save the error image
    error_image_file = 'error.png'
    error_image.save(os.path.join(picdir, error_image_file))
    # Close error image
    error_image.close()
    # Write error to screen
    write_to_screen(error_image_file, 30)

#Draw boxes for centering text
def create_image(size, bgColor, message, font, fontColor):
    W, H = size
    image = Image.new('RGB', size, bgColor)
    draw = ImageDraw.Draw(image)
    _, _, w, h = draw.textbbox((0, 0), message, font=font)
    draw.text(((W-w)/2, (H-h)/2), message, font=font, fill=fontColor)
    return image

#Draw boxes for centering text with image on right for World 2-Desert
def create_image_w2(size, bgColor, message, font, fontColor):
    W, H = size
    image = Image.new('RGB', size, bgColor)
    draw = ImageDraw.Draw(image)
    _, _, w, h = draw.textbbox((0, 0), message, font=font)
    draw.text((((W-w)/2)-20, (H-h)/2), message, font=font, fill=fontColor)
    return image

# Set the fonts
font20 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 20)
font22 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 22)
font23 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 23)
font25 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 25)
font30 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 30)
font35 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 35)
font50 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 50)
font60 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 60)
font100 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 100)
font160 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 160)

# Set the colors
black = 'rgb(0,0,0)'
white = 'rgb(255,255,255)'
grey = 'rgb(235,235,235)'

# Initialize and clear screen
print('Initializing and clearing screen.')
epd.init()
epd.Clear()

while True:
    # Ensure there are no errors with connection
    error_connect = True
    while error_connect == True:
        try:
            # HTTP request
            print('Attempting to connect to Tempest WX.')
            response = requests.get(URL, timeout = 2.5)
            if response.status_code == 200:
                print('Connection to Tempest WX successful.')
                error_connect = None
        except requests.Timeout:
            # Call function to display connection error
            print('Connection error.')
            display_error('CONNECTION') 

    error = None
    while error == None:
        # Check status of code request
        if response.status_code == 200:
            print('JSON pull from Tempest WX successful.')
            # get data in jason format
            f = urllib.request.urlopen(URL)
            wxdata = json.load(f)
            f.close()
            # get current dict block
            current = wxdata['current_conditions']
            # get current
            temp_current = current['air_temperature']
            # get feels like
            feels_like = current['feels_like']
            # get humidity
            humidity = current['relative_humidity']
            #get dew point
            dewpt = current['dew_point']
            # get wind speed
            wind = current['wind_avg']
            windcard = current['wind_direction_cardinal']
            gust =  current['wind_gust']
            # get description
            weather = current['conditions']
            report = current['conditions']
            #get pressure trend
            baro = current['sea_level_pressure']
            trend = current['pressure_trend']

            #Meme Mode Mod
            icon_code = current['icon']
            if memes == 0 and icon_code != 'thunderstorm' and icon_code != 'snow' and icon_code != 'sleet' and icon_code != 'rainy' and gust >= wind_thresh:
                icon_code = 'windy'
            elif memes == 1 and icon_code != 'thunderstorm' and icon_code != 'snow' and icon_code != 'sleet' and icon_code != 'rainy' and gust >= wind_thresh:
                icon_code = 'windy-meme'
            elif memes ==1 and dewpt >= 76:
                icon_code = 'death-meme'
                report = 'Death'                
            elif memes ==1 and feels_like >= 95 and (humidity >= 60 or dewpt >= 70) :
                icon_code = 'angry-sun-meme'
                report = 'World 2-'
            else:
                icon_code = current['icon']

            #Lighning strikes in the last 3 hours
            strikesraw = current['lightning_strike_count_last_3hr']
            strikes = f"{strikesraw:,}"

            #Check for Thundersnow
            if icon_code == 'snow' and strikesraw > 1 and memes == 1:
                icon_code = 'thundersnow'

            #Lightning distance message
            lightningdist = current['lightning_strike_last_distance_msg']

            # get daily dict block
            daily = wxdata['forecast']['daily'][0]

            # get daily precip
            daily_precip_percent = daily['precip_probability']

            total_rain = current['precip_accum_local_day']
            rain_time = current['precip_minutes_local_day']
            if rain_time > 0 and total_rain <= 0:
                total_rain = 1000
            if rain_time >= 61:
                hours = rain_time // 60
                minutes = rain_time % 60
                if hours >1:
                    rain_time = "{} hrs {} min".format(hours, minutes)
                else:
                    rain_time = "{}hr {} min".format(hours, minutes)
            else:
                rain_time = "{} min".format(rain_time)

            # get min and max temp
            daily_temp = current['air_temperature']
            temp_max = daily['air_temp_high']
            temp_min = daily['air_temp_low']
            sunriseepoch = daily['sunrise']
            sunsetepoch = daily['sunset']
            #Convert epoch to readable time
            sunrise = datetime.fromtimestamp(sunriseepoch)
            sunset = datetime.fromtimestamp(sunsetepoch)
            #Get Severe weather data from NWS
            alert = None
            string_event = None
            response = requests.get(nws_url)
            nws = response.json()

            try:
                alert = nws['features'][int(0)]['properties']
                event = alert['event']
                urgency = alert['urgency']
                severity = alert['severity']
            except IndexError:
                alert = None

            if alert != None:
                string_event = event
            #string_event = 'Severe Thunderstorm Warning'
            #print(string_event)

            # Set strings to be printed to screen
            string_temp_current = format(temp_current, '.0f') + u'\N{DEGREE SIGN}F'
            string_feels_like = 'Feels like: ' + format(feels_like, '.0f') +  u'\N{DEGREE SIGN}F'
            string_humidity = 'Humidity: ' + str(humidity) + '%'
            string_dewpt = 'Dew Point: ' + format(dewpt, '.0f') +  u'\N{DEGREE SIGN}F'
            string_wind = 'Wind: ' + format(wind, '.1f') + ' MPH ' + windcard
            if report.title() == 'Wintry Mix Possible':
                string_report = ''
                string_reportaux = report.title()
            elif report == 'World 2-':
                string_report = report
            else:
                string_report = report.title()
            string_baro = str(baro) + ' inHg'
            string_temp_max = 'High: ' + format(temp_max, '>.0f') + u'\N{DEGREE SIGN}F'
            string_temp_min = 'Low:  ' + format(temp_min, '>.0f') + u'\N{DEGREE SIGN}F'
            string_precip_percent = 'Precip: ' + str(format(daily_precip_percent, '.0f'))  + '%'
            if total_rain < 1000:
                string_total_rain = 'Total: ' + str(format(total_rain, '.2f')) + ' in | Duration: ' + str(rain_time)
            else:
                string_total_rain = 'Total: Trace | Duration: ' + str(rain_time)
            string_rain_time = str(rain_time)

            # Set error code to false
            error = False

        else:
            # Call function to display HTTP error
            display_error('HTTP')

    # Open template file
    template = Image.open(os.path.join(picdir, 'template.png'))
    # Initialize the drawing context with template as background
    draw = ImageDraw.Draw(template)

    # Draw top left box
    #Logic for nighttime....DAYTIME
    nowcheck = datetime.now()
    if icon_code.startswith('possibly') or icon_code == 'thundersnow' or icon_code  == 'cloudy' or icon_code == 'foggy' or icon_code == 'windy' or icon_code.startswith('clear') or icon_code.startswith('partly') or icon_code.endswith('-meme'):
        icon_file = icon_code + '.png'
    elif nowcheck >= sunrise and nowcheck < sunset:
        icon_file = icon_code + '-day.png'
    else:
        icon_file = icon_code + '-night.png'
    icon_image = Image.open(os.path.join(icondir, icon_file))
    template.paste(icon_image, (46, 15))
    if string_report == 'World 2-':
        now_center = create_image_w2((249, 25), 'white', string_report, font23, 'black')
        template.paste(now_center, (6,175))
        w2d_file = 'w2d.png'
        w2d_image = Image.open(os.path.join(icondir, w2d_file))
        template.paste(w2d_image, (155,176))
    else:
        now_center = create_image((249, 25), 'white', string_report, font23, 'black')
        template.paste(now_center, (6,175))

    #Barometer trend logic block
    if trend == 'falling':
        baro_file = 'barodown.png'
    elif trend == 'steady':
        baro_file = 'barosteady.png'
    else:
        baro_file = 'baroup.png'
    baro_image = Image.open(os.path.join(icondir, baro_file))
    template.paste(baro_image, (15, 213)) #15, 218
    draw.text((65, 223), string_baro, font=font22, fill=black) #65,228

    #Precipitation Logic
    if temp_current <= 39 and temp_current >= 33:
        precip_file = 'mix.png'
    elif temp_current <= 32:
        precip_file = 'chance_snow.png'
    else:
        precip_file = 'precip.png'
    precip_image = Image.open(os.path.join(icondir, precip_file))
    template.paste(precip_image, (15, 255)) #15, 260
    draw.text((65, 263), string_precip_percent, font=font22, fill=black) #65, 268

    #Main temp centered
    temp_center = create_image((530, 190), 'white', string_temp_current, font160, 'black') #365, 190
    template.paste(temp_center, (263,20)) #580,35
    difference = int(feels_like) - int(temp_current)

    #Center Feels Like
    if memes == 0 and dewpt >= 76:
        textImg2 = Image.new(mode='RGB', size=(520, 65), color='white')
        draw3 = ImageDraw.Draw(textImg2)
        x2 = ((textImg2.width // 2)- 35) 
        y2 = (textImg2.height // 2)
        draw3.text((x2, y2), string_feels_like, fill='black', font=font50, anchor='mm')
        text_width, text_height = draw.textsize(string_feels_like, font=font50)
        feels_file = 'death.png'
        feels_image = Image.open(os.path.join(icondir, feels_file))
        textImg2.paste(feels_image, ((((265 + text_width) // 2 ) + 100), 3))
        template.paste(textImg2, (265, 195))
        
    if (report != 'Death' and report != 'World 2-') and difference >= 5:
        textImg2 = Image.new(mode='RGB', size=(520, 65), color='white')
        draw3 = ImageDraw.Draw(textImg2)
        x2 = ((textImg2.width // 2)- 35) 
        y2 = (textImg2.height // 2)
        draw3.text((x2, y2), string_feels_like, fill='black', font=font50, anchor='mm')
        text_width, text_height = draw.textsize(string_feels_like, font=font50)
        feels_file = 'feelshot.png'
        feels_image = Image.open(os.path.join(icondir, feels_file))
        textImg2.paste(feels_image, ((((265 + text_width) // 2 ) + 100), 3))
        template.paste(textImg2, (265, 195))

    elif difference <= -5:
        textImg2 = Image.new(mode='RGB', size=(520, 65), color='white')
        draw3 = ImageDraw.Draw(textImg2)
        x2 = ((textImg2.width // 2)- 35) 
        y2 = (textImg2.height // 2)
        draw3.text((x2, y2), string_feels_like, fill='black', font=font50, anchor='mm')
        text_width, text_height = draw.textsize(string_feels_like, font=font50)
        feels_file = 'feelscold.png'
        feels_image = Image.open(os.path.join(icondir, feels_file))
        textImg2.paste(feels_image, ((((265 + text_width) // 2 ) + 100), 3))
        template.paste(textImg2, (265, 195))

    else:
        textImg2 = Image.new(mode='RGB', size=(520, 65), color='white')
        draw3 = ImageDraw.Draw(textImg2)
        x2 = (textImg2.width // 2) 
        y2 = (textImg2.height // 2)
        draw3.text((x2, y2), string_feels_like, fill='black', font=font50, anchor='mm')
        text_width, text_height = draw.textsize(string_feels_like, font=font50)
        template.paste(textImg2, (265, 195))

    #High/Low temps
    draw.text((35, 330), string_temp_max, font=font50, fill=black) #35,325
    draw.line((170, 390, 265, 390), fill=black, width=4)
    draw.text((35, 395), string_temp_min, font=font50, fill=black) #35,390

    #Rh, Dew Point and Wind
    rh_file = 'rh.png'
    rh_image = Image.open(os.path.join(icondir, rh_file))
    template.paste(rh_image, (320, 320))
    draw.text((370, 330), string_humidity, font=font23, fill=black) #345, 340
    dp_file = 'dp.png'
    dp_image = Image.open(os.path.join(icondir, dp_file))
    template.paste(dp_image, (320, 373))
    draw.text((370, 383), string_dewpt, font=font23, fill=black)
    wind_file = 'wind.png'
    wind_image = Image.open(os.path.join(icondir, wind_file))
    template.paste(wind_image, (320, 425))
    draw.text((370, 435), string_wind, font=font23, fill=black) #345, 400

    #Update time with lightning mod
    #Begin Lightning mod
    if strikesraw >= 1:
        strike_file = 'strike.png'
        strike_image = Image.open(os.path.join(icondir, strike_file))
        template.paste(strike_image, (605, 305))
        draw.text((695, 330), 'Strikes', font=font22, fill=white)
        draw.line((690, 355, 765, 355), fill =white, width=3)
        strikeimg = Image.new(mode='RGB', size=(50, 20), color='black') 
        draw1 = ImageDraw.Draw(strikeimg)
        x0 = (strikeimg.width // 2)
        y0 = (strikeimg.height // 2)
        draw1.text((x0, y0), strikes, fill='white', font=font20, anchor='mm')
        template.paste(strikeimg, (703, 360))
        draw.text((685, 400), 'Distance', font=font22, fill=white)
        draw.line((680, 425, 773, 425), fill =white, width=3)
        draw.text((683, 430), lightningdist, font=font20, fill=white)
    else:
        draw.text((627, 330), 'UPDATED', font=font35, fill=white)
        current_time = datetime.now().strftime('%H:%M')
        draw.text((627, 375), current_time, font = font60, fill=white)

    #Precipitaton mod
    if total_rain > 0 or total_rain == 1000:
        textImg3 = Image.new(mode='RGB', size=(530, 50), color='white')
        draw4 = ImageDraw.Draw(textImg3)
        x3 = ((textImg2.width // 2) + 25)
        y3 = ((textImg2.height // 2) - 10)
        draw4.text((x3, y3), string_total_rain, fill='black', font=font23, anchor='mm')
        text_width2, text_height2 = draw.textsize(string_total_rain, font=font23)
        train_file = 'totalrain.png'
        train_image = Image.open(os.path.join(icondir, train_file))
        textImg3.paste(train_image, ((((x3 - (text_width2 //2))) -50), 0)) #-150
        template.paste(textImg3, (263, 15))

    #Severe Weather Mod
    try:
         if string_event != None:

            #Center the warning data at the bottom of the screen
            textImg = Image.new(mode='RGB', size=(530, 40), color='white')
            draw2 = ImageDraw.Draw(textImg)
            if 'Special' in string_event:
                x = (textImg.width // 2 + 25)
                y = (textImg.height // 2)
                draw2.text((x, y), string_event, fill='black', font=font23, anchor='mm')
                text_width, text_height = draw.textsize(string_event, font=font23)
                alert_file = 'info.png'
                alert_image = Image.open(os.path.join(icondir, alert_file))
                textImg.paste(alert_image, (((x - (text_width //2)) - 50) , 0))
            else:
                x = (textImg.width // 2)
                y = (textImg.height // 2)
                draw2.text((x, y), string_event, fill='black', font=font23, anchor='mm')
                text_width, text_height = draw.textsize(string_event, font=font23)
                alert_file = 'warning.png'
                alert_image = Image.open(os.path.join(icondir, alert_file))
                textImg.paste(alert_image, (((x - (text_width //2)) - 50) , 0))
                textImg.paste(alert_image, (((x + (text_width //2)) + 10) , 0))
            template.paste(textImg, (263, 255))

    except NameError:
        print('No Severe Weather')
    # Save the image for display as PNG
    screen_output_file = os.path.join(picdir, 'screen_output.png')
    template.save(screen_output_file)
    # Close the template file
    template.close()

    # Write to screen
    write_to_screen(screen_output_file, 300)
