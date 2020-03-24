#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Documentation here.
    conda create -n covid -c conda-forge ipython requests matplotlib python=3
    conda activate covid

"""

# Imports
import fx
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# Parameters
refresh = False  # set flag to true if data should be refreshed

# Load data
usData, stateData, stateSummary, italyData = fx.getDatasets(refresh=refresh)

# %% Plot cases by date

plt.plot(usData['date'], usData['positive'], label='US')
plt.plot(italyData['date'], italyData['totalPositive'], label='Italy')
plt.plot(stateData['WA']['date'], stateData['WA']['positive'], label='Washington')
plt.plot(stateData['CA']['date'], stateData['CA']['positive'], label='California')
plt.legend()
plt.tight_layout()
ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
plt.savefig('figs/positives_over_time.png')
plt.show()

# %%

# define colors for states
cv = iter(['red', 'purple', 'pink'])

fig, ax1 = plt.subplots()
plt.xlabel('Days after 100 cases')
plt.ylabel('Covid-19 cases')
left, bottom, width, height = [0.5, 0.6, 0.2, 0.2]
ax2 = fig.add_axes([left, bottom, width, height])

timevec = np.arange(0, len(italyData['totalPositive']))
growth = np.power(1.3, timevec) * 100.
ax1.plot(growth, 'k:', label='30% daily growth', linewidth=3)
ax1.plot(italyData['totalPositive'], color='orange', label='Italy')
ax1.plot(usData['positive'], color='blue', label='US')
for state in stateData.keys():
    sd = stateData[state]
    p = sd['positive']
    p = [0 if value is None else value for value in p]
    p = [value for value in p if value >= 100]
    if state in ['CA', 'WA', 'NY']:
        c = next(cv)
        ax1.plot(p, label=state, color=c)
        ax2.plot(p[0:7], label=state, color=c)
    else:
        ax2.plot(p[0:7], color='gray')

ax2.plot(growth[0:7])
ax1.legend()
plt.tight_layout()
plt.savefig('figs/positives_over_100.png')
plt.show()

