#!/usr/bin/python
from trajectoryPlottingTools import *
from optimizationPlottingTools import *
import os


# rootDirectoryPath = str(sys.argv[1])
rootDirectoryPath = "/home/ryan/Desktop/tmp-test/"
# Extract the path to the latest test dir
with open(rootDirectoryPath+"latestLogPath.txt") as f:
    pathToTestDir = f.readline()

trajDir = pathToTestDir + "Trajectory/"
solverDir = pathToTestDir + "Solver/"



trajOnlyDir = [ d for d in os.listdir(trajDir) if os.path.isdir(trajDir + d)]
trajOnlyDir.sort()

for iterationIndex in range(len(trajOnlyDir)):

    print "Processing ", iterationIndex+1, " of ", len(trajOnlyDir)

    trajLatestDir = trajOnlyDir[iterationIndex]

    savePlot=True
    showPlot=False
    saveDir = pathToTestDir + "Plots/" + str(iterationIndex+1)
    if not os.path.exists(saveDir):
        os.makedirs(saveDir)

    TP = trajectoryPlotter( trajDir + trajLatestDir+"/trajectory.txt", trajDir + trajLatestDir+"/realTrajectory.txt",  trajDir + trajLatestDir+"/waypoints.txt")
    TP.plotTrajectory(savePlot, showPlot, saveDir)

    plotBayesianOptimization(solverDir, iterationIndex, savePlot, showPlot, saveDir)
