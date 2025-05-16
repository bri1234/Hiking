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

with open("google_api_key.json") as file:
    __GOOGLE_API_KEY = json.load(file)["google_api_key"]

__IMG_FORMAT = "PNG"

def GetGpxTrackAndCenter(fitFilename : str) -> tuple[str, float, float]:

    track = CreateGpxTrackFromFitActivity(fitFilename)
    min_lat, max_lat, min_long, max_long = track.get_bounds()   # type: ignore
    center_latitude : float = (min_lat + max_lat) / 2           # type: ignore
    center_longitude : float = (min_long + max_long) / 2        # type: ignore

    track.reduce_points(600, 10)

    point_list : list[str] = []

    for p in track.get_points_data():
        point_list.append(f"{p.point.latitude:.6f},{p.point.longitude:.6f}")

    return "|".join(point_list), center_latitude, center_longitude # type: ignore

def StoreMap(img_filename : str, center_latitude : float, center_longitude : float,
             img_width : int, img_height : int, map_type : str,
             path_points : str, path_color : str = "0xFF000080", path_weight : int = 3) -> None:

    # roadmap, terrain, satellite, hybrid
    # RGBA

    query = f"https://maps.googleapis.com/maps/api/staticmap?center={center_latitude},{center_longitude}&size={img_width}x{img_height}&maptype={map_type}&format={__IMG_FORMAT}&key={__GOOGLE_API_KEY}&path=color:{path_color}|weight:{path_weight}|{path_points}"

    r = requests.get(query)

    if r.status_code != 200:
        raise Exception(f"ERROR: HTTP response {r.status_code}")

    with open(img_filename, "wb") as file:
        file.write(r.content)

if __name__ == "__main__":

    fitFilename = "Pfaffenstein Quirl.fit"

    track, center_latitude, center_longitude = GetGpxTrackAndCenter(fitFilename)
    StoreMap("map.png", center_latitude, center_longitude, 800, 600, "hybrid", track)

