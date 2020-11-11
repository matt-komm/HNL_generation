import os
import argparse
import re
import sys
import h5py
import numpy

parser = argparse.ArgumentParser()
parser.add_argument('--lhe', dest='lhe', type=str, required=True, help='lhe')
parser.add_argument('-o','--output', dest='output', type=str, required=True, help='output')
args = parser.parse_args()

f = open(args.lhe)
weightTagRegex = re.compile("<wgt\s+id\s*=\s*'([a-zA-Z0-9_]+)'\s*>\s*(\S+)\s*</wgt>")
weightList = {}

for l in f:
    if l.find("<event>")>=0:  
        eventWeights = {}
    if l.find("</event>")>=0:
        if len(weightList.keys())==0:
            for k,v in eventWeights.iteritems():
                weightList[k] = [v]
        else:
            if len(weightList.keys())!=len(eventWeights.keys()):
                print "ERROR: number of weights do not match with previous events"
                sys.exit(1)
            for k,v in eventWeights.iteritems():
                weightList[k].append(v)
            
            
    match = weightTagRegex.match(l)
    if match:
        if eventWeights.has_key(match.group(1)):
            print "ERROR: weight id '%s' appears twice in event"
            sys.exit(1)
        eventWeights[match.group(1)]=float(match.group(2))

output = h5py.File(args.output,'w')
for k,v in weightList.iteritems():
    output.create_dataset(k,data=numpy.array(weightList[k],dtype=numpy.float32))
output.close()
    

