set(SOURCES
    main.cpp
)

set(HEADERS
	../include/example/example.hpp
    )

add_executable(Example ${SOURCES} ${HEADERS})

target_include_directories(
    Example
    INTERFACE $<BUILD_INTERFACE:${${PROJECT_NAME}_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)


