#!/usr/bin/python
import os
import glob
import sys
import math
import numpy as np

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D

from matplotlib import cm

rootPath = str(sys.argv[1])

path_file = rootPath + '/latestLogPath.txt'

with open (path_file, "r") as myfile:
    optLogDir=myfile.readline()
# Find current optLog dir.
print 'Looking for data directories in:\n', optLogDir


onlyDir = [ d for d in os.listdir(optLogDir) if os.path.isdir(optLogDir + d)]
onlyDir.sort()

iterDir = onlyDir[-1]

searchSpace_path        = optLogDir + iterDir + '/searchSpace.txt'
searchSpaceBounds_path  = optLogDir + iterDir + '/searchSpaceBounds.txt'
gpParams_path           = optLogDir + iterDir + '/gpParams.txt'
gpWeights_path          = optLogDir + iterDir + '/gpWeights.txt'
gpCosts_path            = optLogDir + iterDir + '/gpCosts.txt'
gpMean_path             = optLogDir + iterDir + '/currentCostMeans.txt'
gpVariance_path         = optLogDir + iterDir + '/currentCostVariances.txt'
LCB_path                = optLogDir + iterDir + '/LCB.txt'
minIndex_path           = optLogDir + iterDir + '/minIndex.txt'
optimumFound_path       = optLogDir + iterDir + '/optimumFound.txt'
currentMinCost_path     = optLogDir + iterDir + '/currentMinCost.txt'
currentConfidence_path  = optLogDir + iterDir + '/currentConfidence.txt'
optimalParameters_path  = optLogDir + iterDir + '/optimalParameters.txt'
tau_path                = optLogDir + iterDir + '/tau.txt'

searchSpace         = np.loadtxt(searchSpace_path)
searchSpaceBounds   = np.loadtxt(searchSpaceBounds_path)
gpParams            = np.loadtxt(gpParams_path)
gpWeights           = np.loadtxt(gpWeights_path)
gpCosts             = np.loadtxt(gpCosts_path)
gpMean              = np.loadtxt(gpMean_path)
gpVariance          = np.loadtxt(gpVariance_path)
LCB                 = np.loadtxt(LCB_path)
minIndex            = np.loadtxt(minIndex_path)
optimumFound        = np.loadtxt(optimumFound_path)
currentMinCost      = np.loadtxt(currentMinCost_path)
currentConfidence   = np.loadtxt(currentConfidence_path)
optimalParameters   = np.loadtxt(optimalParameters_path)


tauFunction = []
for iterDir in onlyDir:
    tau_path = optLogDir + iterDir + '/tau.txt'
    tauFunction.append(np.loadtxt(tau_path))

tau = []
for tmp in tauFunction:
    tau.append(tmp[()]) #weird 0D np array bug: http://stackoverflow.com/questions/773030/why-are-0d-arrays-in-numpy-not-considered-scalar
tau = np.array(tau)




if len(np.shape(gpParams)) == 1:
    kernelDim = 1
    numberOfKernels = np.size(gpParams)

else:
    kernelDim, numberOfKernels = np.shape(gpParams)





nDims, nSamples = np.shape(searchSpace)

nRows = int(math.sqrt(nSamples))
nCols = int(nSamples/nRows)
while (nSamples % nRows) != 0 :
    nRows += 1
    nCols = int(nSamples/nRows)


print 'Reshaped matrices have nRows: ', nRows, '\tnCols: ', nCols

X1mat = np.reshape(searchSpace[0,:], (nRows, nCols))
X2mat = np.reshape(searchSpace[1,:], (nRows, nCols))
Means = np.reshape(gpMean, (nRows, nCols))
Vars = np.reshape(gpVariance, (nRows, nCols))
LCBs = np.reshape(LCB, (nRows, nCols))






# if nRows<50:
#     strideStep = 1
# elif nRows>=50 and nRows<100:
#     strideStep = 5
# else:
#     strideStep = 10

strideStep = 1


# print 'kernelDim: ', kernelDim
# print 'numberOfKernels: ', numberOfKernels
# print 'nDims: ', nDims
# print 'nSamples: ', nSamples



fs_labels = 16
fs_title = 20

var_alpha = 0.3
var_color = 'r'

fig = plt.figure(num='Bayesian Optimization', figsize=(24, 12), dpi=80, facecolor='w', edgecolor='k')
############################################################################################

ax_cost_3d = fig.add_subplot(2, 3, 1, projection='3d')
surfGP = ax_cost_3d.plot_surface(X1mat, X2mat, Means, rstride=strideStep, cstride=strideStep, cmap=cm.jet)
ax_cost_3d.set_ylabel('X (m)', fontsize=fs_labels)
ax_cost_3d.set_xlabel('time (s)', fontsize=fs_labels)
ax_cost_3d.set_zlabel('Cost Mean', fontsize=fs_labels)



ax_cost_2d_means = fig.add_subplot(2, 3, 2)
ax_cost_2d_means.contourf(X1mat, X2mat, Means, rstride=strideStep, cstride=strideStep, cmap=cm.jet)
ax_cost_2d_means.plot(gpParams[0,:], gpParams[1,:], 'go', ms = 10)
ax_cost_2d_means.plot(optimalParameters[0], optimalParameters[1], color='orange', marker='s', ms = 15)


ax_cost_2d_means.set_ylabel('X (m)', fontsize=fs_labels)
ax_cost_2d_means.set_xlabel('time (s)', fontsize=fs_labels)
ax_cost_2d_means.set_title('Cost Mean', fontsize=fs_labels)


ax_cost_2d_vars = fig.add_subplot(2, 3, 3)
ax_cost_2d_vars.contourf(X1mat, X2mat, Vars, rstride=strideStep, cstride=strideStep, cmap=cm.jet)
ax_cost_2d_vars.plot(gpParams[0,:], gpParams[1,:], 'go', ms = 10)
ax_cost_2d_vars.plot(optimalParameters[0], optimalParameters[1], color='orange', marker='s', ms = 15)

ax_cost_2d_vars.set_ylabel('X (m)', fontsize=fs_labels)
ax_cost_2d_vars.set_xlabel('time (s)', fontsize=fs_labels)
ax_cost_2d_vars.set_title('Cost Variance', fontsize=fs_labels)


############################################################################################

ax_lcb_3d = fig.add_subplot(2, 3, 4, projection='3d')
ax_lcb_3d.plot_surface(X1mat, X2mat, LCBs, rstride=strideStep, cstride=strideStep, cmap=cm.jet)
ax_lcb_3d.set_ylabel('X (m)', fontsize=fs_labels)
ax_lcb_3d.set_xlabel('time (s)', fontsize=fs_labels)
ax_lcb_3d.set_zlabel('LCB', fontsize=fs_labels)



ax_lcb_2d = fig.add_subplot(2, 3, 5)
ax_lcb_2d.contourf(X1mat, X2mat, LCBs, rstride=strideStep, cstride=strideStep, cmap=cm.jet)
ax_lcb_2d.plot(optimalParameters[0], optimalParameters[1], color='orange', marker='s', ms = 15)

ax_lcb_2d.set_ylabel('X (m)', fontsize=fs_labels)
ax_lcb_2d.set_xlabel('time (s)', fontsize=fs_labels)
ax_lcb_2d.set_title('LCB', fontsize=fs_labels)


ax_tau = fig.add_subplot(2, 3, 6)
ax_tau.plot(tau)
ax_tau.set_xlabel('iteration', fontsize=fs_labels)
ax_tau.set_ylabel('tau value', fontsize=fs_labels)
ax_tau.set_title('tau function', fontsize=fs_labels)

cbaxes = fig.add_axes([0.02, 0.2, 0.03, 0.6])
fig.colorbar(surfGP, cax=cbaxes)


plt.show() #block=True
