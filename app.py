import numpy as np
from pandas.io import json

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


engine = create_engine("sqlite:///Resources/hawaii.sqlite")


Base = automap_base()

Base.prepare(engine, reflect=True)
mesaurement = Base.classes.measurement
station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the rainy day API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start> and /api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
   #Convert the query results to a dictionary using date as the key and prcp as the value.
    session = Session(bind=engine)
    end_date = dt.date(2017,8,23)
    start_date = end_date - dt.timedelta(days=365)
    twelve_months = session.query(mesaurement).order_by(mesaurement.date.desc()).filter(mesaurement.date >= start_date).all()
    
    precip = session.query(mesaurement.date, mesaurement.prcp, mesaurement.station).all()

    
    return jsonify(precip)


   # Return the JSON representation of your dictionary.


@app.route("/api/v1.0/stations")
def stations():
    #Return a JSON list of stations from the dataset.
    session = Session(bind=engine)

    some_stations = session.query(station.name).all()

    session.close()

    return jsonify(some_stations)
    

@app.route("/api/v1.0/tobs")
def tobs():
    #Query the dates and temperature observations of the most active station for the last year of data.
    session = Session(bind=engine)
    end_date = dt.date(2017,8,23)
    start_date = end_date - dt.timedelta(days=365)
    active_stations = session.query(mesaurement.station, station.name, func.count(mesaurement.station))\
        .filter(mesaurement.station == station.station)\
        .group_by(mesaurement.station)\
        .order_by(func.count(mesaurement.station).desc()).all()

    station_year = session.query(mesaurement.tobs, mesaurement.station, mesaurement.date).order_by(mesaurement.date.desc()).\
        filter(mesaurement.station == active_stations[0][0]).filter(mesaurement.date >= start_date).all()

    session.close()

    return jsonify(station_year)
    # Return a JSON list of temperature observations (TOBS) for the previous year.

@app.route("/api/v1.0/<start>")
def start_end(start):
    session = Session(bind=engine)
    
    query = session.query(mesaurement.date, mesaurement.tobs).filter(mesaurement.date > start)

    session.close()

    return jsonify(query)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.


# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.


# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.


if __name__ == '__main__':
    app.run(debug=True)