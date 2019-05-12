import csv
import time
from math import sin, cos, sqrt, atan2, radians
import json
from shapely.geometry import mapping,shape,Point,LinearRing
import psycopg2
import traceback
import psycopg2.extras
import geopy.distance
connect_str = "dbname='testpython' user='ron' host='localhost' " + \
              "password='1'"

def db_connect():
# use our connection values to establish a connection
    conn = psycopg2.connect(connect_str)
    return conn

def cursor_init(conn):
    # create a psycopg2 dict cursor that can execute queries
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    return cursor

def generalQuery(query,args):
    try:
        db=db_connect()
        c=cursor_init(db)

        #print(query,args)
        c.execute(query,args)
        result=c.fetchall()
        db.commit()
        c.close()
        db.close()
        return result
    except Exception as ex:
        traceback.print_exc()

def insertQuery(table_name,datadict,db):
    try:
        c=cursor_init(db)
        args = [table_name]
        args1 = []
        for i in datadict:
            args.append(i)
            args1.append(datadict[i])

        query = "INSERT INTO %s " + " ({})".format(
            ','.join('%s' for k in list(datadict.keys())))  + " VALUES({})".format(
            ','.join('%%s' for v in list(datadict.values())))+";"


        query = query % tuple(args)
        #print("INSERT QUERY: ", query%tuple(args1))


        c.execute(query, tuple(args1))
        result="OK"#c.fetchall()
        #Make sure data is committed before closing
        db.commit()
        c.close()
        return result
    except Exception:
        traceback.print_exc()
def check_if_pincode_exists(pincode,latitude,longitude):

    lat_long_exists = check_if_lat_long_exists(latitude,longitude)
    if len(lat_long_exists) > 0:
        #print("LAT LONG EXISTS", len(lat_long_exists))
        return lat_long_exists
    if 'IN/' not in pincode:
        #pincode=pincode.split("/")[1]
        pincode='IN/'+pincode
    #print(pincode)
    query="SELECT * FROM locations WHERE PINCODE='%s'"%(pincode)
    #print(query)
    r=generalQuery(query,args=None)
    return r

def check_if_lat_long_exists(latitude,longitude):
    longitude=round(longitude,2)
    latitude=round(latitude,2)
    query = "select * from locations where cast(LATITUDE as text) like '%%%s%%' and cast(LONGITUDE as text) like '%%%s%%';" % (latitude,longitude)
    r=generalQuery(query,args=None)
    return r

def add_location(data_dict):
    index=generalQuery("SELECT COUNT(*) FROM locations",args=None)[0][0]+1
    print(type(index),index)
    data_dict['ID']=index
    if 'IN/' not in data_dict.get('PINCODE'):
        #pincode=pincode.split("/")[1]
        data_dict['PINCODE']='IN/'+data_dict['PINCODE']
    insertQuery('locations',data_dict,db=db_connect())
    return data_dict
def check_earth_distance(latitude,longitude,radius):
    query="SELECT * FROM locations WHERE earth_box(ll_to_earth(%f,%f), %f) @> ll_to_earth(LATITUDE, LONGITUDE);" %(latitude,longitude,radius)
    r=generalQuery(query,args=None)
    return r


#########################
#                       #
#   HELPER FUNCTIONS    #
#                       #
#########################
def parse_json():
    pass

def check_point_polygon(ob,lat,long):
    p = Point(long, lat)
    final_areas=[]
    final_boundaries=[]
    for o in ob:
        s=shape(o[4])
        #print(s,type(s))
        if s.contains(p)==True:
            final_areas.append(o)
        else:
            line=LinearRing(list(s.exterior.coords))
            if line.contains(p):
                final_boundaries.append(o)
     #Check if in Boundary
    if len(final_areas)==0 and len(final_boundaries)!=0:
        #print("in Boundary")
        return final_boundaries
    return final_areas

def check_earth_distance_self(latitude,longitude,radius):
    locations=generalQuery("SELECT * FROM locations",args=None)
    result=[]
    for loc in locations:
        coord1=(latitude,longitude)
        coord2 = (loc[4], loc[5])
        r = geopy.distance.distance(coord1, coord2).m
        if r <=radius:
            #print(loc)
            result.append(loc)
    return result

def insert_csv(csv_file_path):
    db=db_connect()
    #cu=cursor_init(db)
    with open(csv_file_path) as f:
        csv_reader=csv.reader(f)
        for n,c in enumerate(csv_reader):
            if c[3]=='':
                c[3]=0
                c[4]=0
            dict={"ID":n+1,"PINCODE":str(c[0]),"NAME":str(c[1]),"STATE":str(c[2]),"LATITUDE":float(c[3]),"LONGITUDE":float(c[4])}
            print(dict)
            #insertQuery('locations',dict,db)
            time.sleep(0.05)

def insert_json(json_file_path):
    db=db_connect()
    #cu=cursor_init(db)
    with open(json_file_path) as f:
        data=json.load(f)
        data=data.get('features')
        for n,c in enumerate(data):



            polygon=c.get('geometry')
            #print(polygon[0])
            c=c.get('properties')

            dict = {"ID": n + 1, "NAME": str(c.get('name')), "TYPE": str(c.get('type')), "PARENT": str(c.get('parent')),"POLYGON_BOUNDARY":json.dumps(polygon)}
            print(dict)
            #insertQuery('areas',dict,db)
            lat=28.4908
            long=77.0690
            check_point_polygon(dict.get("POLYGON_BOUNDARY"),lat,long)
            #generalQuery(query,db,args=None)
            time.sleep(0.1)



TABLE_1="""
CREATE TABLE LOCATIONS(
   ID SERIAl PRIMARY KEY     ,
   PINCODE           TEXT    NOT NULL,
   NAME            TEXT     NOT NULL,
   STATE        TEXT NOT NULL,
   LATITUDE float NOT NULL,
   LONGITUDE float NOT NULL,
   ACURRACY INT
);
"""
TABLE_2="""
CREATE TABLE AREAS(
   ID SERIAl PRIMARY KEY     ,
   NAME            TEXT     NOT NULL,
   TYPE        TEXT NOT NULL,
   PARENT TEXT NOT NULL,
   POLYGON_BOUNDARY JSON
);
"""
#query2="INSERT INTO locations values (%i,%s,%s,%s,%f,%f);"
#args=(3,'IN/202390','Danpur','Uttar Pradesh',23.5167,74.7167,4)
#query3="UPDATE areas SET POLYGON_BOUNDARY"
#res=generalQuery(queryy,db=db_connect(),args=None)

#res=check_earth_distance(15.2,73.9,50000)
#print(res)
#insert_csv('IN.csv')
