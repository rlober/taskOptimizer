cmake_minimum_required(VERSION 2.8.9)
project(taskOptimizer CXX)
SET(CMAKE_CXX_FLAGS "-std=c++11")
find_package(YARP REQUIRED)

set(SMLT_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake/Modules)

list(APPEND CMAKE_MODULE_PATH ${YARP_MODULE_PATH} ${SMLT_MODULE_PATH})

find_package(Eigen REQUIRED)
find_package(PkgConfig REQUIRED)
find_package(SMLT REQUIRED)

# PKG_CHECK_MODULES(CMAES libcmaes REQUIRED)

if(SMLT_FOUND)
    message("Found SMLT version: ${SMLT_VERSION}" )
endif(SMLT_FOUND)

find_package(Boost COMPONENTS system filesystem REQUIRED)

file(GLOB folder_source src/*.cpp)
file(GLOB folder_header include/*.hpp)
source_group("Source Files" FILES ${folder_source})
source_group("Header Files" FILES ${folder_header})


include_directories(include/
                    ${YARP_INCLUDE_DIRS}
                    ${SMLT_INCLUDE_DIRS}
                    ${Eigen_INCLUDE_DIRS}
                    # ${CMAES_INCLUDE_DIRS}
                    )

add_executable(${PROJECT_NAME} ${folder_source} ${folder_header})

target_link_libraries(${PROJECT_NAME}
                        ${YARP_LIBRARIES}
                        ${SMLT_LIBRARIES}
                        ${Boost_LIBRARIES}
                        # ${CMAES_LIBRARIES}
                        )

INSTALL(TARGETS ${PROJECT_NAME} DESTINATION bin)

# add_subdirectory(app)
