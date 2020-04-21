import numpy as np
import requests
from bs4 import BeautifulSoup


def get_data(countrylabel):
    """take html source code from link and read information from it as string. Read dates and total cases
	return dictionary"""
    country = dict({'countrylabel':countrylabel})       # return dictionary with data to this country

    link = "http://www.worldometers.info/coronavirus/country/%s/" % countrylabel  # read this website
    r = requests.get(link)                              # response from website
    soup = BeautifulSoup(r.content, 'html.parser')      # data structure representing a parsed HTML
    charts = soup.find_all("script", 
                           attrs={'type': 'text/javascript', 
                                  'src':'', 'class':'', 'data-cfasync':''})  # find all <script type='text/javascript' in html and store them to a list 
    for i in range(len(charts)):
        if 'coronavirus-cases-linear' in str(charts[i]):                     # find the chart with data wanted
            rawdata = str(charts[i]).replace(" ", "")                        # html to string and omit whitspaces
            time = rawdata.split('xAxis:{\ncategories:[')[1].split("]}")[0]  # split string to time data               
            time = np.array(time.replace("\"", "").split(','))               # make array of strings
            total = rawdata.split('TotalCoronavirusCases')[1].split('data:[')[1].split("]}")[0]  # total cases to time data 
            total = np.array(total.split(','), dtype=int)
            country['time'] = time
            country['total'] = total
            return country
        else:
            pass

if __name__ == '__main__':
    print(get_data('germany'))
