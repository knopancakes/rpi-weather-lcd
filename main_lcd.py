#!/usr/bin/python

from lcd_16x2 import *
from subprocess import *
from time import sleep, strftime
from datetime import datetime
import weather_report_parser as weather


title = "lcd"

# modes
GREETING = 0
WEATHER_REPORT = 1
CLOCK = 2
SYS_INFO = 3

# terminal commands
get_wlan = "ip addr show wlan0 | grep inet | awk '{print $2}' | cut -d/ -f1"
get_eth0 = "ip addr show eth0 | grep inet | awk '{print $2}' | cut -d/ -f1"
get_weather = "sh /home/pi/rpi-weather-lcd/get_weather.sh 02135"
weather_file = "/home/pi/rpi-weather-lcd/weather_report.xml"
weather_mode = 3
# startup param
wupdate_delay = 600

def main():

    lcd_init()
    display_mode = 0
    global wupdate_delay
    
    while True:
        
        if( wupdate_delay < 600):
            wupdate_delay = wupdate_delay + 1
        else:
            wupdate_delay = 0;
            updateWeatherReport()
        
        if(display_mode == SYS_INFO):
            # raspberry pi info
            #sysInfo(3)
            display_mode = GREETING
        elif(display_mode == GREETING):
            # greeting mode
            greeting(1.5)
            display_mode = WEATHER_REPORT
        elif(display_mode == CLOCK):
            # clock mode
            clock(1.5)
            display_mode = SYS_INFO
        elif(display_mode == WEATHER_REPORT):
            displayWeather(1.5)
            display_mode = CLOCK

        #here want to check for user input to change modes

def greeting(delay):
    hour = datetime.now().hour

    if( 1 <= hour and hour < 4):
        msg = "Go to bed!"
    elif( 4 <= hour and hour < 12):
        msg = "Good morning"
    elif( 12 <= hour and hour < 17):
        msg = "Good afternoon"
    elif( 17 <= hour and hour < 21):
        msg = "Good evening"
    elif( 21 <= hour and hour < 24):
        msg = "Good night"
    else:
        msg = "Sleepy?"
    lcd_string(msg, LCD_LINE_1)
    lcd_string("",LCD_LINE_2)
    sleep(delay)

def clock(delay):
    time = datetime.now().strftime('%b %d  %H:%M')
    lcd_string(time, LCD_LINE_1)
    lcd_string("",LCD_LINE_2)
    sleep(delay)

def sysInfo(delay):
    global get_wlan
    global get_eth0

    iwaddr = run_cmd(get_wlan)
    inaddr = run_cmd(get_eth0)

    #print "get inaddr returns: " + inaddr
    #print "get iwaddr returns: " + iwaddr

    if(iwaddr):
        lcd_string("I am wireless!",LCD_LINE_1)
        lcd_string('IP: ' + iwaddr[:-1],LCD_LINE_2)
        sleep(delay)
    elif(inaddr):
        lcd_string("I am wired.",LCD_LINE_1)
        lcd_string('IP: ' + inaddr[:-1],LCD_LINE_2)
        sleep(delay)
    else:
        print "network must be down..."
        #ret = run_cmd('sudo reboot')
        lcd_string("I can't see!", LCD_LINE1)
        lcd_string("Please help me.",LCD_LINE2)

def updateWeatherReport():
    global weather_file
    global get_weather
    global weather_mode
    global wupdate_delay

    got_weather = 0
  
    try:
        ret = run_cmd(get_weather)
    except:
        iwaddr = run_cmd(get_wlan)
        inaddr = run_cmd(get_eth0)

        if not iwaddr and not inaddr:
            print "Network down, attempting to reset connection"
            subprocess.call(['sudo /sbin/ifdown wlan0 && sleep 10 && sudo /sbin/ifup --force wlan0'], shell=True)
            wupdate_delay = 600
        else:
            print "Something went wrong when trying to fetch weather"
        
        got_weather = 0

    got_weather = 1
    
    return got_weather


def displayWeather(delay):
    try:
        if(weather_mode > 2):
            temp_now, sky_now = weather.getCurrent(weather_file) 
            lcd_string("Currently", LCD_LINE_1)
            lcd_string( temp_now + ' ' + sky_now, LCD_LINE_2)
            sleep(delay)
        if(weather_mode > 0):
            low, high, sky = weather.getToday(weather_file)        
            lcd_string("Today's Report", LCD_LINE_1)
            lcd_string('Low: ' + low, LCD_LINE_2)
            sleep(delay)
            lcd_string("Today's Report", LCD_LINE_1)
            lcd_string('High: ' + high, LCD_LINE_2)
            sleep(delay)
            lcd_string("Today's Report", LCD_LINE_1)
            lcd_string(sky, LCD_LINE_2)
            sleep(delay)
        if(weather_mode > 1):
            low, high, sky = weather.getTomorrow(weather_file)
            lcd_string("Morrow's Report", LCD_LINE_1)
            lcd_string('Low: ' + low, LCD_LINE_2)
            sleep(delay)
            lcd_string("Morrow's Report", LCD_LINE_1)
            lcd_string('High: ' + high, LCD_LINE_2)
            sleep(delay)
            lcd_string("Morrow's Report", LCD_LINE_1)
            lcd_string(sky, LCD_LINE_2)
            sleep(delay)
    except:
        print "Something went wrong while parsing weather report"
        pass



def run_cmd(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print 'goodbye'
        lcd_byte(0x01, LCD_CMD)
        lcd_string("Goodbye!",LCD_LINE_1)
        GPIO.cleanup()
        
