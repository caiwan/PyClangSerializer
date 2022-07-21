# MyProject
cmake_minimum_required(VERSION 3.15)
project(Threadpool VERSION 0.1.0 LANGUAGES C CXX)

cmake_policy(SET CMP0074 NEW)

set_property(GLOBAL PROPERTY USE_FOLDERS ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/../cmake/" ${CMAKE_MODULE_PATH})

include(CodeGeneration)

initialize_code_generator("${CMAKE_CURRENT_SOURCE_DIR}/../dist/gk_source_index-0.1-py3-none-any.whl")

add_subdirectory(src)
