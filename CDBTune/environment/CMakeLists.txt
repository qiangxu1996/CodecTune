cmake_minimum_required(VERSION 3.10)
project(encoder_tune)

set(CMAKE_CXX_STANDARD 17)

include_directories(/usr/local/include)
link_directories(/usr/local/lib)

find_package(OpenCV REQUIRED)
find_package(TBB)

add_subdirectory(pybind11)
pybind11_add_module(encoder_tune encoder_tune.cpp)