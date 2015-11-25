#!/usr/bin/python
from trajectoryPlottingTools import *
import yarp
import os


# Start yarp Network
yarp.Network.init()

# Create input port
inputPort = yarp.BufferedPortBottle()
inputPort.open("/python/trajVis:i");

# Wait for first message which should be the root dir for the tests
# rootDirBottle = inputPort.read(True)
# rootDirectoryPath = rootDirBottle.get(0).asString()
rootDirectoryPath = "/home/ryan/Desktop/tmp-test/"
# Extract the path to the latest test dir
with open(rootDirectoryPath+"latestLogPath.txt") as f:
    pathToTestDir = f.readline()

trajDir = pathToTestDir + "Trajectory/"


trajOnlyDir = [ d for d in os.listdir(trajDir) if os.path.isdir(trajDir + d)]
trajOnlyDir.sort()

iterationIndex = 2
trajLatestDir = trajOnlyDir[iterationIndex]

savePlot=True
showPlot=False
saveDir = pathToTestDir + "Plots/" + str(iterationIndex)

TP = trajectoryPlotter( trajDir + trajLatestDir+"/trajectory.txt", trajDir + trajLatestDir+"/realTrajectory.txt",  trajDir + trajLatestDir+"/waypoints.txt")
TP.plotTrajectory(savePlot, showPlot, saveDir)



inputPort.close();
yarp.Network.fini();
