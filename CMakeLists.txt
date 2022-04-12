cmake_minimum_required(VERSION 3.15)
project(CodeGenerationPOC
    VERSION 0.0.1
    LANGUAGES CXX
    )

# ---

option(BUILD_TESTS "Build all tests." ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ---

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake/")

# ---
include(CodeGeneration)

set(SOURCE_FILES
    src/main.cpp
    )

set(INCLUDE_FILES
    include/HelloWorld/translation.h
    )

add_executable(${PROJECT_NAME}_HelloWorld ${SOURCE_FILES} ${INCLUDE_FILES})

target_include_directories(${PROJECT_NAME}_HelloWorld
    INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/include/
    PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include/
    )

add_collect_translations_target(
    TARGET ${PROJECT_NAME}_HelloWorld
    SOURCES ${SOURCE_FILES}
    INPUT_DIRS ${CMAKE_CURRENT_SOURCE_DIR}
    INCLUDE_DIRS ${CMAKE_CURRENT_SOURCE_DIR}/src ${CMAKE_CURRENT_SOURCE_DIR}/include
    OUT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/translations
)

