#!/usr/bin/python
import xml.etree.ElementTree as ET
import re
from datetime import datetime, timedelta



def main():
    weather_file = "/home/pi/workspace/lcd/weather_report.xml"
    print "Current: "
    print getCurrent(weather_file)
    print "Today: "
    print getToday(weather_file)
    print "Tomorrow: "
    print getTomorrow(weather_file)

def getCurrent(weather_file):
    tree = ET.parse(weather_file)
    root = tree.getroot()
 
    sky = 'outside'
    temp = 'ERROR'

    for a in root.iter('item'):
        title =  a.find('title').text
        description = a.find('description').text
        curr = re.search('^Currently:', title)
        if curr:
            #print title
            rtemp = re.search(r'\b(?:\d*F)\b', title)
            if(rtemp):
                temp = rtemp.group(0)
                #print temp.group(0)

    return temp, sky

def getToday(weather_file):
    tree = ET.parse(weather_file)
    root = tree.getroot()
    
    today = datetime.today().strftime("%-m/%-d/%Y")
    high = "err"
    low = "err"
    sky = "err"
    # print ("today is " + today)

    for a in root.iter('item'):
        title =  a.find('title').text
        description = a.find('description').text
        temp = re.search('^'+today, title)
        if temp:
            data = re.split('\s+',description)
            #print 'found today\'s weather report:'
            low, high, sky = parse_description(description,data)

    return low, high,  sky


def getTomorrow(weather_file):
    tree = ET.parse(weather_file)
    root = tree.getroot()
    
    tomorrow = (datetime.today()+timedelta(days=1)).strftime("%-m/%-d/%Y")
    high = "err"
    low = "err"
    sky = "err"
    #print ("tomorrow is " + tomorrow)

    for a in root.iter('item'):
        title =  a.find('title').text
        description = a.find('description').text
        temp = re.search('^'+tomorrow, title)
        if temp:
            data = re.split('\s+',description)
            #print 'found tomorrow\'s weather report:'
            low, high, sky = parse_description(description,data)

    return low, high, sky


def parse_description(description,data):

    low = "err2"
    high = "err2"
    sky = "err2"

    for i in range (0,len(data)):
        #print data[i]
        if (data[i] == 'High:'):
            high = data[i+1] + data[i+2]
        if (data[i] == 'Low:'):
            low = data[i+1]+ data[i+2]

        #get weather keywords
        if (re.search('(?i)severe', description)):
            sky = "REALLY BAD STUFF"
        elif (re.search('(?i)rain', description)):                   
            if(re.search('(?i)snow', description)):
                sky = "Rain & snow..."                    
            elif(re.search('(?i)heavy', description)):
                sky = "Heavy rain..."                    
            elif (re.search('(?i)wind', description)):
                sky = "Windy & rain..."
            else:
                sky = "Looks rainy..."
        elif (re.search('(?i)shower', description)):
            sky = "Just showers..."
        elif (re.search('(?i)fog', description)):
            sky = "Looks foggy..."
        elif (re.search('(?i)mist', description)):
            sky = "How mist-erious..."
        elif (re.search('(?i)snow', description)):
            if (re.search('(?i)heavy', description)):
                sky = "Heavy snow!"
            elif (re.search('(?i)flurr', description)):
                sky = "Flurries!"
            else:
                sky = "Looking snowy..."    
        elif (re.search('(?i)flurr', description)):
            sky = "Flurries!"    
        elif (re.search('(?i)cloud', description)):
            sky = "Cloudy..."
        elif (re.search('(?i)wind', description)):
            if (re.search('(?)cold', description)):
                sky = "Cold & windy..."
            else:
                sky = "Windy..."
        elif (re.search('(?i)sun', description)):
            if (re.search('(?i)cloud', description)):
                sky = "Sun & clouds"
            else:
                sky = "Sunny!"
        else:
            sky = "The usual.."

    return low, high, sky        
         
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print 'goodbye'
