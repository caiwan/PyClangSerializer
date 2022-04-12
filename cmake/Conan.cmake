option(CONAN_PROFILE "Conan profile" "default")

# --- Install conan dependencies
if (CONAN_EXPORTED) # in conan local cache
	# standard conan installation, deps will be defined in conanfile.py
	# and not necessary to call conan again, conan is already running
	include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
	conan_basic_setup()

else ()
	if (NOT EXISTS "${CMAKE_BINARY_DIR}/conan.cmake")
		message(STATUS "Downloading conan.cmake from https://github.com/conan-io/cmake-conan")
		file(DOWNLOAD "https://raw.githubusercontent.com/conan-io/cmake-conan/develop/conan.cmake"
			"${CMAKE_BINARY_DIR}/conan.cmake")
	endif ()
	include(${CMAKE_BINARY_DIR}/conan.cmake)

	# conan_add_remote(NAME jinncrafters INDEX 1 URL https://api.bintray.com/conan/jinncrafters/conan)

	conan_cmake_run(CONANFILE conanfile.txt
        PROFILE ${CONAN_PROFILE}
		BUILD missing
		BASIC_SETUP
		CMAKE_TARGETS
		CONFIGURATION_TYPES "Release;Debug;RelWithDebInfo;MinSizeRel"
		)
endif ()
