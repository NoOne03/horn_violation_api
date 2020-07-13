from flask import Flask, request, make_response, Response
from os import environ
from dotenv import load_dotenv
import requests
import pandas as pd
import matplotlib.pyplot as plt
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg

# Load authentication details from .env
load_dotenv()
API_KEY = environ.get('API_KEY')

app=Flask(__name__)

# API for single data request
@app.route('/', methods=['POST'])
def horn():
    lat = request.form['lat']
    lon = request.form['lon']
    radius = request.form['radius']
    res = requests.get('https://api.tomtom.com/search/2/categorySearch/school%2Fcollege%2Funiversity%2Fhospital.JSON?key={}&countrySet=IND&lat={}&lon={}&radius={}'.format(API_KEY,lat,lon,radius)) 
    if res.ok:
        py_res = res.json()
        n = len(py_res["results"])
        data={}
        data['data']=[]
        for x in range(n):
            distance = py_res["results"][x]["dist"]
            violation = 'YES' if (distance<=100) else 'NO'
            data['data'].append({'name':py_res["results"][x]["poi"]["name"],'distance':distance,'violation':violation})
        response = make_response(data,200)
        return response
    else:
        return "Failed!!"
    
# API for multiple data request in csv 
@app.route('/csv',methods=['POST'])
def horn_csv():
    file = request.files['file']
    cordinates = pd.read_csv(file)
    total = len(cordinates['lat'])
    violations=0
    for cord in range(total):
        lat = cordinates['lat'][cord]
        lon = cordinates['lon'][cord]
        radius = 100
        res = requests.get('https://api.tomtom.com/search/2/categorySearch/school%2Fcollege%2Funiversity%2Fhospital.JSON?key={}&countrySet=IND&lat={}&lon={}&radius={}'.format(API_KEY,lat,lon,radius))
        if res.ok:
            py_res=res.json()
            n=len(py_res["results"])
            data={}
            data['data']=[]
            for x in range(n):
                if(py_res["results"][x]["dist"]<=100):
                        violations=violations+1
                        break
    fig,ax=plt.subplots()
    plt.bar(('YES','NO'),(violations,total-violations),width=0.2)
    plt.xlabel('Violation')
    plt.ylabel('Count')
    plt.title('Horn Violation Result')
    output = io.BytesIO()
    FigureCanvasAgg(fig).print_png(output)
    return Response(output.getvalue(), mimetype="image/png")

app.run()