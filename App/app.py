import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>Precipitation (in) - Last 12 Months</a><br/>"
        f"<a href='/api/v1.0/stations'>Stations List</a><br/>"
        f"<a href='/api/v1.0/tobs'>Daily Temperature - Last 12 Months</a><br/>"
        f"<a href='/api/v1.0/20170225'>Vaca Day 1 (2/25) - on</a><br/>"
        f"<a href='/api/v1.0/20170225/20170304'>Whole Vaca 2/25 - 3/4</a><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    #Determine most recent date and date of one year ago
    last_date = session.query(Measurement,Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = dt.datetime((int(last_date[1][0:4])-1),int(last_date[1][5:7]),int(last_date[1][8:10]))

    results = session.query(Measurement.date,func.avg(Measurement.prcp)).filter(Measurement.date>year_ago).group_by(Measurement.date).order_by(Measurement.date.desc()).all()

    session.close()

    all_results = []
    for item in results:
        item_dict = {"Date":item[0],"Avg Rainfall":round(item[1],2)}
        all_results.append(item_dict)

    return jsonify(all_results)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Measurement.station).group_by(Measurement.station).all()

    session.close()

    all_results = list(np.ravel(results))

    return jsonify(all_results)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    #Identify most active station
    results = session.query(Measurement.station,func.count(Measurement.id)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.id).desc()).all()
    most_active_stat = results[0][0]
    #Determine most recent date and date of one year ago
    last_date = session.query(Measurement,Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = dt.datetime((int(last_date[1][0:4])-1),int(last_date[1][5:7]),int(last_date[1][8:10]))
    #Query for last 12 months of temp observations
    results = session.query(Measurement.date,Measurement.tobs).\
        filter(Measurement.date>year_ago).\
        filter(Measurement.station==most_active_stat).\
        order_by(Measurement.date.desc()).all()

    session.close()

    all_results = []
    for item in results:
        item_dict = {"Date":item[0],"Temperature":round(item[1],2)}
        all_results.append(item_dict)

    return jsonify(all_results)

@app.route("/api/v1.0/<string:vaca_start>")
def vaca_start(vaca_start):
    vaca_start = (f"{vaca_start[0:4]}-{vaca_start[4:6]}-{vaca_start[6:8]}")
    session = Session(engine)
    sel = [
        Measurement.date,
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ]
    results = session.query(*sel).\
        filter(Measurement.date>=vaca_start).\
        order_by(Measurement.date).\
        group_by(Measurement.date).all()
    
    session.close()

    all_results = []
    for item in results:
        item_dict = {
            "Date":item[0],
            "Min Temp":item[1],
            "Avg Temp":item[2],
            "Max Temp":item[3],
        }
        all_results.append(item_dict)

    return jsonify(all_results)

@app.route("/api/v1.0/<string:vaca_start>/<string:vaca_end>")
def vaca_range(vaca_start,vaca_end):
    vaca_start = (f"{vaca_start[0:4]}-{vaca_start[4:6]}-{vaca_start[6:8]}")
    vaca_end = (f"{vaca_end[0:4]}-{vaca_end[4:6]}-{vaca_end[6:8]}")
    session = Session(engine)
    sel = [
        Measurement.date,
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ]
    results = session.query(*sel).\
        filter(Measurement.date>=vaca_start).\
        filter(Measurement.date<=vaca_end).\
        order_by(Measurement.date).\
        group_by(Measurement.date).all()

    session.close()

    all_results = []
    for item in results:
        item_dict = {
            "Date":item[0],
            "Min Temp":item[1],
            "Avg Temp":item[2],
            "Max Temp":item[3],
        }
        all_results.append(item_dict)

    return jsonify(all_results)

if __name__ == '__main__':
    app.run(debug=True)