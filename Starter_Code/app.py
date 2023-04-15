# Import the dependencies.

import datetime as dt


import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect,Column, Integer, String, Float, Date, and_
from sqlalchemy.sql import text

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///C:/Users/aumek/OneDrive/Desktop/Git_Personnal_Rep/sqlalchemy-challenge/sqlalchemy-challenge/Starter_Code/Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

inspector = inspect(engine)
inspector.get_table_names()

# Save references to each table
Mst = Base.classes.measurement
St = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind=engine)


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
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )


           
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a dictionary of the past 12 months of precipitation"""
    # Query past 12 months
    
    most_recent_date = session.query(Mst.date).order_by(Mst.date.desc()).first()
    most_recent_date_str = most_recent_date[0] 
        
    one_year_ago = (dt.datetime.strptime(most_recent_date_str, '%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')
    last_12_months = session.query(Mst.date, Mst.prcp).\
    filter(Mst.date >= one_year_ago).\
    order_by(Mst.date).all()

    session.close()

    # Convert list of tuples into list of dictionaries
    results = []
    for date, prcp in last_12_months:
        results.append({"date": date, "prcp": prcp})

    return jsonify(results)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations from the dataset"""
    active_stations = session.query(Mst.station).\
    group_by(Mst.station).\
    order_by(func.count().desc()).all()
    
    session.close()

    # Convert list of tuples into normal list
    results_stations = []
    for station in active_stations:
        results_stations.append({"station": station[0]})

    return jsonify(results_stations)



@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations (TOBS) for the 12months."""
    
    # Query the dates and temperature observations of the most active station for the last year of data
    last_date = session.query(Mst.date).order_by(Mst.date.desc()).first()[0]
    last_12_months = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query the last 12 months of temperature observation data for the most active station
    temperature_data = session.query(Mst.tobs)\
                        .filter(Mst.station == 'USC00519281')\
                        .filter(Mst.date >= last_12_months)\
                        .all()

    session.close()

    # Convert list of tuples into normal list
    results_temperature = []
    for temperature in temperature_data:
        results_temperature.append({"tobs": temperature[0]})

    return jsonify(results_temperature)


@app.route("/api/v1.0/<start>")
def start(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range."""

    # Create session object
    session = Session(engine)

    # Query temperature statistics for given start date
    results = session.query(func.min(Mst.tobs), func.avg(Mst.tobs), func.max(Mst.tobs)).\
        filter(Mst.date >= start).\
        all()

    session.close()

    # Convert list of tuples into normal list
    temperature_stats = []
    for temp_stat in results:
        temperature_stats.append({"TMIN": temp_stat[0], "TAVG": temp_stat[1], "TMAX": temp_stat[2]})

    return jsonify(temperature_stats)
     
    
    
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range."""

    # Create session object
    session = Session(engine)

    # Query temperature statistics for given start and end dates
    results = session.query(func.min(Mst.tobs), func.avg(Mst.tobs), func.max(Mst.tobs)).\
        filter(and_(Mst.date >= start, Mst.date <= end)).\
        all()

    session.close()

    # Convert list of tuples into normal list
    temperature_stats = []
    for temp_stat in results:
        temperature_stats.append({"TMIN": temp_stat[0], "TAVG": temp_stat[1], "TMAX": temp_stat[2]})

    return jsonify(temperature_stats)


if __name__ == "__main__":
    app.run(debug=True)
