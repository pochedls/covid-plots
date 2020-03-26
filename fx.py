#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Function library to fetch data related to covid-19.

    conda create -n covid python=3.6 matplotlib ipython requests
    $conda activate covid

    https://gist.github.com/rogerallen/1583593
    https://towardsdatascience.com/walkthrough-mapping-basics-with-bokeh-and-geopandas-in-python-43f40aa5b7e9

"""

import requests
import datetime
from collections import defaultdict
import time
import numpy as np
import pickle
import os


def request2json(url):
    """
    jsonData = request2json(url)

    Helper function takes a URL and returns the json response.
    """
    R = requests.get(url)
    jsonData = R.json()
    return jsonData


def parseItaly(data):
    """
    dataOut = parseItaly(jsonData)

    Function takes Italian data (json) and returns a dictionary
    of fields with data lists:

    dataOut['date'] = [datetime.date(2020, 2, 24),
                       datetime.date(2020, 2, 25),
                       datetime.date(2020, 2, 26),
                       ...]
    dataOut['totalCases'] = [4324, 8623, 9587, ...]
    """

    # field mappings
    fields = {'data': 'date',
              'ricoverati_con_sintomi': 'hospitalizedWithSymptoms',
              'terapia_intensiva': 'intensiveCare',
              'totale_ospedalizzati': 'totalHospitalized',
              'isolamento_domiciliare': 'homeQuarantine',
              'totale_attualmente_positivi': 'totalPositive',
              'nuovi_attualmente_positivi': 'newPositives',
              'dimessi_guariti': 'dischargedRecovered',
              'deceduti': 'deceased',
              'totale_casi': 'totalCases',
              'tamponi': 'swabs'}
    # create empty dictionary
    dataOut = {}
    for key in fields:
        enKey = fields[key]
        dataOut[enKey] = []

    # loop over each day and store fields in dictionary
    for day in data:
        for key in fields.keys():
            enKey = fields[key]
            # cast dates to datetime, otherwise leave as int
            if key == 'data':
                d = day['data']
                d = datetime.datetime.strptime(d, "%Y-%m-%dT%H:%M:%S").date()
            else:
                d = day[key]
            dataOut[enKey].append(d)

    return dataOut


# def none2zero(value):
#     if value is None:
#         value = 0
#     return value


# def parseStateData(data):
#     """
#     dataOut = parseStateData(jsonData)

#     Function takes state level data (json) and returns a dictionary
#     of fields with data lists:

#     dataOut['date'] = [datetime.date(2020, 3, 22),
#                        datetime.date(2020, 3, 23),
#                        datetime.date(2020, 3, 24),
#                        ...]
#     dataOut['total'] = [515, 515, 522, 531s, ...]
#     """
#     # field mappings
#     fields = ['date', 'positive', 'negative', 'pending',
#               'hospitalized', 'death', 'total']
#     # create empty dictionary
#     dataOut = {}
#     for key in fields:
#         dataOut[key] = []

#     # loop over each day and store fields in dictionary
#     for day in data:
#         for key in fields:
#             # cast dates to datetime, otherwise leave as int
#             if key == 'date':
#                 d = str(day['date'])
#                 d = datetime.datetime.strptime(d, "%Y%m%d").date()
#             else:
#                 d = day[key]
#             dataOut[key].append(d)

#     # re-arrange fields so time is ascending
#     dt = np.array(dataOut['date'])
#     IndList = np.argsort(dt)
#     for key in dataOut.keys():
#         dataOut[key] = [dataOut[key][index] for index in IndList]

#     return dataOut


def fetchState(state):
    """
    dataOut = fetchState(state)

    Function takes a two-letter state abbreviation, fetches the state
    level Covid-19 data and parses it into a dictionary of lists:

    dataOut['date'] = [datetime.date(2020, 3, 22),
                       datetime.date(2020, 3, 23),
                       datetime.date(2020, 3, 24),
                       ...]
    dataOut['total'] = [515, 515, 522, 531s, ...]
    """

    # define state level API url
    url = 'https://covidtracking.com/api/states/daily?state=' + state + '&'
    R = requests.get(url)
    x = R.content.decode()
    # check if request succeeded
    # if it fails it returns an error about CloudBase issues...
    if x.find('Cloud') > 0:
        success = False
        return success, {}
    else:
        stateData = R.json()
        stateData = parseUsData(stateData)
        success = True
        return success, stateData


def fetchDetailedStateData(stateSummary, retryLimit=10, verbose=True):
    """
    dataOut = fetchDetailedStateData(stateSummary, retryLimit=10, verbose=True)

    Function takes the json data from the Covid-19 state API to determine
    states that have data available. It then downloads data for each individual
    state. The data is organized into a dictionary of states. Each state
    contains a dictionary with the state level data:

    dataOut['CA']['date'] = [datetime.date(2020, 3, 22),
                       datetime.date(2020, 3, 23),
                       datetime.date(2020, 3, 24),
                       ...]
    dataOut['CA']['total'] = [515, 515, 522, 531s, ...]
    """

    # get list of states in dataset
    states = []
    for item in stateSummary:
        # skip if item is empty
        if ((list(item.keys()) == []) | (item['state'] is None)):
            continue
        else:
            states.append(item['state'])
    states = list(set(states))
    states.sort()

    # loop over states and get data; organize data into a dictionary of lists
    outData = {}
    for state in states:
        if verbose:
            print(state)
        success = False
        # if API fails, try again to retry limit
        retry = 0
        while ((not success) & (retry < retryLimit)):
            success, stateData = fetchState(state)
            retry += 1
            if success:
                outData[state] = stateData
            else:
                if verbose:
                    print(state + ' failed. Retry ' + str(retry) + ' of 10.')
                time.sleep(45)
        # alert if state failed
        if ((retry == retryLimit) & verbose):
            print(state + ' failed.')
    return outData


def parseUsData(data):
    """
    dataOut = parseUnitedStates(jsonData)

    Function takes US data (json) and returns a dictionary
    of fields with data lists:

    dataOut['date'] = [datetime.date(2020, 2, 24),
                       datetime.date(2020, 2, 25),
                       datetime.date(2020, 2, 26),
                       ...]
    dataOut['totalCases'] = [4324, 8623, 9587, ...]
    """
    
    # get fields
    fields = list(data[0].keys())

    # create empty dictionary
    dataOut = {}
    for key in fields:
        dataOut[key] = []

    # loop over each day and store fields in dictionary
    for day in data:
        for key in fields:
            # cast dates to datetime, otherwise leave as int
            if key == 'date':
                d = str(day['date'])
                d = datetime.datetime.strptime(d, "%Y%m%d").date()
            else:
                d = day[key]
            dataOut[key].append(d)

    # re-arrange fields so time is ascending
    dt = np.array(dataOut['date'])
    IndList = np.argsort(dt)
    for key in dataOut.keys():
        dataOut[key] = [dataOut[key][index] for index in IndList]

    return dataOut

def getDatasets(refresh=False):
    """
    usData, stateData, stateSummary, italyData = getDatasets()

    Function loads datasets. By setting optional argument refresh
    to true, it will update all datasets:
        getDatasets(refresh=True)
    """
    # if refresh is true, download/parse/save data
    # else load existing pickle file
    if refresh:

        # API URLs
        italyUrl = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-andamento-nazionale.json'
        statesUrl = 'https://covidtracking.com/api/states'
        usUrl = 'https://covidtracking.com/api/us/daily'

        # get Italian data
        italyData = request2json(italyUrl)
        italyData = parseItaly(italyData)

        # get US state level data
        stateSummary = request2json(statesUrl)
        stateData = fetchDetailedStateData(stateSummary)

        # get national data
        usData = request2json(usUrl)
        usData = parseUsData(usData)

        # save out data for convenience
        data = {'usData': usData, 'italyData': italyData,
                'stateData': stateData, 'stateSummary': stateSummary}

        with open('data/covid.pkl', 'wb') as f:
            pickle.dump(data, f)
    else:
        with open('data/covid.pkl', 'rb') as f:
            data = pickle.load(f)
        usData = data['usData']
        italyData = data['italyData']
        stateData = data['stateData']
        stateSummary = data['stateSummary']

    return usData, stateData, stateSummary, italyData
