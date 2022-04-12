# Adds the files to the corresponding group bsed on their type and path, visual studio style
# caiwan/IR

function(assign_source_group)
  foreach (_source IN ITEMS ${ARGN})
    if (IS_ABSOLUTE "${_source}")
      file(RELATIVE_PATH _source_rel "${CMAKE_CURRENT_SOURCE_DIR}" "${_source}")
    else ()
      set(source_rel "${_source}")
    endif ()

    get_filename_component(_source_path "${_source_rel}" PATH)

    set(_source_group_path "${_source_path}")
    string(REPLACE "../include" "" _source_group_path "${_source_group_path}")
    string(REPLACE "../" "" _source_group_path "${_source_group_path}")
    string(REPLACE "/" "\\" _source_group_path "${_source_group_path}")

    if ("${_source}" MATCHES ".*\\.(c(p|x)*|inc)\\s?")
      set(_source_group_path "Source Files\\${_source_group_path}")

    elseif ("${_source}" MATCHES ".*\\.(h(p|x)*|inl)\\s?")
      set(_source_group_path "Header Files\\${_source_group_path}")

    elseif ("${_source}" MATCHES ".*\\.(js|qs|lua)\\s?")
      set(_source_group_path "Script Files\\${_source_group_path}")

    elseif ("${_source}" MATCHES ".*\\.(hlsl|fx)\\s?")
      set(_source_group_path "Shader Files\\${_source_group_path}")

    elseif ("${_source}" MATCHES ".*\\.(ui)\\s?")
      set(_source_group_path "UI Files\\${_source_group_path}")

    elseif ("${_source}" MATCHES ".*\\.(py)\\s?")
      set(_source_group_path "Source Files\\${_source_group_path}")

      #    elseif("${_source}" MATCHES ".*\\.(blend)\\s?")
      #      set(_source_group_path "Blender Files\\${_source_group_path}")

    else ()
      set(_source_group_path "Resource Files\\${_source_group_path}")

    endif ()

    source_group("${_source_group_path}" FILES "${_source}")

  endforeach ()

endfunction(assign_source_group)

##
##

function(assign_custom_source_group SOURCE_GRP IN_FILES)
  foreach (_source IN ITEMS ${IN_FILES})
    if (IS_ABSOLUTE "${_source}")
      file(RELATIVE_PATH _source_rel "${CMAKE_CURRENT_SOURCE_DIR}" "${_source}")
    else ()
      set(source_rel "${_source}")
    endif ()

    get_filename_component(_source_path "${_source_rel}" PATH)

    set(_source_group_path "${_source_path}")
    string(REPLACE "../include" "" _source_group_path "${_source_group_path}")
    string(REPLACE "../" "" _source_group_path "${_source_group_path}")
    string(REPLACE "/" "\\" _source_group_path "${_source_group_path}")

    source_group("${SOURCE_GRP}/${_source_group_path}" FILES "${_source}")

  endforeach ()
endfunction(assign_custom_source_group)
