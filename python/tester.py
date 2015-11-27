#!/usr/bin/python
from trajectoryPlottingTools import *
import os


rootDirectoryPath = "/home/ryan/Desktop/tmp-test/"
with open(rootDirectoryPath+"latestLogPath.txt") as f:
    pathToTestDir = f.readline()

trajDir = pathToTestDir + "Trajectory/8/"

CP = costPlotter(trajDir)

CP.plotCosts(savePlot=False)
