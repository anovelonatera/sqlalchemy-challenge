import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import pandas as pd

from flask import Flask, jsonify


# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables Measurement and Station.
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Function to calculate Min, Avg, and Max of set of temperatures.
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()




# Flask Setup
#################################################
app = Flask(__name__)

@app.route("/")
def welcome():
     return (
        f"Welcome to the Hawaii Climate API!!!<br/>"
        f"These are the Available Routes:<br/><br/>"
        f"* Precipitations:<br/>"
        f"/api/v1.0/precipitation<br/><br/>"
        f"* Stations numbers and names:<br/>"
        f"/api/v1.0/stations<br/><br/>"
        f"* Temperatures from stations:<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        
        f"* Min/Avg/Max temperature from starting date:<br/>"
        f"/api/v1.0/START<br/><br/>"
        f"* Min/Avg/Max temperature during a period of dates date:<br/>"
        f"/api/v1.0/START_DATE/END_DATE<br/>" 

        f"To input the date use format: YYYY-mm-dd: Example: 2017-08-23"
    )
    
# Convert the query results to a Dictionary using 'date' as the key and 'prcp' as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitations():
    # Query all dates and precipitations.
    results = session.query(Measurement.date, Measurement.prcp).all()


    # Get the date from the start 12 months before the last date recorded.
    date_year_back = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Get all dates from the last 12 months of the record
    query_measurement = session.query(Measurement.date, Measurement.prcp).\
                    filter(Measurement.date >= date_year_back).\
                    order_by(Measurement.date).all()

    # Jsonify results.
    precipitations = []
    for date, prcp in query_measurement:
        prcp_dict = {}
        prcp_dict['date'] = date
        prcp_dict['prcp'] = prcp
        precipitations.append(prcp_dict)

    return jsonify(precipitations)



# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    stations_query = session.query(Station.name, Station.station).all()

    stations = []
    for name, station in stations_query:
        stations_dict = {}
        stations_dict['name'] = name
        stations_dict['station'] = station
        stations.append(stations_dict)

    return jsonify(stations)


# Query for the dates and temperature observations from a year from the last data point.
# Return a JSON list of Temperature Observations (tobs) for the previous year.
@app.route("/api/v1.0/tobs")
def temperatures():
    # Get the date from the start 12 months before the last date recorded.
    date_year_back = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    temp_query = session.query(Measurement.date, Measurement.tobs).\
                 filter(Measurement.date >= date_year_back).all()
    
    temps = []
    for date, tobs in temp_query:
        temps_dict = {}
        temps_dict['date'] = date
        temps_dict['tobs'] = tobs
        temps.append(temps_dict)

    return jsonify(temps)



# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def start(start):
    # Get last date of records
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    temperatures = calc_temps(start, latest_date[0])
    min_temp = temperatures[0][0]
    avg_temp = temperatures[0][1]
    max_temp = temperatures[0][2]

    temps_dict = {'Minimum Temperature':min_temp, 
                  'Average Temperature':avg_temp, 
                  'Maximum Temperature':max_temp}

    return jsonify(temps_dict)

# When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end_date>")
def end(start, end_date):

    temperatures = calc_temps(start, end_date)
    min_temp = temperatures[0][0]
    avg_temp = temperatures[0][1]
    max_temp = temperatures[0][2]

    temps_dict = {'Minimum Temperature':min_temp, 
                  'Average Temperature':avg_temp, 
                  'Maximum Temperature':max_temp}

    return jsonify(temps_dict)



if __name__ == '__main__':
    app.run(debug=True)


 