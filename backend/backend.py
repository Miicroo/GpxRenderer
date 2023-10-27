from os import listdir
from os.path import isfile, join, abspath

import string
import sys
import xml.etree.ElementTree

DEFAULT_GPX_PATH = "../data"

def getGpxPath():
    if len(sys.argv) == 1:
        return DEFAULT_GPX_PATH
    else:
        return sys.argv[1]
    
def getGpxFiles():
    path = getGpxPath()
    return [abspath(join(path, f)) for f in listdir(path) if isfile(join(path, f)) and f.endswith(".gpx")]

def parseGpx(filename):
    print("Parsing " + filename)
    
    template = string.Template("{http://www.topografix.com/GPX/1/1}$tag")
    trkptTag = template.substitute(tag="trkpt")
    timeTag = template.substitute(tag="time")
    root = xml.etree.ElementTree.parse(filename)

    latlon = []
    for trkpt in root.findall(".//"+trkptTag):
        latlon.append({"lat": trkpt.get("lat"), "lng": trkpt.get("lon")});
        
    for time in root.findall(".//"+timeTag):
        filenameFromTime = time.text.replace("-", "").replace(":", "")
        break
    
    return (filenameFromTime, latlon)

def gpxDataToJsFunc(gpxData):
    filename, coordinates = gpxData
    funcName = "func"+filename
    
    jsFnc = "var "+funcName+" = function() {\n";
    jsFnc += "\tvar coordinates = [\n";
    
    for i, coordinate in enumerate(coordinates):
        jsFnc += "\t\t{lat: " +coordinate["lat"] + ", lng: " + coordinate["lng"] + "}"
        if i != len(coordinates)-1:
            jsFnc += ","
        jsFnc += "\n";
        
    jsFnc += "\t];\n";
    jsFnc += "\treturn coordinates;\n";
    jsFnc += "};\n"

    return (funcName, jsFnc)

def getAllJsFunc(funcnames):
    gpsFunc = "var getAllGpsFuncs = function() {\n";
    gpsFunc += "\tvar funcs = [\n";

    for i, funcname in enumerate(funcnames):
        gpsFunc += "\t\t"+funcname
        if i != len(funcnames)-1:
            gpsFunc += ","
        gpsFunc += "\n";

    gpsFunc += "\t];\n";
    gpsFunc += "\treturn funcs;\n";
    gpsFunc += "};\n"

    return gpsFunc

def writeJsFile(filename, data):
    with open(filename, "w") as handle:
        handle.write(data)

def main():
    allJsFuncs = []
    jsData = ""
    gpxFiles = getGpxFiles();
    for i, filename in enumerate(gpxFiles):
        gpxdata = parseGpx(filename)
        
        (funcname, jsFunc) = gpxDataToJsFunc(gpxdata)
        allJsFuncs.append(funcname)
        jsData += jsFunc

        print(str(i+1) + " of " + str(len(gpxFiles)) + " done")

    jsContainerFunc = getAllJsFunc(allJsFuncs)

    writeJsFile("../web/backend.js", jsContainerFunc + "\n\n" + jsData)

main()
