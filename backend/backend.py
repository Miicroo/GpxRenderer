from fit2gpx import StravaConverter
from os import listdir
from os.path import isfile, join, abspath

import string
import sys
import xml.etree.ElementTree

DEFAULT_GPX_PATH = './data'
ARG_FROM_STRAVA = '--from-strava'
STRAVA_PATH = 'activities_gpx'


def get_gpx_path():
    return f'{get_data_path()}/{STRAVA_PATH}' if should_parse_from_strava() else get_data_path()


def get_data_path():
    if len(sys.argv) == 1 or sys.argv[1] == ARG_FROM_STRAVA:
        return DEFAULT_GPX_PATH
    else:
        return sys.argv[1]


def should_parse_from_strava():
    return ARG_FROM_STRAVA in sys.argv


def parse_strava():
    strava_conv = StravaConverter(
        dir_in=get_data_path()
    )
    strava_conv.unzip_activities()
    strava_conv.add_metadata_to_gpx()
    strava_conv.strava_fit_to_gpx()


def get_gpx_files():
    path = get_gpx_path()
    return [abspath(join(path, f)) for f in listdir(path) if isfile(join(path, f)) and f.endswith('.gpx')]


def parse_gpx(filename):
    print(f'Parsing {filename}')

    template = string.Template('{http://www.topografix.com/GPX/1/1}$tag')
    track_point_tag = template.substitute(tag='trkpt')
    time_tag = template.substitute(tag='time')
    root = xml.etree.ElementTree.parse(filename)

    latlon = []
    for track_point in root.findall('.//' + track_point_tag):
        latlon.append({'lat': track_point.get('lat'), 'lng': track_point.get('lon')})

    filename_from_time = filename.split('/')[-1].replace('.', '')
    for time in root.findall('.//' + time_tag):
        filename_from_time = time.text.replace('-', '').replace(':', '')
        break

    return filename_from_time, latlon


def gpx_data_to_js_func(gpx_data):
    filename, coordinates = gpx_data
    func_name = f'func{filename}'

    js_fnc = 'var ' + func_name + ' = function() {\n'
    js_fnc += '\tvar coordinates = [\n'

    for i, coordinate in enumerate(coordinates):
        js_fnc += '\t\t{lat: ' + coordinate['lat'] + ', lng: ' + coordinate['lng'] + '}'
        if i != len(coordinates) - 1:
            js_fnc += ','
        js_fnc += '\n'

    js_fnc += '\t];\n'
    js_fnc += '\treturn coordinates;\n'
    js_fnc += '};\n'

    return func_name, js_fnc


def get_all_js_func(funcnames):
    gps_func = 'var getAllGpsFuncs = function() {\n'
    gps_func += '\tvar funcs = [\n'

    for i, func_name in enumerate(funcnames):
        gps_func += '\t\t' + func_name
        if i != len(funcnames) - 1:
            gps_func += ','
        gps_func += '\n'

    gps_func += '\t];\n'
    gps_func += '\treturn funcs;\n'
    gps_func += '};\n'

    return gps_func


def write_js_file(filename, data):
    with open(filename, 'w') as handle:
        handle.write(data)


def main():
    if should_parse_from_strava():
        parse_strava()

    all_js_funcs = []
    js_data = ''
    gpx_files = get_gpx_files()
    for i, filename in enumerate(gpx_files):
        gpxdata = parse_gpx(filename)

        (func_name, jsFunc) = gpx_data_to_js_func(gpxdata)
        all_js_funcs.append(func_name)
        js_data += jsFunc

        print(str(i + 1) + ' of ' + str(len(gpx_files)) + ' done')

    js_container_func = get_all_js_func(all_js_funcs)

    write_js_file('./web/backend.js', js_container_func + '\n\n' + js_data)


main()
