cmake_minimum_required(VERSION 3.10)
project(encoder_tune)
add_subdirectory(pybind11)
pybind11_add_module(encoder_tune encoder_tune.cpp)