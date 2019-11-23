import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return the Precipitation dictionary"""
    # Query date and prcp
    results = session.query(Measurement.date, Measurement.prcp).\
        order_by(Measurement.date.desc()).all()

    session.close()

    # Create a dictionary from the raw data and append to a list of prcpData
    prcpData = []
    for date, prcp in results:
        prcpDict = {}
        prcpDict["date"] = date
        prcpDict["prcp"] = prcp
        prcpData.append(prcpDict)

    return jsonify(prcpData)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
        
    """Return a list of all stations"""
    # Query all stations
    results = session.query(Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find the last date in our data
    last_date = session.query(Measurement.date).\
        order_by(Measurement.date.desc()).first()

    # Calculate the date one year ago from the last data point in the database
    one_year = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= str(one_year), Measurement.date <= '2017-08-23').\
            order_by(Measurement.date.desc()).all()    

    session.close()

    # Create a dictionary from the raw data and append to a list
    tempLastYear = []
    for date, tobs in results:
        tempDict = {}
        tempDict["date"] = date
        tempDict["temperature"] = tobs
        tempLastYear.append(tempDict)

    return jsonify(tempLastYear)


@app.route('/api/v1.0/<start>/')
def startDate(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    results = session.query(Measurement.date, func.avg(Measurement.tobs), 
        func.max(Measurement.tobs), func.min(Measurement.tobs)).\
        filter(Measurement.date == start).all()

    session.close()

    # Create a dictionary from the raw data and append to a list
    startDataList = []
    for result in results:
        startDataDict = {}
        startDataDict['Date'] = result[0]
        startDataDict['Average Temperature'] = result[1]
        startDataDict['Highest Temperature'] = result[2]
        startDataDict['Lowest Temperature'] = result[3]
        startDataList.append(startDataDict)

    return jsonify(startDataList)

@app.route('/api/v1.0/<start>/<end>/')
def query_dates(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    results = session.query(func.avg(Measurement.tobs), func.max(Measurement.tobs),
        func.min(Measurement.tobs)).\
        filter(Measurement.date >= start, Measurement.date <= end).all()

    session.close()

    # Create a dictionary from the raw data and append to a list
    datesDataList = []
    for result in results:
        datesDataDict = {}
        datesDataDict["Start Date"] = start
        datesDataDict["End Date"] = end
        datesDataDict["Average Temperature"] = result[0]
        datesDataDict["Highest Temperature"] = result[1]
        datesDataDict["Lowest Temperature"] = result[2]
        datesDataList.append(datesDataDict)
    return jsonify(datesDataList)


if __name__ == '__main__':
    app.run(debug=True)
