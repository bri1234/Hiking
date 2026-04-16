# type: ignore

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

import random
from staticmap import StaticMap, CircleMarker, Line 
from convert_fit_to_gpx import ReadFitFile, GetTrackPointsFromMessages

def CreateImageOverviewMap(fit_filename : str,
                           output_filename : str,
                           img_width : int, img_height : int,
                           zoom : int = 8,
                           path_color : str = "red", path_width : int = 3) -> None:
    """ Creates an overview image showing a specific area on the map.

    Args:
        fit_filename (str): The FIT file containing the track data.
        output_filename (str): The image output filename. (PNG)
        img_width (int): The image width in pixels.
        img_height (int): The image height in pixels.
        zoom (int): The zoom level of the map.
    """
    fitMessages = ReadFitFile(fit_filename)
    pointList = GetTrackPointsFromMessages(fitMessages)

    server_list = [ "a", "b", "c" ]
    server = server_list[random.randint(0, len(server_list) - 1)]

    url_tmp = "https://" + server + ".tile.opentopomap.org/{z}/{x}/{y}.png"

    map = StaticMap(img_width, img_height, url_template=url_tmp)

    centerLongitude = 0.0
    centerLatitude = 0.0
    cnt = 0

    for idx in range(1, len(pointList) - 3):
        p1 = pointList[idx - 1]
        p2 = pointList[idx]
        line = Line( ( (p1.Longitude, p1.Latitude), (p2.Longitude, p2.Latitude)), path_color, path_width )
        map.add_line(line)

        centerLongitude += p1.Longitude
        centerLatitude += p1.Latitude
        cnt += 1

    centerLongitude /= cnt
    centerLatitude /= cnt
    center = (centerLongitude, centerLatitude)

    map.add_marker(CircleMarker(center, "red", 15))

    image = map.render(zoom=zoom, center=center)
    image.save(output_filename)

# for testing only
if __name__ == "__main__":
    CreateImageOverviewMap("test.fit", "germany.png", 400, 400, zoom=8)

