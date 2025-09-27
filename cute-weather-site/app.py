from flask import Flask, render_template, request
import requests

app = Flask(__name__)

def wx_desc(code):
    table = {
        0:"Clear", 1:"Mainly clear", 2:"Partly cloudy", 3:"Overcast",
        45:"Fog", 48:"Depositing rime fog", 51:"Light drizzle", 53:"Drizzle", 55:"Heavy drizzle",
        61:"Light rain", 63:"Rain", 65:"Heavy rain", 66:"Freezing rain", 67:"Heavy freezing rain",
        71:"Light snow", 73:"Snow", 75:"Heavy snow", 77:"Snow grains",
        80:"Rain showers", 81:"Rain showers", 82:"Violent rain showers",
        85:"Snow showers", 86:"Heavy snow showers",
        95:"Thunderstorm", 96:"Thunderstorm w/ hail", 99:"Thunderstorm w/ heavy hail"
    }
    return table.get(code, f"Code {code}")

@app.route("/", methods=["GET"])
def home():
    q = request.args.get("q")
    if not q:
        return render_template("index.html", result=None)

    g = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": q, "count": 1, "language": "en", "format": "json"},
        timeout=15
    ).json()

    if not g.get("results"):
        return render_template("index.html", error="Place not found.", result=None)

    r0 = g["results"][0]
    lat, lon = r0["latitude"], r0["longitude"]

    f = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat, "longitude": lon,
            "current_weather": True,
            "daily": "temperature_2m_max,temperature_2m_min,uv_index_max,precipitation_sum",
            "timezone": "auto"
        },
        timeout=15
    ).json()

    c = f.get("current_weather", {})
    d = f.get("daily", {})

    result = {
        "name": f'{r0.get("name")}, {r0.get("country_code")}',
        "lat": lat, "lon": lon, "tz": f.get("timezone"),
        "temp": c.get("temperature"), "wind": c.get("windspeed"),
        "code": c.get("weathercode"), "desc": wx_desc(c.get("weathercode", -1)),
        "time": c.get("time"),
        "tmax": (d.get("temperature_2m_max") or [None])[0],
        "tmin": (d.get("temperature_2m_min") or [None])[0],
        "uv":   (d.get("uv_index_max") or [None])[0],
        "prcp": (d.get("precipitation_sum") or [None])[0],
    }
    return render_template("index.html", result=result, error=None)

if __name__ == "__main__":
    app.run(debug=True)


