
import math
import numpy as np

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D

try:
    import cPickle as pickle
except:
    import pickle


class Plotter():

    def __init__(self, pathToTrajFile, pathToWaypointFile):
        self.readFromText(pathToTrajFile, pathToWaypointFile)

    def readFromText(self, pathToTextFile, pathToWaypointFile):
        trajData = np.loadtxt(pathToTextFile)
        self.waypointData = np.loadtxt(pathToWaypointFile)
        nRows, nCols = np.shape(trajData)
        self.n_DoF = int((nCols-1)/4)

        tmp = trajData[:,self.n_DoF*3+1:]
        self.variance = tmp[:,0:3]
        self.weights = tmp[:,3:]
        self.generateFromNumpyArray(trajData[:,0:self.n_DoF*3+1])

    def generateFromNumpyArray(self, trajData):
        nRows, nCols = np.shape(trajData)

        self.timeline = np.array([trajData[:,0]]).T
        self.time_start = self.timeline[0,0] # Starting time
        self.time_end = self.timeline[-1,0]
        self.duration = abs(self.time_end - self.time_start)
        self.pos = trajData[:,1:1+self.n_DoF]
        self.vel = trajData[:,1+self.n_DoF:1 + 2*self.n_DoF]
        self.acc = trajData[:,1+2*self.n_DoF:1 + 3*self.n_DoF]

        self.waypointTimes = self.waypointData[:,0]
        self.waypoints = self.waypointData[:,1:]

        print self.n_DoF

        self.trajectory = np.array(np.hstack((self.timeline, self.pos, self.vel, self.acc)))
        self.initial_state = trajData[0,1:]
        self.goal_state = trajData[-1,1:]


    def plotTrajectory(self):
        fs = 10 # fontsize for axes
        dof_labels = ['x','y','z']
        var_color = 'r'
        var_alpha = 0.3
        if self.n_DoF == 3:
            fig = plt.figure(num=1, figsize=(8, 8), dpi=80, facecolor='w', edgecolor='k')
            ax_3d = fig.gca(projection='3d')
            ax_3d.plot(self.pos[:,0],self.pos[:,1],self.pos[:,2])
            ax_3d.plot(self.waypoints[1:-1,0],self.waypoints[1:-1,1],self.waypoints[1:-1,2], 'bo', ms=10)
            ax_3d.plot(self.waypoints[0:1,0],self.waypoints[0:1,1],self.waypoints[0:1,2], 'go', ms=10)
            ax_3d.plot(self.waypoints[-1:,0],self.waypoints[-1:,1],self.waypoints[-1:,2], 'ro', ms=10)
            ax_3d.set_title('3D Trajectory Plot')
            ax_3d.set_xlabel('X')
            ax_3d.set_ylabel('Y')
            ax_3d.set_zlabel('Z')

        elif self.n_DoF==2:
            fig = plt.figure(figsize=(8, 8), dpi=80, facecolor='w', edgecolor='k')
            plt.plot(self.pos[:,0],self.pos[:,1], color='r', label='Original')
            plt.plot(self.waypoints[1:-1,0], self.waypoints[1:-1,1], 'bo', ms=10)
            plt.plot(self.waypoints[0,0],self.waypoints[0,1], 'go', ms=10)
            plt.plot(self.waypoints[-1,0],self.waypoints[-1,1], 'ro', ms=10)

            plt.title('2D Trajectory Plot')
            plt.ylabel('Y')
            plt.xlabel('X')



        dof_fig = plt.figure(num=2, figsize=(16, 9), dpi=80, facecolor='w', edgecolor='k')
        maxtime = self.timeline[-1] +0.5
        # self.n_DoF = 3
        for dd in range(self.n_DoF):
            ax_pos = plt.subplot2grid((4,self.n_DoF), (0,dd))
            mean_plot, = ax_pos.plot(self.timeline, self.pos[:,dd])
            waypoints_plot, = ax_pos.plot(self.waypointTimes[1:-1],self.waypoints[1:-1,dd], 'bo', ms=8, alpha=0.8)
            ax_pos.plot(self.waypointTimes[0],self.waypoints[0,dd], 'go', ms=8, alpha=0.8)
            ax_pos.plot(self.waypointTimes[-1],self.waypoints[-1,dd], 'ro', ms=8, alpha=0.8)

            dof_var = self.variance[:,dd]
            upperVar = self.pos[:,dd] - dof_var
            lowerVar = self.pos[:,dd] + dof_var
            ax_pos.fill_between(self.timeline[:,0], upperVar, lowerVar, alpha=var_alpha, facecolor=var_color, edgecolor=None)
            var_plot = plt.Rectangle((0, 0), 1, 1, alpha=var_alpha, facecolor=var_color, edgecolor=None)


            ax_pos.axhline(y = self.waypoints[0,dd], c='g', ls='--', lw=2) #starting point
            ax_pos.axhline(y = self.waypoints[-1:,dd], c='red', ls='--', lw=2) #end point
            ax_pos.set_title('DoF_'+dof_labels[dd], fontsize=fs)
            ax_pos.set_xlabel('time (s)', fontsize=fs)
            ax_pos.set_ylabel('position', fontsize=fs)
            ax_pos.set_xlim(left=-0.5, right=maxtime)


            # ax_pos.set_ylim([-2, 4])



            ax_vel = plt.subplot2grid((4,self.n_DoF), (1,dd))
            ax_vel.plot(self.timeline, self.vel[:,dd])
            ax_vel.axhline(y = 0, c='red', ls='--', lw=2)
            ax_vel.set_title('DoF_'+dof_labels[dd], fontsize=fs)
            ax_vel.set_xlabel('time (s)', fontsize=fs)
            ax_vel.set_ylabel('velocity', fontsize=fs)
            ax_vel.set_xlim(left=-0.5, right=maxtime)

            ax_acc = plt.subplot2grid((4,self.n_DoF), (2,dd))
            ax_acc.plot(self.timeline, self.acc[:,dd])
            ax_acc.axhline(y = 0, c='red', ls='--', lw=2)
            ax_acc.set_title('DoF_'+dof_labels[dd], fontsize=fs)
            ax_acc.set_xlabel('time (s)', fontsize=fs)
            ax_acc.set_ylabel('acceleration', fontsize=fs)
            ax_acc.set_xlim(left=-0.5, right=maxtime)

            ax_weights = plt.subplot2grid((4,self.n_DoF), (3,dd))
            ax_weights.plot(self.timeline, self.weights[:,dd])
            # ax_weights.axhline(y = 0, c='red', ls='--', lw=2)
            ax_weights.set_title('DoF_'+dof_labels[dd], fontsize=fs)
            ax_weights.set_xlabel('time (s)', fontsize=fs)
            ax_weights.set_ylabel('weight', fontsize=fs)
            ax_weights.set_ylim([0,1])
            ax_weights.set_xlim(left=-0.5, right=maxtime)

        dof_fig.legend([mean_plot, var_plot, waypoints_plot], ['Path Mean', 'Path Variance', 'Waypoints'], loc='upper left')
        plt.subplots_adjust(wspace=0.5, hspace=0.5)
        plt.show(block=True)






trajPlotter = Plotter("./trajectory.txt", "./waypoints.txt")
trajPlotter.plotTrajectory()
