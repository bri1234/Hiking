# Hiking tools

## convert_fit_to_gpx

This tool converts tracks from GARMIN activity FIT files to GPX files.

**Usage:**
```bash
python3 convert_fit_to_gpx.py input_file.fit
```
Converts the track from the file "input_file.fit" to the file "input_file.gpx".

Install needed python package:
```bash
python3 -m pip install garmin-fit-sdk
```

Show options:
```bash
python3 convert_fit_to_gpx.py -h
```
