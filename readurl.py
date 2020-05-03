import numpy as np
import requests
from bs4 import BeautifulSoup


def get_data(countrylabel):
    """take html source code from link and read information from it as string. Read dates and total cases
	return dictionary. Read corona data from http://www.worldometers.info/coronavirus/country/countrylabel.
	:param: countrylabel str"""
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
        
        elif 'graph-active-cases-total' in str(charts[i]):
            rawdata = str(charts[i]).replace(" ", "")                        # html to string and omit whitspaces
            active = rawdata.split('TotalCoronavirusCurrentlyInfected')[1].split('data:[')[1].split("]}")[0] # currently infected
            active = np.array(active.split(','), dtype=int)
            country['active'] = active
    return country

def get_data_berlin():
    """ Load from https://datawrapper.dwcdn.net/fIw01/56/ to get Covid19 data of Berlin. Source is Senatsverwaltung
    fuer Gesundheit und Pflege.
    :return dictionary
    time (str-array), total (int-array), inhosp (int-array), sever (int-array), death (int-array)"""
    berlin = dict({'countrylabel':'Berlin'})       # return dictionary with data to Berlin

    link = 'https://datawrapper.dwcdn.net/fIw01/56/'

    r = requests.get(link)                              # response from website
    soup = BeautifulSoup(r.content, 'html.parser')      # data structure representing a parsed HTML
    sourcecode = str(soup.contents)                        # get source code as string
    rawdata = sourcecode.split('gestorben\\\\n')[1].split('\\",\\"')[0]   # crop string to data
    string = rawdata.replace('\\\\t', ',').replace('\\\\n', ',')          # change utf8 delimiter to comma
    arraystr = np.array(string.split(','))                                # make string
    arraystr = np.reshape(arraystr, (len(arraystr)//5, 5))                # change to table (2darray) with 5 columns

    # extract columns in dictionary time=dates (str) rest is integer
    berlin['time'] = np.array([translate_time_format(date) for date in arraystr[:, 0]])  # dd.02.yyy -> Febdd etc
    berlin['total'] = np.array(arraystr[:, 1], dtype=int)
    berlin['inhosp'] = np.array(arraystr[:, 2], dtype=int)
    berlin['severe'] = np.array(arraystr[:, 3], dtype=int)
    berlin['death'] = np.array(arraystr[:, 4], dtype=int)
    berlin['active'] = np.zeros(len(berlin['time']))

    return berlin


def translate_time_format(ddmmyyy):
    """
    :param: ddmmyyyy (str) as 'dd.mm.yyyy'  with mm = 01,02,...,12
    :return date (str) as 'MMdd'        with MM=Jan,Feb,...,Dec
    """
    months = dict({'01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun',
                   '07': 'Jul', '08': 'Aug', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'})
    dmy = ddmmyyy.split('.')
    return months[dmy[1]] + dmy[0]

if __name__ == '__main__':
    print(get_data('germany'))
