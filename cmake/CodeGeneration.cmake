# Allows run custom code generation using prototypes

# Bootsreap
if(DEFINED ENV{CLANG_PATH})
	set(CLANG_PATH "$ENV{CLANG_PATH}")
else()
	if(NOT CLANG_PATH)
		message(FATAL_ERROR "Variable CLANG_PATH is not set")
	endif()
endif()

include(CMakeParseArguments)

# Helps create and manage venv inside cmake infrastructure without pollute any existing one
find_package(Python3 COMPONENTS Interpreter REQUIRED)

function(_create_python_venv PY_ENVIRONMENT_NAME PYENV_SCRIPT_PATH)
	message("Creating pyenv: ${PY_ENVIRONMENT_NAME}")

	# TODO: IF venv is already installed, skip
	execute_process(
		COMMAND ${Python3_EXECUTABLE} -m venv ${CMAKE_BINARY_DIR}/${PY_ENVIRONMENT_NAME}
		WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
		RESULT_VARIABLE _error_code
		OUTPUT_VARIABLE _result
		COMMAND_ECHO STDOUT
	)

	string(REGEX REPLACE "\n$" "" _result "${_result}")

	if(_error_code MATCHES "0")
		message("Python OK")
	else()
		message(FATAL_ERROR "Python not installed or requirements not properly set up.\n Exit code: ${_error_code}\n Message: ${_result}")
	endif()

	if(WIN32)
		set(${PYENV_SCRIPT_PATH} ${CMAKE_BINARY_DIR}/${PY_ENVIRONMENT_NAME}/Scripts PARENT_SCOPE)
	elseif(UNIX)
		set(${PYENV_SCRIPT_PATH} ${CMAKE_BINARY_DIR}/${PY_ENVIRONMENT_NAME}/bin PARENT_SCOPE)
	else()
		message(FATAL_ERROR "Unsupported platform")
	endif()
endfunction(_create_python_venv)

function(_string_camel_case_to_lower_snake_case str var)
	string(REGEX REPLACE "(.)([A-Z][a-z]+)" "\\1_\\2" value "${str}")
	string(REGEX REPLACE "([a-z0-9])([A-Z])" "\\1_\\2" value "${value}")
	string(TOLOWER "${value}" value)
	set(${var} "${value}" PARENT_SCOPE)
endfunction(_string_camel_case_to_lower_snake_case)

function(_string_camel_case_to_upper_snake_case str var)
	_string_camel_case_to_lower_snake_case(${str} ${var})
	string(TOUPPER ${str} ${var})
endfunction(_string_camel_case_to_upper_snake_case var str)

# ---
#
# ---
function(initialize_code_generator PACKAGE_PATH)
	if(NOT _PYTHON_CLANG_BINDING_OK)
		_create_python_venv("venv" PYTHON_VENV_SCRIPT_PATH)

		if(WIN32)
			set(PIP_PATH ${PYTHON_VENV_SCRIPT_PATH}/pip.exe)
			set(CLANG_CHECK_PATH ${PYTHON_VENV_SCRIPT_PATH}/check-clang.exe)
			set(_GENERATE_CODE_PATH ${PYTHON_VENV_SCRIPT_PATH}/generate-code.exe PARENT_SCOPE CACHE STRING "Generate code script path" FORCE)
		elseif(UNIX)
			# TODO:
			message(FATAL_ERROR "Unsupported platform")
		else()
			message(FATAL_ERROR "Unsupported platform")
		endif()

		message("Pip install: ${PIP_PATH} install ${PACKAGE_PATH}")
		execute_process(
			COMMAND ${PIP_PATH} install ${PACKAGE_PATH}
			WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
			RESULT_VARIABLE _error_code
			OUTPUT_VARIABLE _result
			COMMAND_ECHO STDOUT
		)
		message("\n${_result}\n")
		if(_error_code MATCHES "0")
			message("Pip install OK")
		else()
			message(FATAL_ERROR "Python not installed or requirements not properly set up.\n Exit code: ${_error_code}")
			set(_PYTHON_CLANG_BINDING_OK 0 PARENT_SCOPE CACHE BOOL "Python clang binding OK" FORCE)
			return()
		endif()

		message("Check clang: ${CLANG_CHECK_PATH} ${CLANG_PATH}")

		execute_process(
			COMMAND ${CLANG_CHECK_PATH} ${CLANG_PATH}
			WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
			RESULT_VARIABLE _error_code
			OUTPUT_VARIABLE _result
			COMMAND_ECHO STDOUT
		)
		message("\n${_result}\n")
		if(_error_code MATCHES 0)
			message("Python Clang binding OK")
		else()
			message(FATAL_ERROR "Python not installed or requirements not properly set up.\n Exit code: ${_error_code}")
			set(_PYTHON_CLANG_BINDING_OK 0 PARENT_SCOPE)
			return()
		endif()

		set(_PYTHON_CLANG_BINDING_OK 0 PARENT_SCOPE CACHE BOOL "Python clang binding OK" FORCE)
	endif()
endfunction()

# ---
# Usage:
# TARGET target to add to
# PRE_BUILD, POST_BUILD or PRE_LINK (PRE_BUILD default)
# SCRIPT script path
#
function(_add_execute_script_target)
	if(NOT _PYTHON_CLANG_BINDING_OK)
		message(FATAL_ERROR "Python clang script is not installed or not properly set up.")
	endif()

	cmake_parse_arguments(
		ARGS # prefix
		"" # flags
		"TARGET;OUTPUT;SCRIPT;SUFFIX" # single-values
		"OPTIONS" # lists
		${ARGN}
	)

	if(NOT ARGS_TARGET AND NOT TARGET ${ARGS_TARGET})
		message(FATAL_ERROR "You must provide a target in parameter TARGET")
	endif()

	if(NOT ARGS_SCRIPT)
		message(FATAL_ERROR "You must provide parameter SCRIPT")
	elseif(NOT EXISTS "${ARGS_SCRIPT}")
		message(FATAL_ERROR "Script ${ARGS_SCRIPT} does not exist")
	endif()

	set(_command ${ARGS_SCRIPT} ${ARGS_OPTIONS})

	add_custom_command(
		TARGET ${ARGS_TARGET}
		PRE_BUILD
		COMMAND ${_command}
		COMMAND_EXPAND_LISTS
		WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
		COMMENT "Executing ${_command}"
	)

	# Execute it during the configuration time too
	execute_process(
		COMMAND ${_command}
		WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
		RESULT_VARIABLE _error_code
		OUTPUT_VARIABLE _result
		COMMAND_ECHO STDOUT
	)
	message("\n${_result}\n")
	if(_error_code MATCHES "0")
		message("Pip install OK")
	else()
		message(FATAL_ERROR "Could not generate code.\n Exit code: ${_error_code}")
		set(_PYTHON_CLANG_BINDING_OK 0 PARENT_SCOPE CACHE BOOL "Python clang binding OK" FORCE)
		return()
	endif()
endfunction(_add_execute_script_target)

# ---

# Usage:
#
# TARGET target which generation will attached to
# OUT_DIR where collected translations are collected
# SOURCES sources to be scanned
# INPUT_DIR directory where sources are
function(add_code_generation_target)
	if(NOT _PYTHON_CLANG_BINDING_OK)
		message(FATAL_ERROR "Clang Python binding Sctipt is not installed or not properly set up.")
	endif()

	cmake_parse_arguments(
		ARGS # prefix
		"" # flags
		"TARGET;OUT_DIR;CONFIG_FILE" # single-values
		"SOURCES;INCLUDE_DIRS" # lists
		${ARGN}
	)

	if(NOT ARGS_TARGET AND NOT TARGET ${ARGS_TARGET})
		message(FATAL_ERROR "You must provide a valid target")
	endif()

	if(NOT ARGS_CONFIG_FILE)
		message(FATAL_ERROR "You must provide a valid output directory")
	endif()

	# TODO: Configure Suffix
	# set(GEN_TARGET "${ARGS_TARGET}_generate")
	set(GEN_TARGET "${ARGS_TARGET}")

	if(NOT TARGET ${GEN_TARGET})
		add_custom_target(${GEN_TARGET})
	endif()

	set(_include_dirs)

	if(ARGS_INCLUDE_DIRS)
		set(_include_dirs "-I" ${ARGS_INCLUDE_DIRS})
	endif(ARGS_INCLUDE_DIRS)

	_add_execute_script_target(
		TARGET ${GEN_TARGET} PRE_BUILD
		SCRIPT ${_GENERATE_CODE_PATH}
		OPTIONS
		"--config" ${ARGS_CONFIG_FILE}
		${_include_dirs}
		"--clang-path" ${CLANG_PATH}
		"--input" ${ARGS_SOURCES}
		"--dir" ${ARGS_OUT_DIR}
	)

	# TODO: return the generated file list
	# TODO: Run generation if any of the input files changed - in config time (?)
endfunction(add_code_generation_target)
