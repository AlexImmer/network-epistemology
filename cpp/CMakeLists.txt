cmake_minimum_required(VERSION 3.10)
project(cpp)

set(CMAKE_CXX_STANDARD 11)

FIND_PACKAGE(Boost 1.40 COMPONENTS system serialization REQUIRED)
INCLUDE_DIRECTORIES(${Boost_INCLUDE_DIR})

add_executable(cpp main.cpp io.cpp io.h)

TARGET_LINK_LIBRARIES(cpp LINK_PUBLIC ${Boost_LIBRARIES})