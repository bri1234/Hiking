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

import garmin_fit_sdk as garmin # type: ignore
import xml.dom.minidom as xmd
import argparse
from datetime import datetime
from typing import Any
from pathlib import Path

def SemicircleToDegress(semicircles : int) -> float:
    """ Converts semicircles to degrees.

    Args:
        semicircles (int): semicircles.

    Returns:
        float: degrees.
    """
    return semicircles * 180.0 / (2 ** 31)

def DegreesToSemicircles(degrees : float) -> int:
    """ Converts degrees to semicircles.

    Args:
        degrees (float): degrees.

    Returns:
        int: semicircles.
    """
    return int(degrees * (2 ** 31) / 180.0)

def ReadFitFile(fitFilename : str) -> dict[str, list[Any]]:
    """ Reads the FIT file.

    Args:
        fitFilename (str): FIT filename.

    Returns:
        dict[str, list[Any]]: The messages stored in the FIT file.
    """
    stream = garmin.Stream.from_file(fitFilename) # type: ignore

    decoder = garmin.Decoder(stream)
    if not decoder.is_fit():
        raise Exception("not a FIT file")
    if not decoder.check_integrity():
        raise Exception("FIT file is corrupt")

    stream.reset()
    messages, _ = decoder.read() # type: ignore

    return messages # type: ignore

class TrackPoint:
    Latitude : float
    Longitude : float
    Altitude  : float
    Time : datetime
    
def GetTrackPointsFromMessages(messages : dict[str, list[Any]]) -> list[TrackPoint]:
    """ Returns the list of track points.

    Args:
        messages (dict[str, list[Any]]): The FIT file messages.

    Returns:
        list[TrackPoint]: The track points.
    """
    pointList : list[TrackPoint] = []

    for msg in messages["record_mesgs"]:
        if "position_lat" not in msg or "position_long" not in msg:
            continue
        
        point = TrackPoint()

        point.Latitude = SemicircleToDegress(msg["position_lat"])
        point.Longitude = SemicircleToDegress(msg["position_long"])
        point.Altitude = msg["enhanced_altitude"]
        point.Time = msg["timestamp"]

        pointList.append(point)

    return pointList

def __CreateNodeTrkSeq(doc : xmd.Document, pointList : list[TrackPoint]) -> xmd.Element:
    """ Creates the GPX track sequence.

    Args:
        doc (xmd.Document): The XML document.
        pointList (list[TrackPoint]): List of track points.

    Returns:
        xmd.Element: The GPX track sequence node.
    """
    nodeTrkSeq = doc.createElement("trkseg")

    for point in pointList:

        nodeTrkPt = doc.createElement("trkpt")
        nodeTrkSeq.appendChild(nodeTrkPt)

        nodeTrkPt.setAttribute("lat", f"{point.Latitude:.10f}")
        nodeTrkPt.setAttribute("lon", f"{point.Longitude:.10f}")

        nodeTime = doc.createElement("time")
        nodeTrkPt.appendChild(nodeTime)
        nodeTime.appendChild(doc.createTextNode(point.Time.strftime("%Y-%m-%dT%H:%M:%SZ")))

        nodeEle = doc.createElement("ele")
        nodeTrkPt.appendChild(nodeEle)
        nodeEle.appendChild(doc.createTextNode(f"{point.Altitude:.3f}"))

    return nodeTrkSeq

def __CreateNodeTrk(doc : xmd.Document, name : str, trackType : str, pointList : list[TrackPoint]) -> xmd.Element:
    """ Creates the GPX track node.

    Args:
        doc (xmd.Document): The XML document.
        name (str): The name of the track.
        trackType (str): The type of the track activity, e.g. hiking.
        pointList (list[TrackPoint]): List of track points.

    Returns:
        xmd.Element: The GPX track node.
    """

    nodeTrk = doc.createElement("trk")

    nodeName = doc.createElement("name")
    nodeName.appendChild(doc.createTextNode(name))
    nodeTrk.appendChild(nodeName)

    nodeType = doc.createElement("type")
    nodeType.appendChild(doc.createTextNode(trackType))
    nodeTrk.appendChild(nodeType)

    nodeTrkSeq = __CreateNodeTrkSeq(doc, pointList)
    nodeTrk.appendChild(nodeTrkSeq)

    return nodeTrk

def WriteGpxFile(gpxFilename : str, name : str, trackType : str, pointList : list[TrackPoint]) -> None:
    """ Writes the GPX file

    Args:
        gpxFilename (str): _description_
        name (str): The name of the track.
        trackType (str): The type of the track activity, e.g. hiking.
        pointList (list[TrackPoint]): List of track points.
    """
    doc = xmd.getDOMImplementation().createDocument(None, "gpx", None)
    
    nodeGpx = doc.documentElement
    if nodeGpx is None:
        raise Exception("missing root node")
    
    nodeGpx.setAttribute("creator", "convert_fit_to_gpx")
    nodeGpx.setAttribute("xmlns", "http://www.topografix.com/GPX/1/1")
    nodeGpx.setAttribute("version", "1.1")
    nodeGpx.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    nodeGpx.setAttribute("xsi:schemaLocation", "http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/11.xsd")

    nodeTrk = __CreateNodeTrk(doc, name, trackType, pointList)
    nodeGpx.appendChild(nodeTrk)

    with open(gpxFilename, "w") as file:
        doc.writexml(file, encoding="UTF-8", addindent="  ", newl="\n")

def ConvertFitFileToGpxFile(fitFilename : str, gpxFilename : str, removePointsBegin : int = 0, removePointsEnd : int = 0) -> None:

    messages = ReadFitFile(fitFilename)

    trackType = messages["sport_mesgs"][0]["sport"]
    pointList = GetTrackPointsFromMessages(messages)

    if removePointsBegin > 0:
        pointList = pointList[removePointsBegin : ]

    if removePointsEnd > 0:
        pointList = pointList[ : -removePointsEnd]

    print(f"Number of points: {len(pointList)}")
    
    name = Path(fitFilename).stem
    WriteGpxFile(gpxFilename, name, trackType, pointList)

if __name__ == "__main__":

    argParser = argparse.ArgumentParser("convert_fit_to_gpx", description="Converts tracks from Garmin activity FIT files to GPX files.")
    argParser.add_argument("filename", help='input filename "abc.FIT"')
    argParser.add_argument("-rb", "--removebegin", help="remove number of points from the begin of the track", required=False)
    argParser.add_argument("-re", "--removeend", help="remove number of points from the end of the track", required=False)
    args = argParser.parse_args()

    inputFilename = args.filename
    outputFilename = str(Path(inputFilename).with_suffix(".gpx"))

    removePointsBegin = abs(int(args.removebegin)) if args.removebegin is not None else 0
    removePointsEnd = abs(int(args.removeend)) if args.removeend is not None else 0
        
    print(f"Convert activity FIT file {inputFilename} to GPX file {outputFilename} ...")
    if removePointsBegin > 0:
        print(f"removing {removePointsBegin} points from the begin of the track")
    if removePointsEnd > 0:
        print(f"removing {removePointsEnd} points from the end of the track")

    ConvertFitFileToGpxFile(inputFilename, outputFilename, removePointsBegin, removePointsEnd)

    print("done")


