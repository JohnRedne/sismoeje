# -*- coding: utf-8 -*-
"""Untitled39.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ksMno3B0QB-Qf9RRXjNA6TWH6M0CG4DW
"""

from flask import Flask, request, jsonify, send_file
import urllib.request
import io
from obspy import read, UTCDateTime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

app = Flask(__name__)

def date_to_julian_day(date: str) -> int:
    dt = datetime.fromisoformat(date)
    start_of_year = datetime(dt.year, 1, 1)
    return (dt - start_of_year).days + 1

@app.route('/generate_sismograma', methods=['GET'])
def get_sismograma():
    try:
        start_date_input = request.args.get('start_date')
        end_date_input = request.args.get('end_date')
        net = request.args.get('net')
        sta = request.args.get('sta')
        channel = "HNE.D"  # Canal fijo

        start_date = datetime.fromisoformat(start_date_input)
        end_date = datetime.fromisoformat(end_date_input)

        if start_date == end_date:
            start_date += timedelta(seconds=20)
            end_date -= timedelta(seconds=10)

        if (end_date - start_date) > timedelta(minutes=15):
            end_date = start_date + timedelta(minutes=15)

        julian_day = date_to_julian_day(start_date.isoformat())
        year = start_date.year

        url = f"http://osso.univalle.edu.co/apps/seiscomp/archive/{year}/{net}/{sta}/{channel}/{net}.{sta}.00.{channel}.{year}.{julian_day}"
        response = urllib.request.urlopen(url)
        stream = read(io.BytesIO(response.read()))

        start_utc = UTCDateTime(start_date)
        end_utc = UTCDateTime(end_date)
        stream = stream.slice(starttime=start_utc, endtime=end_utc)

        trace = stream[0]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(trace.times("matplotlib"), trace.data, label=f"Canal {channel}", color='blue')
        ax.set_title(f"Sismograma {channel} ({sta})")
        ax.set_xlabel("Tiempo (UTC)")
        ax.set_ylabel("Amplitud")
        ax.grid()
        ax.legend()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S UTC'))
        fig.autofmt_xdate()

        img_path = "sismograma.png"
        plt.savefig(img_path)
        plt.close()

        return send_file(img_path, mimetype='image/png')
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
