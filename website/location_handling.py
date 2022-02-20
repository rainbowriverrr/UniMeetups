from math import radians,cos,sin,asin,sqrt
import googlemaps as gmaps
from replit import db
import geocoder

GEO_KEY = "AIzaSyAA0vrb6JeeS7-hE-CvExFSdhlIEoCmOBw"

client = gmaps.Client(key=GEO_KEY)


def populate_schools():
  '''Populate all the schools in the database'''
  with open("schools.txt","r") as file:
    schools = file.read().splitlines()
    university_locations = {}
    for school in schools:
      geo_res = client.find_place(school,input_type="textquery")
      place_id = geo_res["candidates"][0]["place_id"]
      uni_info = client.place(place_id)
      university_locations[school] = uni_info["result"]["geometry"]["location"]
    
    db["schools"] = university_locations



def get_closest_schools(user_ip):
  user_location = geocoder.ip(user_ip)
  lat,long = user_location.latlng
  distances = {}

  unis = db["schools"]
  
  for uni in unis:
    uni_lat = unis[uni]["lat"]
    uni_long = unis[uni]["lng"]
    pos_dist = distance(lat, uni_lat, long, uni_long)
    distances[uni] = pos_dist

  all_distances = list(distances.values())
  all_distances.sort()
  top_three = all_distances[0:3]
  closest_schools = []
  
  for school in distances:
    if distances[school] in top_three:
      closest_schools.append(school)

  return closest_schools

def distance(lat1, lat2, lon1, lon2):
    # reference: https://www.geeksforgeeks.org/program-distance-two-points-earth/
  
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
      
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
 
    c = 2 * asin(sqrt(a))
    
    r = 6371
      

    return c * r

