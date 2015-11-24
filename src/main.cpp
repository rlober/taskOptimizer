#include "taskOptimizerModule.hpp"
#include <iostream>

using namespace yarp::os;
using namespace std;

int main(int argc, char * argv[])
{
    Network yarp;

    taskOptimizerModule module;
    ResourceFinder rf;
    rf.setVerbose();
    rf.setDefaultConfigFile("config.ini");
    rf.setDefaultContext("taskOptimizer");
    rf.configure(argc, argv);

    cout<<"Configure module & start module..."<<endl;
    if (!module.runModule(rf))
    {
        cerr<<"Error module did not start"<<endl;
        return 1;
    }

    cout<<"Main returning..."<<endl;
    return 0;
}
