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

import json
from convert_fit_to_gpx import CreateGpxTrackFromFitActivity
from playwright.sync_api import sync_playwright

####################################################################################
### This module creates a map image with a track from a garmin activity file
### using the Google Maps DYNAMIC API.
###
### The dynamic API supports all map types.
####################################################################################

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
        # e.g.: { lat: 50.9240, lng: 13.9760 }
        point_list.append(f"{{ lat: {p.point.latitude:.6f}, lng: {p.point.longitude:.6f} }}")

    return ",".join(point_list), center_latitude, center_longitude # type: ignore

def __CreateAndSaveMapImage(img_filename : str,
             img_width : int, img_height : int, map_type : str,
             path_points : str, path_color : str = "#C0000000", path_width : int = 3) -> None:
    """ Creates the map with the track and stores it in an image file.

    Args:
        img_filename (str): The name of the image file. (PNG)
        img_width (int): The image width in pixels.
        img_height (int): The image height in pixels.
        map_type (str): The map type: roadmap, terrain, satellite, hybrid.
        path_points (str): The track points.
        path_color (str, optional): The track color in RGBA. Defaults to "0xFF000080".
        path_width (int, optional): The track width. Defaults to 3.

    """

    # pixel around the track points to be included in the image
    pixel_bounds = 10

    googleApiKey = __ReadGoogleApiKey()

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>html, body, #map {{ height: 100%; margin: 0; padding: 0; }}</style>
</head>
<body>
    <div id="map"></div>
    <script>
        function initMap() {{
            const trackPoints = [
                {path_points}
            ];

            const bounds = new google.maps.LatLngBounds();
            trackPoints.forEach(p => bounds.extend(p));

            const map = new google.maps.Map(document.getElementById("map"), {{
                center: bounds.getCenter(),
                zoom: 14,
                mapTypeId: "{map_type}",
                disableDefaultUI: true
            }});

            map.fitBounds(bounds, {pixel_bounds});

            new google.maps.Polyline({{
                path: trackPoints,
                geodesic: true,
                strokeColor: "{path_color}",
                strokeOpacity: 1.0,
                strokeWeight: {path_width},
                map: map
            }});

            google.maps.event.addListenerOnce(map, "tilesloaded", function() {{
                setTimeout(function() {{ window.mapReady = true; }}, 3000);
            }});
        }}
    </script>
    <script src="https://maps.googleapis.com/maps/api/js?key={googleApiKey}&callback=initMap" async defer></script>
</body>
</html>
"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": img_width, "height": img_height})
        
        page.set_content(html_content, wait_until="load")
        
        page.wait_for_function("window.mapReady === true", timeout=30000)
    
        page.screenshot(path=img_filename)
        browser.close()    

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

    track, _, _ = __MakeGpxTrackAndCenterIt(fit_filename)

    __CreateAndSaveMapImage(output_filename,
                            img_width, img_height,
                            map_type,
                            track,
                            path_color, path_width)

# for testing only
if __name__ == "__main__":

    file_name = "test.fit"
    color = "#E00000"

    CreateImageWithTrackOnMap(file_name, "map1.jpg", 800, 600, "hybrid", color, 3)
    CreateImageWithTrackOnMap(file_name, "map2.png", 800, 600, "roadmap", color, 3)
    CreateImageWithTrackOnMap(file_name, "map3.png", 800, 600, "terrain", color, 3)
    CreateImageWithTrackOnMap(file_name, "map4.jpg", 800, 600, "satellite", color, 3)



