# Import the dependencies.
import pandas as pd # Data manipulation and analysis library
import numpy as np # Library for numerical operations and handling arrays
import sqlalchemy # SQL toolkit and Object Relational Mapper (ORM) for Python
from sqlalchemy.ext.automap import automap_base # For automapping database tables to Python classes
from sqlalchemy.orm import Session # For creating a session to interact with the database
from sqlalchemy import create_engine, func # For creating a database engine and using SQL functions
from flask import Flask, jsonify # Flask framework for building web applications and returning JSON responses
from sqlalchemy.exc import SQLAlchemyError # For handling exceptions related to SQLAlchemy operations
from flask import abort # For returning error responses in the Flask application
from datetime import datetime # For working with date and time, especially for validating date formats


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Print the reflected table names
print(Base.classes.keys())  # This will show you the names of all tables reflected from the database

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
# Included in each session in each route.

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """List all available api routes."""
    
    # Return a formatted string that lists all available API routes
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation (Route to get precipitation data for the last 12 months)<br/>"
        f"/api/v1.0/stations (Route to get a list of weather stations)<br/>"
        f"/api/v1.0/tobs (Route to get temperature observations from the most active station)<br/>"
        f"/api/v1.0/&lt;start&gt; (Where 'start' is a date in YYYY-MM-DD format)<br/>"                              # Route to get temperature data starting from a specific date
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt; (Where 'start' and 'end' are dates in YYYY-MM-DD format)<br/>"        # Route to get temperature data for a specific date range
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """
    Retrieves precipitation data for the last 12 months from the Measurement table.
    
    Returns:
        JSON object containing dates as keys and precipitation amounts as values.
    """
    # Start a session to interact with the database
    session = Session(engine)
    try:
        # Query the most recent date from the Measurement table
        most_recent_day = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
        most_recent_date = pd.to_datetime(most_recent_day)
        # Calculate the date 12 months prior to the most recent date
        twelve_month_prior = most_recent_date - pd.Timedelta(days=365)
        twelve_month_prior_str = twelve_month_prior.strftime('%Y-%m-%d')

        # Query precipitation data for the last 12 months
        results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= twelve_month_prior_str).order_by(Measurement.date).all()

        # Create a dictionary to hold date and precipitation data
        precip_dict = {result[0]: result[1] for result in results}

        # Return the precipitation data as a JSON response
        return jsonify(precip_dict)
    except SQLAlchemyError as e:
        # Handle any SQLAlchemy errors and return an error message
        return jsonify({"error": str(e)}), 500
    finally:
        # Ensure the session is closed after the operation
        session.close()


    
@app.route("/api/v1.0/stations")
def stations():
    """
    Retrieves a list of all station identifiers from the Station table.
    
    Returns:
        JSON object containing a list of station identifiers.
    """
    # Create a session to interact with the database
    session = Session(engine)
    try:
        # Query the Station table to get all station identifiers
        results = session.query(Station.station).all()
        # Flatten the results into a list
        stations_list = list(np.ravel(results))
        # Return the list of stations as a JSON response
        return jsonify(stations_list)
    except SQLAlchemyError as e:
        # Return an error message if there's an issue with the query
        return jsonify({"error": str(e)}), 500
    finally:
        # Close the session to free up resources
        session.close()



@app.route("/api/v1.0/tobs")
def tobs():
    """
    Retrieves temperature observations (TOBS) for the most active station over the last 12 months.
    
    Returns:
        JSON object containing dates and corresponding temperature observations.
    """
    # Create a session to interact with the database
    session = Session(engine)
    try:
        # Query to find the most active station based on the number of observations
        most_active_station = session.query(Measurement.station, func.count(Measurement.station)) \
            .group_by(Measurement.station) \
            .order_by(func.count(Measurement.station).desc()) \
            .first()[0]
            
        # Get the most recent date in the Measurement table
        most_recent_day = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
        most_recent_date = pd.to_datetime(most_recent_day)
        
        # Calculate the date 12 months prior to the most recent date
        twelve_month_prior = most_recent_date - pd.Timedelta(days=365)
        twelve_month_prior_str = twelve_month_prior.strftime('%Y-%m-%d')
        
        # Query to get temperature observations for the most active station in the last 12 months
        results = session.query(Measurement.date, Measurement.tobs) \
            .filter(Measurement.station == most_active_station) \
            .filter(Measurement.date >= twelve_month_prior_str) \
            .order_by(Measurement.date).all()

        # Create a list of dictionaries to hold the date and temperature observations
        tobs_list = [{"date": result[0], "temperature": result[1]} for result in results]

        # Return the list of temperature observations as a JSON response
        return jsonify(tobs_list)
    except SQLAlchemyError as e:
        # Return an error message if there's an issue with the query
        return jsonify({"error": str(e)}), 500
    finally:
        # Close the session to free up resources
        session.close()
        

def is_valid_date(date_str):
    """Check if the date string is in the format YYYY-MM-DD."""
    try:
        # Attempt to parse the date string into a datetime object
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        # Return False if a ValueError is raised, indicating an invalid date format
        return False
        
        
@app.route("/api/v1.0/<start>")
def start(start):
    """Retrieve temperature statistics (min, avg, max) from the given start date.
    
    Args:
        start (str): The start date in the format YYYY-MM-DD.
    
    Returns:
        JSON object containing the minimum, average, and maximum temperatures,
        or an error message if the date format is invalid or no data is found.
    """
    
    # Create a session to interact with the database
    session = Session(engine)
    # Validate the date format; if invalid, abort with a 400 error
    if not is_valid_date(start):
        abort(400, description="Invalid date format. Use YYYY-MM-DD.")
    try:
        # Query to get the min, avg, and max temperatures from the start date onward
        results = session.query(
            func.min(Measurement.tobs),
            func.round(func.avg(Measurement.tobs), 1), # Rounds the average temp to 1 decimal place
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start).all()

        # Check if results are empty or if the min temperature is None
        if not results or results[0][0] is None:
            return jsonify({"error": "No data found for the given start date."}), 404

        # Create a dictionary to hold the temperature statistics
        temperature_data = {
            "TMIN": results[0][0],
            "TAVG": results[0][1],
            "TMAX": results[0][2]
        }
        # Return the temperature statistics as a JSON response
        return jsonify(temperature_data)
    except SQLAlchemyError as e:
        # Return an error message if there's an issue with the query
        return jsonify({"error": str(e)}), 500
    finally:
        # Close the session to free up resources
        session.close()

        
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Retrieve temperature statistics (min, avg, max) from the given start to end date.
    
    Args:
        start (str): The start date in the format YYYY-MM-DD.
        end (str): The end date in the format YYYY-MM-DD.
    
    Returns:
        JSON object containing the minimum, average, and maximum temperatures,
        or an error message if the date format is invalid or no data is found.
    """
    
    # Create a session to interact with the database
    session = Session(engine)
    
    # Validate the date formats; if invalid, abort with a 400 error
    if not is_valid_date(start) or not is_valid_date(end):
        abort(400, description="Invalid date format. Use YYYY-MM-DD.")
        
    try:
        # Query to get the min, avg, and max temperatures for the specified date range
        results = session.query(
            func.min(Measurement.tobs),
            func.round(func.avg(Measurement.tobs), 1), # Rounds the average temp to 1 decimal place
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

        # Check if results are empty or if the min temperature is None
        if not results or results[0][0] is None:
            return jsonify({"error": "No data found for the given date range."}), 404

        # Create a dictionary to hold the temperature statistics
        temperature_data = {
            "TMIN": results[0][0],
            "TAVG": results[0][1],
            "TMAX": results[0][2]
        }

        # Return the temperature statistics as a JSON response
        return jsonify(temperature_data)
    except SQLAlchemyError as e:
        # Return an error message if there's an issue with the query
        return jsonify({"error": str(e)}), 500
    finally:
        # Close the session to free up resources
        session.close()
 
        
if __name__ == '__main__':
    # Run the Flask application
    app.run(debug=True) # Set debug=True for development; change to False in production
