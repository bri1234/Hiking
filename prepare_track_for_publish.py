#!/usr/bin/python3

"""

Copyright (C) 2026  Torsten Brischalle
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
from convert_fit_to_gpx import CreateGpxTrackFromFitActivity
from gpx_statistic import TimespanToHoursMinutesSeconds
from pathlib import Path
import matplotlib.pyplot as plt
import math
import create_map_googlemaps_js as create_map_googlemaps
import create_map_openstreetmap
import create_overview_map

stoppedSpeedThreshold = 0.15

ALTITUDE_PROFILE_IMG_WIDTH = 1000
ALTITUDE_PROFILE_IMG_HEIGHT = 200

MAP_PREVIEW_IMG_WIDTH = 400
MAP_PREVIEW_IMG_HEIGHT = 400

MAP_IMG_WIDTH = 1500
MAP_IMG_HEIGHT = 1500


def SaveAllTrackInfosAsHtml(gpx : gpxpy.gpx.GPX, filename : str, name : str) -> None:
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

    hours_pause, minutes_pause, _ = TimespanToHoursMinutesSeconds(stopped_time)
    print(f"Pause time: {hours_pause} Hours {minutes_pause:02d} Minutes")

    print(f"Maximum speed: {max_speed * 3.6:.1f} km/h")
    
    print(f"Number of GPS points: {gpx.get_points_no()}")

    minElevation, maxElevation = gpx.get_elevation_extremes()
    if maxElevation is None or minElevation is None:
        raise Exception("missing GPS elevation data")
    
    print(f"Minimum altitude: {minElevation:.1f} m Maximum altitude: {maxElevation:.1f} m")
    print(f"Höhenunterschied: {maxElevation - minElevation:.1f} m")

    uphill, downhill = gpx.get_uphill_downhill()
    print(f"Uphill: {uphill:.1f} m downhill: {downhill:.1f} m")

    base = f"/{name}_published/{name}"

    html_code = f"""
<div class="wp-block-columns is-layout-flex wp-container-core-columns-is-layout-9d6595d7 wp-block-columns-is-layout-flex">
    <div class="wp-block-column is-layout-flow wp-block-column-is-layout-flow">
        <figure class="wp-block-image size-large">
            <a href="{base}_map1.png">
                <img decoding="async" src="{base}_map_preview1.png" alt=""/>
            </a>
        </figure>
    </div>
    <div class="wp-block-column is-layout-flow wp-block-column-is-layout-flow">
        <figure class="wp-block-image size-large">
            <a href="{base}_map2.jpg">
                <img decoding="async" src="{base}_map_preview2.jpg" alt=""/>
            </a>
        </figure>
    </div>
    <div class="wp-block-column is-layout-flow wp-block-column-is-layout-flow">
        <figure class="wp-block-image size-large">
            <a href="{base}_overview_large.jpg">
                <img decoding="async" src="{base}_overview.jpg" alt=""/>
            </a>
        </figure>
    </div>
</div>
<figure class="wp-block-table">
    <table class="has-fixed-layout">
        <tbody>
            <tr>
                <td><strong>Länge:</strong></td><td>{moving_distance / 1000:.1f} km</td>
                <td><strong>Dauer:</strong></td><td>{hours} h {minutes:02d} min</td>
            </tr>
            <tr>
                <td><strong>&Oslash; Geschwindigkeit:</strong></td><td>{moving_distance / moving_time * 3.6:.1f} km/h</td>
                <td><strong>Höhenunterschied:</strong></td><td>{maxElevation - minElevation:.1f} m</td>
            </tr>
            <tr>
                <td><strong>Minimale Höhe:</strong></td><td>{minElevation:.1f} m</td>
                <td><strong>Maximale Höhe:</strong></td><td>{maxElevation:.1f} m</td>
            </tr>
            <tr>
                <td><strong>Bergauf:</strong></td><td>{uphill:.1f} m</td>
                <td><strong>Bergab:</strong></td><td>{downhill:.1f} m</td>
            </tr>
            <tr>
                <td><strong>GPX Track</strong></td><td><a href="{base}.gpx">{name}.gpx</a></td>
            </tr>
        </tbody>
    </table>
</figure>
<figure class="wp-block-image size-large">
    <img decoding="async" src="{base}_altitude.png" alt=""/>
</figure>
"""
    
    with open(filename, "w") as file:
        file.write(html_code)

def SaveSmoothedTrackAsGpx(gpx : gpxpy.gpx.GPX, filename : str) -> gpxpy.gpx.GPX:
    """ Creates a smoothed track and saves it.

    Args:
        gpx (gpxpy.gpx.GPX): The track.
        filename (str): The filename for the smoothed track.
    """
    cloned_gpx = gpx.clone()
    cloned_gpx.reduce_points(gpx.get_points_no() // 2, min_distance=10)
    cloned_gpx.smooth()

    xml = cloned_gpx.to_xml()
    with open(filename, "w") as file:
        file.write(xml)

    return cloned_gpx

def SaveAltitudeProfileImage(gpx : gpxpy.gpx.GPX, filename : str, width : int, height : int) -> None:
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

    # plt.show() # type: ignore

def PrepareTrackForWordpressPublish(fitFilepath : str, altitudeProfileImgWidth : int, altitudeProfileImgHeight : int,
                           mapPreviewImgWidth : int, mapPreviewImgHeight : int,
                           mapImgWidth : int, mapImgHeight : int,
                           removePointsBegin : int = 0, removePointsEnd : int = 0) -> None:
    """ Prepares the track for publishing on Wordpress: creates statistic, high profile and a smoothed GPX track.

    Args:
        fitFilename (str): the FIT activity filename.
    """

    name = Path(fitFilepath).stem
    basedir = str(Path(fitFilepath).with_suffix("")) + "_published"
    Path(basedir).mkdir(exist_ok=True)
    basepath = str(Path(basedir).joinpath(name))

    gpx = CreateGpxTrackFromFitActivity(fitFilepath, removePointsBegin, removePointsEnd)

    SaveAllTrackInfosAsHtml(gpx, basepath + ".html", name)

    smoothedTrack = SaveSmoothedTrackAsGpx(gpx, basepath + ".gpx")

    SaveAltitudeProfileImage(smoothedTrack, basepath + "_altitude.png", altitudeProfileImgWidth, altitudeProfileImgHeight)

    track_color = "#E00000"

    # print("create preview maps ...")
    create_map_openstreetmap.CreateImageWithTrackOnMap(fitFilepath, basepath + "_map_preview1.png", mapPreviewImgWidth, mapPreviewImgHeight, "red", 3)
    create_map_googlemaps.CreateImageWithTrackOnMap(fitFilepath, basepath + "_map_preview2.jpg", mapPreviewImgWidth, mapPreviewImgHeight, "hybrid", track_color, 3)
    # create_map_googlemaps.CreateImageWithTrackOnMap(fitFilepath, basepath + "_map_preview3.png", mapPreviewImgWidth, mapPreviewImgHeight, "terrain", track_color, 3)

    # print("create maps ...")
    create_map_openstreetmap.CreateImageWithTrackOnMap(fitFilepath, basepath + "_map1.png", mapImgWidth, mapImgHeight, "red", 3)
    create_map_googlemaps.CreateImageWithTrackOnMap(fitFilepath, basepath + "_map2.jpg", 1280, 1280, "hybrid", track_color, 3)
    # create_map_googlemaps.CreateImageWithTrackOnMap(fitFilepath, basepath + "_map3.png", 1280, 1280, "terrain", track_color, 3)

    create_overview_map.CreateImageOverviewMap(fitFilepath, basepath + "_overview.jpg", mapPreviewImgWidth, mapPreviewImgHeight, zoom=8, path_color=track_color, path_width=3)
    create_overview_map.CreateImageOverviewMap(fitFilepath, basepath + "_overview_large.jpg", mapImgWidth, mapImgHeight, zoom=7, path_color=track_color, path_width=3)

    print("done")

###################################################################################################
# The standalone application starts here.
###################################################################################################

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

    PrepareTrackForWordpressPublish(args.filename,
                           ALTITUDE_PROFILE_IMG_WIDTH, ALTITUDE_PROFILE_IMG_HEIGHT,
                           MAP_PREVIEW_IMG_WIDTH, MAP_PREVIEW_IMG_HEIGHT,
                           MAP_IMG_WIDTH, MAP_IMG_HEIGHT,
                           removePointsBegin, removePointsEnd)
