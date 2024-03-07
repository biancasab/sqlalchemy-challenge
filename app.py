# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy

from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()

# reflect the tables
base.prepare(engine, reflect=True)

# Save references to each table
measurement = base.classes.measurement
station = base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available API routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a JSON of the last 12 months of precipitation data"""
    # Create session
    session = Session(engine)

    # Query precipitation data
    precipitation_scores = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= dt.date(2017,8,23) - dt.timedelta(days=365)).\
    order_by(measurement.date).all()

    # Close session
    session.close()

    # Convert query results to a dictionary
    precipitation_dict = {date: prcp for date,prcp in precipitation_scores}
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def get_stations():
    """Return a JSON list of stations."""
    # Create session
    session = Session(engine)

    # Query all stations
    stations = session.query(station.station,).all()

    # Close session
    session.close()

    # Create a list for the stations
    stations_list =[]
    for name in stations:
        stations_list.append(name.station)
    
    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations for the most active station for the previous year."""
    # Create session
    session = Session(engine)

    # Query dates and temps of the most-active station for previous year 
    temp_scores_most_active = session.query(measurement.date, measurement.tobs).\
    filter(measurement.date >= dt.date(2017,8,23) - dt.timedelta(days=365)).\
    filter(measurement.station == "USC00519281").\
    order_by(measurement.date).all()

    # Close session
    session.close()

    # Create a list for the temperature observations
    tobs_list = []
    for result in temp_scores_most_active:
        tobs_list.append(result[1])

    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def start_date(start):
    """Returns the min, max, and ave temps from the given start date"""
    # Create session
    session = Session(engine)

    # Query the min, max, and ave temps from the given start date
    temp_stats = session.query(func.min(measurement.tobs).label("min_temp"), 
    func.max(measurement.tobs).label("avg_temp"), 
    func.avg(measurement.tobs).label("max_temp"))\
            .filter(measurement.date >= start).all()
    
    # Close session
    session.close()

    #Create a list for the min, max, and ave temps
    stats_list = []
    for result in temp_stats:
        stats_list.append({
            "TMIN": result.min_temp,
            "TAVG": result.avg_temp,
            "TMAX": result.max_temp
        })
    
    return jsonify(stats_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """Returns the min, max, and ave temps from the given start and end date"""
   
    # Create session
    session = Session(engine)

    # Query the min, max, and ave temps from the given start and end date
    temp_stats = session.query(func.min(measurement.tobs).label("min_temp"),
                  func.max(measurement.tobs).label("avg_temp"),
                  func.avg(measurement.tobs).label("max_temp"))\
            .filter(measurement.date >= start)\
            .filter(measurement.date <= end).all()

    # Close session
    session.close()

    #Create a list for the min, max, and ave temps
    stats_list = []
    for result in temp_stats:
        stats_list.append({
            "TMIN": result.min_temp,
            "TAVG": result.avg_temp,
            "TMAX": result.max_temp
        })
    
    return jsonify(stats_list)
                    
if __name__ == '__main__':
    app.run(debug=True)