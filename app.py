# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, asc, desc, func, and_
import datetime as dt
from datetime import datetime as dt, timedelta
import matplotlib.pyplot as plt

#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect the tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

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
    return (
        f"Welcome to the API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start and /api/v1.0/start/end<br/>"
        f"start and end date format: yyyy-mm-dd"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    most_recent_date = session.query(measurement.date).order_by(desc(measurement.date)).first()[0]
    
    # Calculate the date one year from the last date in data set.
    most_recent_date = dt.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(measurement.date, measurement.prcp).\
            filter(measurement.date <= most_recent_date).\
            filter(measurement.date >= one_year_ago).\
            order_by(measurement.date).all() 
    
    session.close()
    # Convert the results to a dicitonary
    results_dict = {date: prcp for date, prcp in results}

    #Return the JSONify results
    return jsonify(results_dict)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    stations_query = session.query(station.station).all()
   
    session.close()

    # convert the list of row objects to a list of dictionaries to jsonify
    stations_list = [row.station for row in stations_query]

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # Using the most active station id
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    from sqlalchemy import and_

    # Design a query to retrieve the last 12 months of precipitation data and plot the results. 
    # Starting from the most recent data point in the database. 
    most_recent_date = session.query(measurement.date).order_by(desc(measurement.date)).first()[0]

    # Calculate the date one year from the last date in data set.
    most_recent_date = dt.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - timedelta(days=365)

    temp_data = session.query(measurement.tobs).\
                filter(and_(measurement.station == 'USC00519281', measurement.date >= one_year_ago)).all()

    #Pull the temp out of the tuple into a list.
    temps = [temp[0] for temp in temp_data]

    #Close the session
    session.close()

    return jsonify(temps)

    # Return a JSON list of the minimum temperature, the average temperature, 
    # and the maximum temperature for a specified start or start-end range.

    # For a specified start, calculate TMIN, TAVG, and TMAX for all the dates 
    # greater than or equal to the start date.

    # For a specified start date and end date, calculate TMIN, TAVG, and TMAX 
    # for the dates from the start date to the end date, inclusive.
      
@app.route("/api/v1.0/<start>") 
@app.route("/api/v1.0/<start>/<end>")
def temps(start, end=None):
    session = Session(engine)
    
    start_time = dt.strptime(start, '%Y-%m-%d') 
    end_time = None if end is None else dt.strptime(end, '%Y-%m-%d')
    
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    
    if end_time is None:
        results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start_time).all()
    else:
        results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(and_(measurement.date >= start_time, measurement.date <= end_time)).all()
    
    session.close()

    if not results:
        return jsonify({"error": "No results found"}), 404

    result_list = [list(result) for result in results]

    return jsonify(result_list)
    
if __name__ == '__main__':
    app.run(debug=True)


    