# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, asc, desc
import datetime as dt
from datetime import timedelta

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
        f"/api/v1.0/<start> and /api/v1.0/<start>/<end>"
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

    stations_list = session.query(station.station).all()
   
    session.close()

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    
    
    
    session.close()

    return jsonify(tobs_list)


if __name__ == '__main__':
    app.run(debug=True)