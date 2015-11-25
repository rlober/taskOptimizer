#!/usr/bin/python
from optimizationPlottingTools import *
import yarp
import os


# Start yarp Network
yarp.Network.init()

# Create input port
inputPort = yarp.BufferedPortBottle()
inputPort.open("/python/costVis:i");

# Wait for first message which should be the root dir for the tests
# rootDirBottle = inputPort.read(True)
# rootDirectoryPath = rootDirBottle.get(0).asString()
rootDirectoryPath = "/home/ryan/Desktop/tmp-test/"
# Extract the path to the latest test dir
with open(rootDirectoryPath+"latestLogPath.txt") as f:
    pathToTestDir = f.readline()

solverDir = pathToTestDir + "Solver/"

plotBayesianOptimization(solverDir)
#
# solverOnlyDir = [ d for d in os.listdir(solverDir) if os.path.isdir(solverDir + d)]
# solverOnlyDir.sort()
#
# solverLatestDir = solverOnlyDir[-2]





inputPort.close();
yarp.Network.fini();
