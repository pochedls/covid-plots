# covid-plots

Use public APIs to create a plot of Covid-19 cases. The function file (fx.py) parses the json files returned from the APIs into dictionaries / lists, which are plotted using the plot_data.py file. Could be enhanced by plotting interactive maps (e.g., using bokeh). Note that the states WA, CA, and NY are currently hardcoded into the script. 

Using Anaconda, install and activate environment with:
```
  conda create -n covid -c conda-forge ipython requests matplotlib python=3
  conda activate covid
```

Run with:
  `python plot_data.py`

To refresh data, set `refresh = True` in plot_data.py. 
