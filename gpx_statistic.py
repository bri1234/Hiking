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
    """ Converts timespan in seconds to hours, minutes and seconds.

    Args:
        timeSpan (float): The timespan in seconds.

    Returns:
        tuple[int, int, int]: The timespan in hours, minutes, seconds.
    """
    hours = int(timeSpan // 3600)
    minutes = int(timeSpan % 3600 // 60)
    seconds = int(timeSpan % 60)

    return hours, minutes, seconds

def ShowGpxFileStatistic(filename : str) -> None:
    """ Shows 

    Args:
        filename (str): _description_
    """

    with open(filename, "r") as file:
        gpx = gpxpy.parse(file)
    
    moving_time, stopped_time, moving_distance, _, max_speed = gpx.get_moving_data(stopped_speed_threshold=0.1)

    print(f"Track length: {moving_distance / 1000:.2f} km")

    hours, minutes, _ = TimespanToHoursMinutesSeconds(moving_time)
    print(f"Moving time: {hours} Hours {minutes:02d} Minutes")

    hours, minutes, _ = TimespanToHoursMinutesSeconds(stopped_time)
    print(f"Pause time: {hours} Hours {minutes:02d} Minutes")

    print(f"Maximum speed: {max_speed * 3.6:.1f} km/h")
    
    print(f"Number of GPS points: {gpx.get_points_no()}")

    minElevation, maxElevation = gpx.get_elevation_extremes()
    print(f"Minimum altitude: {minElevation:.1f} m Maximum altitude: {maxElevation:.1f} m")

    cloned_gpx = gpx.clone()
    cloned_gpx.reduce_points(cloned_gpx.get_points_no() // 2, min_distance=10)
    cloned_gpx.smooth()
    print(f"Number of GPS points smoothed: {cloned_gpx.get_points_no()}")
    
    # xml = cloned_gpx.to_xml()
    # with open("test.gpx", "w") as file:
    #     file.write(xml)

if __name__ == "__main__":

    # ShowGpxFileStatistic('2025-05-09 10.08.20.gpx')

    argParser = argparse.ArgumentParser("gpx_statistic", description="Calculates track statistic from GPX file.")
    argParser.add_argument("filename", help='input filename "abc.GPX"')
    args = argParser.parse_args()

    ShowGpxFileStatistic(args.filename)
