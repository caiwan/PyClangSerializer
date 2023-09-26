project(Example)

set(GENERATED_SOURCES
	./generated/example/serialize_example.cpp
)

set(GENERATED_HEADERS
	${${PROJECT_NAME}_SOURCE_DIR}/../include/example/example.hpp
)

add_library(${PROJECT_NAME}_Generated ${GENERATED_SOURCES} ${GENERATED_HEADERS})

add_code_generation_target(
	TARGET ${PROJECT_NAME}_Generated
	INCLUDE_DIRS ${${PROJECT_NAME}_SOURCE_DIR}/../include
	OUT_DIR ${${PROJECT_NAME}_SOURCE_DIR}/generated/example
	CONFIG_FILE ${${PROJECT_NAME}_SOURCE_DIR}/example-config.yaml
	SOURCES ${GENERATED_HEADERS}
)

target_include_directories(
	${PROJECT_NAME}_Generated
	PRIVATE $<BUILD_INTERFACE:${${PROJECT_NAME}_SOURCE_DIR}/../include>
	INTERFACE $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

#

set(SOURCES
	main.cpp
)

set(HEADERS
	${GENERATED_HEADERS}
)

add_executable(${PROJECT_NAME} ${SOURCES} ${HEADERS})

target_link_libraries(${PROJECT_NAME} ${PROJECT_NAME}_Generated)

target_include_directories(
	Example
	PRIVATE $<BUILD_INTERFACE:${${PROJECT_NAME}_SOURCE_DIR}/../include>
	INTERFACE $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)
