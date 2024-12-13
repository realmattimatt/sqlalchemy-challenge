# sqlalchemy-challenge

## About
We will use Python and SQLAlchemy to do a basic climate analysis and data exploration of the climate database for Hawaii using two supplied csv files from past observations. 

## Before running the application, ensure you have the following dependencies installed (descriptions are in the `app.py` file):
    1. import pandas as pd
    2. import numpy as np
    3. from sqlalchemy.ext.automap import automap_base
    4. from sqlalchemy.orm import Session
    5. from sqlalchemy import create_engine, func
    6. from flask import Flask, jsonify
    7. from sqlalchemy.exc import SQLAlchemyError
    8. from flask import abort
    9. from datetime import datetime
    10. from matplotlib import style
    style.use('fivethirtyeight')
    11. import matplotlib.pyplot as plt
    12. import datetime as dt
    

### How to run.
    1. Install dependancies
    2. Run climate_starter.ipynb in Jupyter notebook or equivalent
    3. Run app.py in a terminal inside the directory to open up a working local host.
    4. Use the http://xxx.x.x.x:5000 in a search bar.
    5. Use the supplied routes to find the information needed as available. 


## Sources
1. Class time
2. [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
3. Office hours
4. [SQLAlchemy Cheatsheet](https://michaelcurrin.github.io/dev-cheatsheets/cheatsheets/python/libraries/database/sqlalchemy.html)
5. Xpert Learning Assistant
6. Stack Overflow
7. Tutor Brandon Wong
8. Tutor Carlos Gattorno
9. ChatGPT
10. Google
11. [Matplotlib Documentation](https://matplotlib.org/stable/index.html)
12. [NumPy Documentation](https://numpy.org/doc/)
13. [Pandas Documentation](https://pandas.pydata.org/docs/)
