cmake_minimum_required(VERSION 3.10)
project(codec_driver)

set(CMAKE_CXX_STANDARD 17)

include_directories(/usr/local/include)
link_directories(/usr/local/lib)

#bell config
include_directories(/home/alexa157/x265_git/source/)
include_directories(/home/alexa157/x265_git/build/linux/)
link_directories(/home/alexa157/x265_git/build/linux/)
#end bell config

find_package(OpenCV REQUIRED)
find_package(TBB)

add_executable(codec_driver main.cpp)
target_link_libraries(codec_driver ${OpenCV_LIBS} TBB::tbb x265 pthread)
