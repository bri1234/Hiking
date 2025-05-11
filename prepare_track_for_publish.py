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
from convert_fit_to_gpx import ReadFitFile, GetTrackPointsFromMessages, TrackPoint
from gpx_statistic import TimespanToHoursMinutesSeconds
from pathlib import Path

def CreateGpxTrackFromFitActivity(fitFilename : str) -> tuple[gpxpy.gpx.GPX, list[TrackPoint]]:
    """ Converts FIT activity track to GPX track.

    Args:
        fitFilename (str): The FIT activity filename.

    Returns:
        gpxpy.gpx.GPX: The GPX track.
    """
    messages = ReadFitFile(fitFilename)
    pointList = GetTrackPointsFromMessages(messages)

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

    return gpx, pointList

def OutputStatistic(gpx : gpxpy.gpx.GPX, filename : str) -> None:
    """ Creates a HTML table with the track statistic and saves it.

    Args:
        gpx (gpxpy.gpx.GPX): The track.
        filename (str): The filename for the HTML track statistic.
    """
    moving_time, _, moving_distance, _, _ = gpx.get_moving_data(stopped_speed_threshold=0.1)

    with open(filename, "w") as file:
        file.write("<table>\n")
        file.write("<tr>\n")

        hours, minutes, _ = TimespanToHoursMinutesSeconds(moving_time)
        file.write(f"<td>Dauer:</td><td>{hours} Stunden {minutes:02d} Minuten</td>\n")

        file.write(f"<td>Länge:</td><td>{moving_distance / 1000:.1f} km</td>\n")

        minElevation, maxElevation = gpx.get_elevation_extremes()
        if maxElevation is None or minElevation is None:
            raise Exception("missing GPS elevation data")
        
        file.write(f"<td>Höhenunterschied:</td><td>{(maxElevation - minElevation):.1f} m</td>\n")
        
        file.write("</tr>\n")

        file.write("<tr>\n")
        file.write("<td>Schwierigkeitsgrad:</td><td></td>\n")
        file.write("<td>Kondition:</td><td></td>\n")
        file.write("<td>Ausrüstung:</td><td></td>\n")
        file.write("</tr>\n")

        file.write("</table>\n")

def OutputSmoothedTrack(gpx : gpxpy.gpx.GPX, filename : str) -> None:
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

def OutputAltitudeProfile(points : list[TrackPoint], filename : str) -> None:
    """ Creates an altutude profile image and saves it (PNG image).

    Args:
        gpx (gpxpy.gpx.GPX): The track.
        filename (str): The filename for the PNG image.
    """
    pass
    

def PrepareTrackForPublish(fitFilename : str) -> None:
    """ Prepares the track for publishing: creates statistic, high profile and a smoothed GPX track.

    Args:
        fitFilename (str): the FIT activity filename.
    """

    gpx, points = CreateGpxTrackFromFitActivity(fitFilename)

    OutputStatistic(gpx, str(Path(fitFilename).with_suffix(".html")))
    OutputSmoothedTrack(gpx, str(Path(fitFilename).with_suffix(".gpx")))
    OutputAltitudeProfile(points, str(Path(fitFilename).with_suffix(".png")))

if __name__ == "__main__":

    argParser = argparse.ArgumentParser("prepare_track_for_publish", description="Prepares the track for publishing: creates statistic, high profile and a smoothed GPX track.")
    argParser.add_argument("filename", help='input filename "abc.FIT"')
    args = argParser.parse_args()

    PrepareTrackForPublish(args.filename)
