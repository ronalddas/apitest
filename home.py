from flask import Flask,request,jsonify
app = Flask(__name__)
from postgres_functions import *
@app.route("/")
def hello():
    return "OK"

@app.route("/post_location",methods=["POST"])
def post_location():
    data=request.json
    #print(data,type(data))
    # {'ID': 11042, 'PINCODE': 'IN/855126', 'NAME': 'Tulsia', 'STATE': 'Bihar', 'LATITUDE': 24.9833, 'LONGITUDE': 81.0583} <class 'dict'>
    pincode_exists=check_if_pincode_exists(data.get("PINCODE"),data.get('LATITUDE'),data.get('LONGITUDE'))
    if len(pincode_exists) >0:
        #print("PINCODE ALREADY EXISTS")
        return jsonify({'location':pincode_exists})

    else:
        data_row=add_location(data)
        return jsonify({'new_loc':data_row})

@app.route("/get_using_postgres",methods=["GET"])
def get_using_postgres():
    data=request.json
    lat = data.get('lat')
    long = data.get('long')
    radius=data.get('radius')
    result=check_earth_distance(latitude=lat,longitude=long,radius=radius)
    return jsonify({'locations':result})

@app.route("/get_using_self",methods=["GET"])
def get_using_self():
    data = request.json
    lat = data.get('lat')
    long = data.get('long')
    radius = data.get('radius')
    result = check_earth_distance_self(latitude=lat, longitude=long, radius=radius)
    return jsonify({'locations': result})


@app.route("/get_using_geojson",methods=["GET"])
def get_using_geojson():
    data=request.json
    #print(data)
    lat=data.get('lat')
    long=data.get('long')
    #db=db_connect()
    areas=generalQuery("SELECT * FROM AREAS",args=None)
    #print(areas)
    area=check_point_polygon(areas,lat,long)
    #print("GEOJSON",area)
    return jsonify({'areas':area})


if __name__=="__main__":
    app.run()