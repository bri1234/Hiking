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

import requests
import json
from prepare_track_for_publish import CreateGpxTrackFromFitActivity

def __ReadGoogleApiKey() -> str:
    """ Reads the Google API key from file.
    The google API key is stored in the file "google_api_key.json"
    Example:

    {
        "google_api_key" : "hdfdhtjtzjtzuz574rtge5345tgedsf"
    }

    Returns:
        str: The Google maps API key.
    """
    with open("google_api_key.json") as file:
        return json.load(file)["google_api_key"]

def __MakeGpxTrackAndCenterIt(fitFilename : str) -> tuple[str, float, float]:
    """ Reads a track from a garmin activity file and centers it.

    Args:
        fitFilename (str): The garmin activity filename.

    Returns:
        str: The pointlist as a string.
        float: The track center latitude.
        float: The track center longitude.
    """
    track = CreateGpxTrackFromFitActivity(fitFilename)
    min_lat, max_lat, min_long, max_long = track.get_bounds()   # type: ignore
    center_latitude : float = (min_lat + max_lat) / 2           # type: ignore
    center_longitude : float = (min_long + max_long) / 2        # type: ignore

    track.reduce_points(600, 10)

    point_list : list[str] = []

    for p in track.get_points_data():
        point_list.append(f"{p.point.latitude:.6f},{p.point.longitude:.6f}")

    return "|".join(point_list), center_latitude, center_longitude # type: ignore

def __CreateAndSaveMapImage(img_filename : str, center_latitude : float, center_longitude : float,
             img_width : int, img_height : int, map_type : str,
             path_points : str, path_color : str = "0xFF000080", path_width : int = 3) -> None:
    """ Creates the map with the track and stores it in an image file.

    Args:
        img_filename (str): The name of the image file. (PNG)
        center_latitude (float): The track center latitude.
        center_longitude (float): The track center longitude.
        img_width (int): The image widht in pixels.
        img_height (int): The image high in pixels.
        map_type (str): The map type: roadmap, terrain, satellite, hybrid.
        path_points (str): The track points.
        path_color (str, optional): The track color in RGBA. Defaults to "0xFF000080".
        path_width (int, optional): The track width. Defaults to 3.

    """

    imgFormat = "PNG"
    googleApiKey = __ReadGoogleApiKey()

    query = f"https://maps.googleapis.com/maps/api/staticmap?center={center_latitude},{center_longitude}&size={img_width}x{img_height}&maptype={map_type}&format={imgFormat}&key={googleApiKey}&path=color:{path_color}|weight:{path_width}|{path_points}"

    r = requests.get(query)

    if r.status_code != 200:
        raise Exception(f"ERROR: HTTP response {r.status_code}")

    with open(img_filename, "wb") as file:
        file.write(r.content)

def CreateImageWithTrackOnMap(fit_filename : str, output_filename : str,
                          img_width : int, img_height : int, map_type : str,
                          path_color : str = "0xFF000080", path_width : int = 3) -> None:
    """ Creates an image from a track on a map with Google Maps.

    Args:
        fit_filename (str): The garmin activity filename.
        output_filename (str): The image output filename. (PNG)
        img_width (int): The image widht in pixels.
        img_height (int): The image high in pixels.
        map_type (str): The map type: roadmap, terrain, satellite, hybrid.
        path_color (str, optional): The track color in RGBA. Defaults to "0xFF000080".
        path_width (int, optional): The track width. Defaults to 3.
    """
    track, center_latitude, center_longitude = __MakeGpxTrackAndCenterIt(fit_filename)
    __CreateAndSaveMapImage(output_filename, center_latitude, center_longitude, img_width, img_height, map_type, track, path_color, path_width)

if __name__ == "__main__":

    CreateImageWithTrackOnMap("Pfaffenstein Quirl.fit", "map1.png", 800, 600, "hybrid", "0xFF000080", 3)
    CreateImageWithTrackOnMap("Pfaffenstein Quirl.fit", "map2.png", 800, 600, "roadmap", "0xFF000080", 3)
    CreateImageWithTrackOnMap("Pfaffenstein Quirl.fit", "map3.png", 800, 600, "terrain", "0xFF000080", 3)
    CreateImageWithTrackOnMap("Pfaffenstein Quirl.fit", "map4.png", 800, 600, "satellite", "0xFF000080", 3)



