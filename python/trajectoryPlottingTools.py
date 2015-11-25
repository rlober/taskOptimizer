#!/usr/bin/python
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

import matplotlib.patches as patches


class trajectoryPlotter():

    def __init__(self, pathToTrajFile, pathToRealTrajFile, pathToWaypointFile):
        self.readFromText(pathToTrajFile, pathToRealTrajFile, pathToWaypointFile)

    def readFromText(self, pathToTrajFile, pathToRealTrajFile, pathToWaypointFile):
        trajData = np.loadtxt(pathToTrajFile)
        realTrajData = np.loadtxt(pathToRealTrajFile)

        self.n_DoF = int((np.shape(trajData)[1]-1)/4)

        self.waypointData = np.loadtxt(pathToWaypointFile)
        self.waypointTimes = self.waypointData[:,0]
        self.waypoints = self.waypointData[:,1:]


        self.startWaypoint = self.waypoints[np.argmin(self.waypointTimes), :]
        self.startWaypointTime = self.waypointTimes[np.argmin(self.waypointTimes)]
        self.endWaypoint = self.waypoints[np.argmax(self.waypointTimes), :]
        self.endWaypointTime = self.waypointTimes[np.argmax(self.waypointTimes)]

        self.variance = trajData[:,self.n_DoF*3+1:]
        self.weights = realTrajData[:,self.n_DoF*3+1:]
        self.generateFromNumpyArray(trajData[:,0:self.n_DoF*3+1], realTrajData[:,0:self.n_DoF*3+1])

    def generateFromNumpyArray(self, trajData, realTrajData):

        self.timeline = np.array([trajData[:,0]]).T
        self.time_start = self.timeline[0,0] # Starting time
        self.time_end = self.timeline[-1,0]
        self.duration = abs(self.time_end - self.time_start)
        self.pos = trajData[:,1:1+self.n_DoF]
        self.vel = trajData[:,1+self.n_DoF:1 + 2*self.n_DoF]
        self.acc = trajData[:,1+2*self.n_DoF:1 + 3*self.n_DoF]


        self.trajectory = np.array(np.hstack((self.timeline, self.pos, self.vel, self.acc)))
        self.initial_state = trajData[0,1:]
        self.goal_state = trajData[-1,1:]


        self.real_timeline = np.array([realTrajData[:,0]]).T
        self.real_time_start = self.real_timeline[0,0] # Starting time
        self.real_time_end = self.real_timeline[-1,0]
        self.real_duration = abs(self.real_time_end - self.real_time_start)
        self.real_pos = realTrajData[:,1:1+self.n_DoF]
        self.real_vel = realTrajData[:,1+self.n_DoF:1 + 2*self.n_DoF]
        self.real_acc = realTrajData[:,1+2*self.n_DoF:1 + 3*self.n_DoF]


        self.real_trajectory = np.array(np.hstack((self.real_timeline, self.real_pos, self.real_vel, self.real_acc)))
        self.real_initial_state = realTrajData[0,1:]
        self.real_goal_state = realTrajData[-1,1:]


    def plotTrajectory(self, savePlot=True, showPlot=True, saveDir="./", extension=".png"):
        fs = 10 # fontsize for axes
        dof_labels = ['x','y','z']
        var_color = 'r'
        var_alpha = 0.3
        if self.n_DoF == 3:
            fig = plt.figure(num=1, figsize=(8, 8), dpi=80, facecolor='w', edgecolor='k')
            ax_3d = fig.gca(projection='3d')
            ax_3d.plot(self.pos[:,0],self.pos[:,1],self.pos[:,2], lw=3, ls='-')
            ax_3d.plot(self.real_pos[:,0],self.real_pos[:,1],self.real_pos[:,2], color='#2A7E43', lw=3)
            ax_3d.plot(self.waypoints[:,0],self.waypoints[:,1],self.waypoints[:,2], 'bo', ms=10)
            ax_3d.plot(self.startWaypoint[0:1],self.startWaypoint[1:2],self.startWaypoint[2:], 'go', ms=10)
            ax_3d.plot(self.endWaypoint[0:1],self.endWaypoint[1:2],self.endWaypoint[2:], 'ro', ms=10)
            ax_3d.set_title('3D Trajectory Plot')
            limRange = abs(self.endWaypoint[2:] - self.startWaypoint[2:])/2
            xlims = [self.startWaypoint[0]+limRange, self.startWaypoint[0]-limRange]
            ylims = [self.startWaypoint[1]-limRange, self.startWaypoint[1]+limRange]
            zlims = [-0.05, 0.30]
            LimList = [xlims, ylims, zlims]
            ax_3d.set_xlim(xlims)
            ax_3d.set_ylim(ylims)
            ax_3d.set_zlim(zlims)
            ax_3d.set_xlabel('X')
            ax_3d.set_ylabel('Y')
            ax_3d.set_zlabel('Z')

        elif self.n_DoF==2:
            fig = plt.figure(figsize=(8, 8), dpi=80, facecolor='w', edgecolor='k')
            plt.plot(self.pos[:,0],self.pos[:,1], color='r', label='Desired')
            plt.plot(self.real_pos[:,0],self.real_pos[:,1], color='#2A7E43', label='Real')
            plt.plot(self.waypoints[:,0],self.waypoints[:,1], 'bo', ms=10)
            plt.plot(self.startWaypoint[0:1],self.startWaypoint[1:2], 'go', ms=10)
            plt.plot(self.endWaypoint[0:1],self.endWaypoint[1:2], 'ro', ms=10)

            plt.title('2D Trajectory Plot')
            plt.ylabel('Y')
            plt.xlabel('X')



        dof_fig = plt.figure(num=2, figsize=(16, 9), dpi=80, facecolor='w', edgecolor='k')
        maxtime = self.timeline[-1] if self.timeline[-1]>self.real_timeline[-1] else self.real_timeline[-1]
        maxtime *= 1.1
        # self.n_DoF = 3
        for dd in range(self.n_DoF):
            ax_pos = plt.subplot2grid((4,self.n_DoF), (0,dd))
            mean_plot, = ax_pos.plot(self.timeline, self.pos[:,dd])
            real_mean_plot, = ax_pos.plot(self.real_timeline, self.real_pos[:,dd], color='#2A7E43', lw=2, ls='--')
            waypoints_plot, = ax_pos.plot(self.waypointTimes[:],self.waypoints[:,dd], 'bo', ms=8, alpha=0.8)
            ax_pos.plot(self.startWaypointTime,self.startWaypoint[dd], 'go', ms=8, alpha=0.8)
            ax_pos.plot(self.endWaypointTime,self.endWaypoint[dd], 'ro', ms=8, alpha=0.8)

            dof_var = self.variance[:,dd]
            upperVar = self.pos[:,dd] - dof_var
            lowerVar = self.pos[:,dd] + dof_var
            ax_pos.fill_between(self.timeline[:,0], upperVar, lowerVar, alpha=var_alpha, facecolor=var_color, edgecolor=None)
            var_plot = plt.Rectangle((0, 0), 1, 1, alpha=var_alpha, facecolor=var_color, edgecolor=None)


            ax_pos.axhline(y = self.startWaypoint[dd], c='g', ls='--', lw=2) #starting point
            ax_pos.axhline(y = self.endWaypoint[dd], c='red', ls='--', lw=2) #end point

            if dd==2:
                ax_pos.fill_between(np.arange(-0.5,maxtime,0.01), self.endWaypoint[dd]+0.03, self.endWaypoint[dd]-0.03, alpha=0.1, facecolor=var_color, edgecolor=None)

            ax_pos.add_patch(patches.Rectangle((1.5, 0.12), maxtime, .01, alpha=var_alpha, facecolor='y', edgecolor=None))



            ax_pos.set_title('DoF_'+dof_labels[dd], fontsize=fs)
            ax_pos.set_xlabel('time (s)', fontsize=fs)
            ax_pos.set_ylabel('position', fontsize=fs)
            ax_pos.set_xlim(left=-0.5, right=maxtime)
            ax_pos.set_ylim(LimList[dd])




            # ax_pos.set_ylim([-2, 4])



            ax_vel = plt.subplot2grid((4,self.n_DoF), (1,dd))
            ax_vel.plot(self.timeline, self.vel[:,dd])
            ax_vel.plot(self.real_timeline, self.real_vel[:,dd], color='#2A7E43', lw=2, ls='--')
            ax_vel.axhline(y = 0, c='red', ls='--', lw=2)
            ax_vel.set_title('DoF_'+dof_labels[dd], fontsize=fs)
            ax_vel.set_xlabel('time (s)', fontsize=fs)
            ax_vel.set_ylabel('velocity', fontsize=fs)
            ax_vel.set_xlim(left=-0.5, right=maxtime)

            ax_acc = plt.subplot2grid((4,self.n_DoF), (2,dd))
            ax_acc.plot(self.timeline, self.acc[:,dd])
            ax_acc.plot(self.real_timeline, self.real_acc[:,dd], color='#2A7E43', lw=2, ls='--')
            ax_acc.axhline(y = 0, c='red', ls='--', lw=2)
            ax_acc.set_title('DoF_'+dof_labels[dd], fontsize=fs)
            ax_acc.set_xlabel('time (s)', fontsize=fs)
            ax_acc.set_ylabel('acceleration', fontsize=fs)
            ax_acc.set_xlim(left=-0.5, right=maxtime)

            ax_weights = plt.subplot2grid((4,self.n_DoF), (3,dd))
            ax_weights.plot(self.real_timeline, self.weights[:,dd])
            # ax_weights.axhline(y = 0, c='red', ls='--', lw=2)
            ax_weights.set_title('DoF_'+dof_labels[dd], fontsize=fs)
            ax_weights.set_xlabel('time (s)', fontsize=fs)
            ax_weights.set_ylabel('weight', fontsize=fs)
            ax_weights.set_ylim([0,1])
            ax_weights.set_xlim(left=-0.5, right=maxtime)

        dof_fig.legend([mean_plot, var_plot, waypoints_plot], ['Path Mean', 'Path Variance', 'Waypoints'], loc='upper left')
        plt.subplots_adjust(wspace=0.5, hspace=0.5)

        if savePlot:
            fig.savefig(saveDir + "/trajectory" + extension)
            dof_fig.savefig(saveDir + "/trajectory_dof" + extension)

        if showPlot:
            plt.show()
        else:
            plt.close(dof_fig)
            plt.close(fig)
