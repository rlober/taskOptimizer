#ifndef TASKOPTIMIZERMODULE_HPP
#define TASKOPTIMIZERMODULE_HPP

#include <iostream>
#include <yarp/os/RFModule.h>
#include <yarp/os/Module.h>
#include <yarp/os/Network.h>
#include <yarp/os/BufferedPort.h>
#include <yarp/os/Bottle.h>

#include <smlt/nonlinearSolver.hpp>
#include <smlt/bayesianOptimization.hpp>


#include "cmaes.h"



class taskOptimizerModule : public yarp::os::RFModule
{

    private:
        smlt::nonlinearSolver* bopt_solver;

        yarp::os::Network yarp;
        yarp::os::BufferedPort<yarp::os::Bottle> optParamsPortIn;
        yarp::os::BufferedPort<yarp::os::Bottle> optVarsPortIn;
        yarp::os::BufferedPort<yarp::os::Bottle> costPortIn;
        yarp::os::BufferedPort<yarp::os::Bottle> optVarsPortOut;
        yarp::os::RpcServer rpcServerPort;

        smlt::optSolution bopt_solution;
        smlt::optParameters bopt_params;

        bool initialize;
        bool waitingForVariables;
        bool waitingForCostData;

        int nDims;
        Eigen::VectorXd optVariables, costData;


        bool initializeSolver(yarp::os::Bottle* optParamsBottle);
        bool getOptimizationVariablesFromYarp(Eigen::VectorXd& optVars, bool waitForBottle=false);
        bool getCostFromYarp(Eigen::VectorXd& cost, bool waitForBottle=false);
        void sendCurrentOptimalVariablesOverYarp();
        bool checkPortConnections();


        double startTime;

        /************** DataProcessor *************/
        class DataProcessor : public yarp::os::PortReader {
            private:
                taskOptimizerModule& toMod;

            public:
                DataProcessor(taskOptimizerModule& toModRef);

                virtual bool read(yarp::os::ConnectionReader& connection);
        };
        /************** DataProcessor *************/


        DataProcessor* processor;
        void parseRpcMessage(yarp::os::Bottle *input, yarp::os::Bottle *reply);


    public:
        double getPeriod();
        bool updateModule();
        bool configure(yarp::os::ResourceFinder &rf);
        bool interruptModule();
        bool close();
};


#endif
