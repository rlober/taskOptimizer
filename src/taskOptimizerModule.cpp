#include "taskOptimizerModule.hpp"
#ifndef TIME_BETWEEN_CONNECTION_CHECKS
#define TIME_BETWEEN_CONNECTION_CHECKS 5.0
#endif


using namespace yarp::os;
using namespace std;



double taskOptimizerModule::getPeriod()
{
    return 0.01; //module periodicity (seconds)
}

/*
* This is our main function. Will be called periodically every getPeriod() seconds.
*/
bool taskOptimizerModule::updateModule()
{
    if (initialize) {
        yarp::os::Bottle *optParamsBottle = optParamsPortIn.read(true);
        if (optParamsBottle!=NULL) {
          std::cout <<"Received the following optimization parameters:\n" << optParamsBottle->toString() << std::endl;
          initializeSolver(optParamsBottle);
        }
        bool waitForBottle = true;
        getOptimizationVariablesFromYarp(optVariables, waitForBottle);
        getCostFromYarp(costData, waitForBottle);

        std::cout << "Initializing optimization." << std::endl;
        bopt_solution = bopt_solver->initialize(Eigen::MatrixXd(optVariables), costData);

        sendCurrentOptimalVariablesOverYarp();
        startTime = yarp::os::Time::now();
        initialize = false;
    }

    while (!bopt_solution.optimumFound) {

        if(getOptimizationVariablesFromYarp(optVariables) && waitingForVariables){waitingForVariables = false;}
        if(getCostFromYarp(costData) && waitingForCostData){waitingForCostData = false;}

        if(!waitingForVariables && !waitingForCostData)
        {
            //evalutate new parameters:
            std::cout << "Updating solver with new optimization variables and cost data." << std::endl;
            // bopt_solution = bopt_solver->update(bopt_solution.optimalParameters, costData);
            bopt_solution = bopt_solver->update(Eigen::MatrixXd(optVariables), costData);
            sendCurrentOptimalVariablesOverYarp();
            waitingForVariables = true;
            waitingForCostData = true;
        }

        // TODO: Check if connected and restart optimization if not.
        // if((yarp::os::Time::now()-startTime) >= TIME_BETWEEN_CONNECTION_CHECKS)
        // {
        //     if (!checkPortConnections())
        //     {
        //        bopt_solution.optimumFound = true;
        //        initialize = true;
        //        std::cout << "Lost connection to controller thread. Resetting the optimizer module." << std::endl;
        //     }
        // }
    }


    return true;
}


/**************************************************************************************************
                                    Nested PortReader Class
**************************************************************************************************/
taskOptimizerModule::DataProcessor::DataProcessor(taskOptimizerModule& toModRef):toMod(toModRef)
{
    //do nothing
}

bool taskOptimizerModule::DataProcessor::read(yarp::os::ConnectionReader& connection)
{
    yarp::os::Bottle input, reply;
    bool ok = input.read(connection);
    if (!ok)
        return false;

    else{
        toMod.parseRpcMessage(&input, &reply);
        yarp::os::ConnectionWriter *returnToSender = connection.getWriter();
        if (returnToSender!=NULL) {
            reply.write(*returnToSender);
        }
        return true;
    }
}
/**************************************************************************************************
**************************************************************************************************/
void taskOptimizerModule::parseRpcMessage(yarp::os::Bottle *input, yarp::os::Bottle *reply)
{
    reply->clear();
    std::string query = input->get(0).asString();
    if (query=="iteration") {
        int currentIter = bopt_solution.nIter;
        reply->addInt(currentIter);
        if (currentIter>0) {
            reply->addInt(bopt_solution.optimumFound);
            for (int j=0; j < bopt_solution.optimalParameters.size(); j++){
                reply->addDouble(bopt_solution.optimalParameters[j]);
            }
        }
    }
}


bool taskOptimizerModule::checkPortConnections()
{
    bool retVal = true;
    retVal = retVal && yarp::os::Network::isConnected("/opt/task/vars:o", "/opt/solver/vars:i");
    if(!retVal){std::cout << "/opt/task/vars:o --and-- /opt/solver/vars:i\tAre not connected!" << std::endl;}
    retVal = retVal && yarp::os::Network::isConnected("/opt/task/cost:o", "/opt/solver/cost:i");
    if(!retVal){std::cout << "/opt/task/cost:o --and-- /opt/solver/cost:i\tAre not connected!" << std::endl;}
    retVal = retVal && yarp::os::Network::isConnected("/opt/solver/vars:o", "/opt/task/vars:i");
    if(!retVal){std::cout << "/opt/solver/vars:o --and-- /opt/task/vars:i\tAre not connected!" << std::endl;}
    retVal = retVal && yarp::os::Network::isConnected("/opt/task/params:o", "/opt/solver/params:i");
    if(!retVal){std::cout << "/opt/task/params:o --and-- /opt/solver/params:i\tAre not connected!" << std::endl;}
    return retVal;
}

bool taskOptimizerModule::getOptimizationVariablesFromYarp(Eigen::VectorXd& optVars, bool waitForBottle)
{
    yarp::os::Bottle *optVarsBottle = optVarsPortIn.read(waitForBottle);
    if (optVarsBottle!=NULL) {
      std::cout <<"Got new optimization variables: " << optVarsBottle->toString() << std::endl;
      for(int i=0; i<nDims; i++)
      {
          optVars(i) = optVarsBottle->get(i).asDouble();
      }
      return true;
    }
    else{return false;}
}


bool taskOptimizerModule::getCostFromYarp(Eigen::VectorXd& cost, bool waitForBottle)
{
    yarp::os::Bottle *optCostBottle = costPortIn.read(waitForBottle);
    if (optCostBottle!=NULL) {
      std::cout <<"Got new cost: " << optCostBottle->toString() << std::endl;
      cost(0) = optCostBottle->get(0).asDouble();
      return true;
    }
    else{return false;}
}

void taskOptimizerModule::sendCurrentOptimalVariablesOverYarp()
{
    yarp::os::Bottle& optVarsBottle = optVarsPortOut.prepare();
    optVarsBottle.clear();
    optVarsBottle.addInt(bopt_solution.optimumFound);
    // TODO: Add a string whether the maxIter or convergence was reached.
    // if (bopt_solution.optimumFound) {
    //
    //     optVarsBottle.addString();
    // }

    for(int i=0; i<nDims; i++)
    {
        optVarsBottle.addDouble(bopt_solution.optimalParameters(i));
    }
    optVarsPortOut.write();
}

/*
* Configure function. Receive a previously initialized
* resource finder object. Use it to configure your module.
* Open port and attach it to message handler.
*/
bool taskOptimizerModule::configure(yarp::os::ResourceFinder &rf)
{

    bool portsOpened = optVarsPortIn.open("/opt/solver/vars:i");
    portsOpened = portsOpened && costPortIn.open("/opt/solver/cost:i");
    portsOpened = portsOpened && optVarsPortOut.open("/opt/solver/vars:o");
    portsOpened = portsOpened && optParamsPortIn.open("/opt/solver/params:i");
    portsOpened = portsOpened && rpcServerPort.open("/opt/solver/rpc:s");

    if(portsOpened){
        bopt_solution = smlt::optSolution();
        processor = new DataProcessor(*this);
        rpcServerPort.setReader(*processor);
        waitingForVariables = true;
        waitingForCostData = true;
        initialize = true;
        return true;
    }
    else{
        std::cout << "Error opening module ports. Please check that yarpserver is running." << std::endl;
        return false;
    }


}

/*
* Interrupt function.
*/
bool taskOptimizerModule::interruptModule()
{
    cout<<"Interrupting your module, for port cleanup"<<endl;
    optVarsPortIn.close();
    costPortIn.close();
    optVarsPortOut.close();
    optParamsPortIn.close();
    rpcServerPort.close();
    return true;
}

/*
* Close function, to perform cleanup.
*/
bool taskOptimizerModule::close()
{
    cout<<"Calling close function\n";

    return true;
}


bool taskOptimizerModule::initializeSolver(yarp::os::Bottle* optParamsBottle)
{
    bopt_params = smlt::optParameters();
    int bottleIndex = 0;

    nDims = optParamsBottle->get(bottleIndex).asInt(); // number of optimization variables

    bottleIndex++;
    optVariables.resize(nDims);
    costData.resize(1);

    bopt_params.searchSpaceMinBound.resize(nDims);
    bopt_params.searchSpaceMaxBound.resize(nDims);

    for(int i=0; i<nDims; i++)
    {
        bopt_params.searchSpaceMinBound(i) = optParamsBottle->get(bottleIndex).asDouble();
        bottleIndex++;
    }
    for(int i=0; i<nDims; i++)
    {
        bopt_params.searchSpaceMaxBound(i) = optParamsBottle->get(bottleIndex).asDouble();
        bottleIndex++;
    }

    // logDirPath = "/home/ryan/Desktop/tmp-test/"; // Get from RF
    // bopt_params.dataLogDir = "/home/ryan/Desktop/tmp-test/";
    bopt_params.dataLogDirPrefix = optParamsBottle->get(bottleIndex).asString();
    bottleIndex++;
    bopt_params.dataLogDir = optParamsBottle->get(bottleIndex).asString();
    bottleIndex++;

    bopt_params.normalize = true;

    // bopt_params.gridSteps.resize(nDims);
    // bopt_params.gridSteps << 10; //, 10;

    bopt_params.gridSteps = Eigen::VectorXi::Constant(nDims, 20);
    bopt_params.maxIter = 30;
    bopt_params.logData = true;
    bopt_params.minConfidence = 99;


    bopt_params.costCovariance = Eigen::MatrixXd::Identity(nDims,nDims);//testTrajectory->getBoptCovarianceMatrix();

    bopt_params.costMaxCovariance = Eigen::VectorXd::Ones(1);

    std::cout << "Optimization parameters:\n" << bopt_params << std::endl;

    bopt_solver = new smlt::bayesianOptimization(bopt_params);

    bopt_solver->setCovarianceScalingFactor(optParamsBottle->get(bottleIndex).asDouble());


}
