import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measure = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"Welcome and kindly see the routes below: <br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"for following: input the date as yyyy-mm-dd <br/>"
        f"/api/v1.0/start_temp/<start>/ <br/>"
        f"/api/v1.0/temperature/<start>/<end>"
    
    )


#Convert the query results to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    measure_col = [Measure.date, Measure.prcp]
    precip_data = session.query(*measure_col).all()
    session.close()
    #date as the key and prcp as the value.
    precip_dict = {date: prcp for date, prcp in precip_data}
    
    return jsonify(precip_dict)


#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)
    station_data = session.query(Station.station, Station.name).all()
    session.close()

    station_list = {station: name for station, name in station_data}
    return jsonify(station_list)


#Query the dates and temperature observations of the most active station for the last year of data.
#Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def temp_observe():
    session = Session(engine)
    most_active = session.query(Measure.station, func.count(Measure.date)).group_by(Measure.station).order_by(func.count(Measure.date).desc()).first()
    search_station = most_active[0]
    active_station_data = session.query(Measure.station, Measure.tobs).filter(Measure.station == search_station).all()
    session.close()

    station_tobs = {station: tobs for station, tobs in active_station_data}
    return jsonify(station_tobs)


#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/start_temp/<start>")
def start_temp(start = None):
    session = Session(engine)
    temp = [func.min(Measure.tobs), func.avg(Measure.tobs), func.max(Measure.tobs)]
    temp_start = session.query(*temp).filter(Measure.date >= start).all()
    session.close()
    temp_start_list = list(np.ravel(temp_start))
        
    return jsonify(temp_start_list)        

@app.route("/api/v1.0/temperature/<start>/<end>")
def temperature(start = None, end = None):
    session = Session(engine)
    temp_dt = [func.min(Measure.tobs), func.avg(Measure.tobs), func.max(Measure.tobs)]
    temp_date = session.query(*temp_dt).filter(Measure.date >= start).filter(Measure.date <= end).all()
    session.close()
    temp_date_list = list(np.ravel(temp_date))
        
    return jsonify(temp_date_list)
        

if __name__ == "__main__":
    app.run(debug = True)