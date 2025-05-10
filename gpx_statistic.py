"""

Copyright (C) 2025  Torsten Brischalle
email: torsten@brischalle.de
web: http://www.aaabbb.de

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to
deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""

import gpxpy
import argparse

def TimespanToHoursMinutesSeconds(timeSpan : float) -> tuple[int, int, int]:
    hours = int(timeSpan // 3600)
    minutes = int(timeSpan % 3600 // 60)
    seconds = int(timeSpan % 60)

    return hours, minutes, seconds

def ReadGpxFile(fileName : str) -> None:

    with open(fileName, "r") as file:
        gpx = gpxpy.parse(file)
    
    moving_time, stopped_time, moving_distance, _, max_speed = gpx.get_moving_data(stopped_speed_threshold=0.1)

    print(f"Streckenlänge: {moving_distance / 1000:.2f} km")

    hours, minutes, _ = TimespanToHoursMinutesSeconds(moving_time)
    print(f"Wanderzeit: {hours} Stunden {minutes:02d} Minuten")

    hours, minutes, _ = TimespanToHoursMinutesSeconds(stopped_time)
    print(f"Pausenzeit: {hours} Stunden {minutes:02d} Minuten")

    print(f"Maximale Geschwindigkeit: {max_speed * 3.6:.1f} km/h")
    
    print(f"Anzahl GPS Punkte: {gpx.get_points_no()}")

    minElevation, maxElevation = gpx.get_elevation_extremes()
    print(f"Minimale Höhe: {minElevation:.1f} m Maximale Höhe: {maxElevation:.1f} m")

    cloned_gpx = gpx.clone()
    cloned_gpx.reduce_points(cloned_gpx.get_points_no() // 2, min_distance=10)
    cloned_gpx.smooth()
    print(f"Anzahl GPS Punkte geglättet: {cloned_gpx.get_points_no()}")
    
    xml = cloned_gpx.to_xml()
    with open("test.gpx", "w") as file:
        file.write(xml)

if __name__ == "__main__":

    # ReadGpxFile('2025-05-09 10.08.20.gpx')

    argParser = argparse.ArgumentParser("gpx_statistic", description="Calculates track statistic from GPX file.")
    argParser.add_argument("filename", help='input filename "abc.GPX"')
    args = argParser.parse_args()

    ReadGpxFile(args.filename)
