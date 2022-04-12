import clang.cindex as clang_index
from source_index.source_model import parse_source_model


"""
Docs:
    - https://libclang.readthedocs.io/en/latest/_modules/clang/cindex.html
    - https://clang.llvm.org/doxygen/group__CINDEX__CURSOR__MANIP.html
"""


def test_basic_model(clang_index_parser: clang_index.Index):
    src = """
    struct A {
        int a;
        float b;
    };
    """

    translation_unit = clang_index_parser.parse(
        "tmp.cpp", args=["-std=c++11"], unsaved_files=[("tmp.cpp", src)], options=0
    )

    source_model = parse_source_model(translation_unit)

    assert source_model
    assert len(source_model.class_types) == 1
    assert source_model.class_types[0].name == "A"
    assert source_model.class_types[0].namespace == "::"

    assert len(source_model.class_types[0].fields) == 2
    assert source_model.class_types[0].fields[0].name == "a"
    assert source_model.class_types[0].fields[0].type == "int"
    assert source_model.class_types[0].fields[1].name == "b"
    assert source_model.class_types[0].fields[1].type == "float"


def test_basic_annotated_model(clang_index_parser: clang_index.Index):
    src = """
    #define SERIALIZABLE(x)
    #define FIELD

    SERIALIZABLE()
    struct A {
        FIELD
        int a;

        FIELD
        float b;
    };

    """

    translation_unit = clang_index_parser.parse(
        "tmp.cpp", args=["-std=c++11"], unsaved_files=[("tmp.cpp", src)], options=0
    )

    source_model = parse_source_model(translation_unit)

    assert source_model
    assert len(source_model.class_types) == 1
    assert len(source_model.class_types[0].annotations) == 1
    assert source_model.class_types[0].annotations[0].name == "SERIALIZABLE"
    assert len(source_model.class_types[0].annotations[0].arguments) == 0

    assert len(source_model.class_types[0].fields) == 2
    assert len(source_model.class_types[0].fields[0].annotations) == 1
    assert source_model.class_types[0].fields[0].annotations[0].name == "FIELD"

    assert len(source_model.class_types[0].fields[1].annotations) == 1
    assert source_model.class_types[0].fields[1].annotations[0].name == "FIELD"
