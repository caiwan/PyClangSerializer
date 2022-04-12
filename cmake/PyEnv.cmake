# Helps create and manage venv inside cmake infrastructure without pollute any existing one
find_package(Python3 COMPONENTS Interpreter REQUIRED)

function(create_python_venv PY_ENVIRONMENT_NAME PY_EXECUTABLE_NAME)
  message("Creating pyenv: ${PY_ENVIRONMENT_NAME}")

  # TODO: IF venv is already installed, skip

  execute_process(
    COMMAND ${Python3_EXECUTABLE} -m venv ${CMAKE_BINARY_DIR}/${PY_ENVIRONMENT_NAME}
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    RESULT_VARIABLE _error_code
    OUTPUT_VARIABLE _result
  )

  string(REGEX REPLACE "\n$" "" _result "${_result}")

  if (_error_code MATCHES "0")
      message("Python OK")
  else ()
      message(FATAL_ERROR "Python not installed or requirements not properly set up.\n Exit code: ${_error_code}\n Message: ${_result}")
  endif ()

  # TODO: If win32...
  set(${PY_EXECUTABLE_NAME} ${CMAKE_BINARY_DIR}/${PY_ENVIRONMENT_NAME}/Scripts/python.exe PARENT_SCOPE)

endfunction()
