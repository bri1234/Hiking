# Hiking tools

## Requirements

### Install needed python package
Pytohn packages:
- garmin-fit-sdk
- staticmap
- gpxpy
- matplotlib
- json

```bash
python3 -m pip install garmin-fit-sdk staticmap gpxpy matplotlib json
```

## convert_fit_to_gpx

This tool converts tracks from GARMIN activity FIT files to GPX files.

### Usage
```bash
python3 convert_fit_to_gpx.py input_file.fit
```
Converts the track from the file "input_file.fit" to the file "input_file.gpx".

### Show options
```bash
python3 convert_fit_to_gpx.py -h
```

## gpx_statistic

This tool prints a statistic summary of a GPX track.

### Usage
```bash
python3 gpx_statistic.py input_file.gpx
```
Converts the track from the file "input_file.fit" to the file "input_file.gpx".

### Show options
```bash
python3 gpx_statistic.py -h
```

## prepare_track_for_publish

Creates an elevation profile, maps and statistic of a GARMIN activity FIT file.

### Usage
```bash
python3 prepare_track_for_publish.py input_file.fit
```
Creates an elevation profile, maps and statistic of FIT file "input_file.fit".

### Show options
```bash
python3 prepare_track_for_publish.py -h
```

