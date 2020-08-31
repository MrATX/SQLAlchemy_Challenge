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

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>Temperature</a><br/>"
        f"<a href='/api/v1.0/2017-02-25'>Vaca Day 1 - 2/25</a><br/>"
        f"<a href='/api/v1.0/2017-02-25/2017-03-4'>Whole Vaca 2/25 - 3/4</a><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    last_date = session.query(Measurement,Measurement.date).order_by(Measurement.date.desc()).first()
    last_date_yr = last_date[1][0:4]
    last_date_mo = last_date[1][5:7]
    last_date_day = last_date[1][8:10]
    last_date = dt.datetime(int(last_date_yr),int(last_date_mo),int(last_date_day))
    year_ago = dt.datetime((int(last_date_yr)-1),int(last_date_mo),int(last_date_day))

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

#@app.root("/api/v1.0/tobs")
#def tobs():
    #session = Session(engine)

#@app.root("/api/v1.0/<string:vaca_start>")
#def 2017-02-25():
    #session = Session(engine)

#@app.root("/api/v1.0/<string:vaca_start>/<string:vaca_end>")
#def tobs():
    #session = Session(engine)


if __name__ == '__main__':
    app.run(debug=True)




