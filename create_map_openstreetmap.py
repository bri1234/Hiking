# type: ignore

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

import random
from staticmap import StaticMap, Line 
from convert_fit_to_gpx import ReadFitFile, GetTrackPointsFromMessages

def CreateImageWithTrackOnMap(fit_filename : str, output_filename : str,
                          img_width : int, img_height : int,
                          path_color : str = "red", path_width : int = 3) -> None:
    """ Creates an image from a track on a map with Open street map.

    Args:
        fit_filename (str): The garmin activity filename.
        output_filename (str): The image output filename. (PNG)
        img_width (int): The image widht in pixels.
        img_height (int): The image high in pixels.
        path_color (str, optional): The track color (suitable for PIL/Pillow, e.g. red, blue). Defaults to "red".
        path_width (int, optional): The track width. Defaults to 3.
    """
    fitMessages = ReadFitFile(fit_filename)
    pointList = GetTrackPointsFromMessages(fitMessages)

    server_list = [ "a", "b", "c" ]
    server = server_list[random.randint(0, len(server_list) - 1)]

    url_tmp = "https://" + server + ".tile.openstreetmap.de/{z}/{x}/{y}.png"
    #url_tmp = "https://" + server + ".tile.openstreetmap.org/{z}/{x}/{y}.png"
    #url_tmp = "https://" + server + ".tile.opentopomap.org/{z}/{x}/{y}.png"

    map = StaticMap(img_width, img_height, url_template=url_tmp)

    for idx in range(1, len(pointList) - 3):
        p1 = pointList[idx - 1]
        p2 = pointList[idx]
        line = Line( ( (p1.Longitude, p1.Latitude), (p2.Longitude, p2.Latitude)), path_color, path_width )
        map.add_line(line)

    image = map.render()
    image.save(output_filename)

if __name__ == "__main__":
    CreateImageWithTrackOnMap("Pfaffenstein Quirl.fit", "map5.png", 800, 600, "red", 3)

