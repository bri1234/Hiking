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

messages = ReadFitFile("2025-05-09 10.08.20.fit")
pointList = GetTrackPointsFromMessages(messages)

server_list = [ "a", "b", "c" ]
server = server_list[random.randint(0, len(server_list) - 1)]

#url_tmp = f"https://" + server + ".tile.openstreetmap.org/{z}/{x}/{y}.png"
url_tmp = "https://" + server + ".tile.openstreetmap.de/{z}/{x}/{y}.png"
#url_tmp = f"https://" + server + ".tile.opentopomap.org/{z}/{x}/{y}.png"

m = StaticMap(1000, 1000, url_template=url_tmp)

for idx in range(1, len(pointList) - 3):
    p1 = pointList[idx - 1]
    p2 = pointList[idx]
    line = Line( ( (p1.Longitude, p1.Latitude), (p2.Longitude, p2.Latitude)), 'blue', 2 )
    m.add_line(line)

image = m.render()
image.save('map.png')
