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
import gpxpy.gpx
import argparse
from convert_fit_to_gpx import ReadFitFile, GetTrackPointsFromMessages
from gpx_statistic import TimespanToHoursMinutesSeconds
from pathlib import Path
import matplotlib.pyplot as plt
import math

stoppedSpeedThreshold = 0.15

def CreateGpxTrackFromFitActivity(fitFilename : str, removePointsBegin : int = 0, removePointsEnd : int = 0) -> gpxpy.gpx.GPX:
    """ Converts FIT activity track to GPX track.

    Args:
        fitFilename (str): The FIT activity filename.

    Returns:
        gpxpy.gpx.GPX: The GPX track.
    """
    messages = ReadFitFile(fitFilename)
    pointList = GetTrackPointsFromMessages(messages)

    if removePointsBegin > 0:
        pointList = pointList[removePointsBegin : ]

    if removePointsEnd > 0:
        pointList = pointList[ : -removePointsEnd]

    gpx = gpxpy.gpx.GPX()

    # create a track
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    # create a segment
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    # add points
    for p in pointList:
        point = gpxpy.gpx.GPXTrackPoint(p.Latitude, p.Longitude, elevation=p.Altitude, time=p.Time)
        gpx_segment.points.append(point)

    return gpx

def OutputStatistic(gpx : gpxpy.gpx.GPX, filename : str) -> None:
    """ Creates a HTML table with the track statistic and saves it.

    Args:
        gpx (gpxpy.gpx.GPX): The track.
        filename (str): The filename for the HTML track statistic.
    """
    moving_time, stopped_time, moving_distance, _, max_speed = gpx.get_moving_data(stopped_speed_threshold=stoppedSpeedThreshold)

    print(f"Track length: {moving_distance / 1000:.2f} km")

    hours, minutes, _ = TimespanToHoursMinutesSeconds(moving_time)
    print(f"Moving time: {hours} Hours {minutes:02d} Minutes")

    print(f"Average speed: {moving_distance / moving_time * 3.6:.1f} km/h")

    hours, minutes, _ = TimespanToHoursMinutesSeconds(stopped_time)
    print(f"Pause time: {hours} Hours {minutes:02d} Minutes")

    print(f"Maximum speed: {max_speed * 3.6:.1f} km/h")
    
    print(f"Number of GPS points: {gpx.get_points_no()}")

    minElevation, maxElevation = gpx.get_elevation_extremes()
    print(f"Minimum altitude: {minElevation:.1f} m Maximum altitude: {maxElevation:.1f} m")

    with open(filename, "w") as file:
        file.write("<table>\n")
        file.write("<tr>\n")

        hours, minutes, _ = TimespanToHoursMinutesSeconds(moving_time)
        file.write(f"<td>Dauer:</td><td>{hours} Stunden {minutes:02d} Minuten</td>\n")

        file.write(f"<td>Länge:</td><td>{moving_distance / 1000:.1f} km</td>\n")

        file.write(f"<td>Geschwindigkeit:</td><td>{moving_distance / moving_time * 3.6:.1f} km/h</td>\n")

        minElevation, maxElevation = gpx.get_elevation_extremes()
        if maxElevation is None or minElevation is None:
            raise Exception("missing GPS elevation data")
        
        file.write(f"<td>Höhenunterschied:</td><td>{(maxElevation - minElevation):.1f} m</td>\n")
        
        file.write("</tr>\n")

        file.write("<tr>\n")
        file.write("<td>Schwierigkeitsgrad:</td><td></td>\n")
        file.write("<td>Kondition:</td><td></td>\n")
        file.write("<td>Ausrüstung:</td><td></td>\n")
        file.write("<td></td><td></td>\n")
        file.write("</tr>\n")

        file.write("</table>\n")

def OutputSmoothedTrack(gpx : gpxpy.gpx.GPX, filename : str) -> gpxpy.gpx.GPX:
    """ Creates a smoothed track and saves it.

    Args:
        gpx (gpxpy.gpx.GPX): The track.
        filename (str): The filename for the smoothed track.
    """
    cloned_gpx = gpx.clone()
    cloned_gpx.reduce_points(cloned_gpx.get_points_no() // 2, min_distance=10)
    cloned_gpx.smooth()

    xml = cloned_gpx.to_xml()
    with open(filename, "w") as file:
        file.write(xml)

    return cloned_gpx

def OutputAltitudeProfile(gpx : gpxpy.gpx.GPX, filename : str, width : int, height : int) -> None:
    """ Creates an altutude profile image and saves it (PNG image).

    Args:
        gpx (gpxpy.gpx.GPX): The track.
        filename (str): The filename for the PNG image.
    """
    pointList = gpx.get_points_data()
    distance : list[float] = []
    altitude : list[float] = []

    for p in pointList:
        distance.append(p.distance_from_start / 1000)
        altitude.append(p.point.elevation)

    minElevation, maxElevation = gpx.get_elevation_extremes()
    if minElevation is None or maxElevation is None:
        raise Exception("missing GPS altitude")
    
    yMin = math.floor(minElevation / 50) * 50
    yMax = math.ceil(maxElevation / 50) * 50
    if yMax - yMin < 200:
        yMax = yMin + 200
    
    dpi = plt.rcParams["figure.dpi"]
    fig, ax = plt.subplots(figsize=(width / dpi, height / dpi)) # type: ignore
    ax.plot(distance, altitude) # type: ignore
    ax.set_xlabel("Entfernung in km") # type: ignore
    ax.set_ylabel("Höhe in m") # type: ignore
    
    plt.grid() # type: ignore
    plt.fill_between(distance, altitude, color="#9999C0") # type: ignore
    plt.ylim(yMin, yMax) # type: ignore
    
    fig.tight_layout()
    plt.savefig(filename) # type: ignore

    plt.show() # type: ignore

def PrepareTrackForPublish(fitFilename : str, imgWidth : int, imgHeight : int, removePointsBegin : int = 0, removePointsEnd : int = 0) -> None:
    """ Prepares the track for publishing: creates statistic, high profile and a smoothed GPX track.

    Args:
        fitFilename (str): the FIT activity filename.
    """

    gpx = CreateGpxTrackFromFitActivity(fitFilename, removePointsBegin, removePointsEnd)

    OutputStatistic(gpx, str(Path(fitFilename).with_suffix(".html")))
    smoothedTrack = OutputSmoothedTrack(gpx, str(Path(fitFilename).with_suffix(".gpx")))

    OutputAltitudeProfile(smoothedTrack, str(Path(fitFilename).with_suffix(".png")), imgWidth, imgHeight)

if __name__ == "__main__":

    argParser = argparse.ArgumentParser("prepare_track_for_publish", description="Prepares the track for publishing: creates statistic, high profile and a smoothed GPX track.")
    argParser.add_argument("filename", help='input filename "abc.FIT"')
    argParser.add_argument("-rb", "--remove_begin", help="remove number of points from the begin of the track", required=False)
    argParser.add_argument("-re", "--remove_end", help="remove number of points from the end of the track", required=False)
    argParser.add_argument("-sst", "--stopped_speed_threshold", help="threshold speed to differ between move and pause", required=False)
    args = argParser.parse_args()

    removePointsBegin = abs(int(args.remove_begin)) if args.remove_begin is not None else 0
    removePointsEnd = abs(int(args.remove_end)) if args.remove_end is not None else 0

    if removePointsBegin > 0:
        print(f"removing {removePointsBegin} points from the begin of the track")
    if removePointsEnd > 0:
        print(f"removing {removePointsEnd} points from the end of the track")

    if args.stopped_speed_threshold is not None:
        stoppedSpeedThreshold = float(args.stopped_speed_threshold)

    PrepareTrackForPublish(args.filename, 1000, 200, removePointsBegin, removePointsEnd)
