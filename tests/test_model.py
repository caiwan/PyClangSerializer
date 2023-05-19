import clang.cindex as clang_index
from gk.source_index.parse_source import parse_source_model


"""
Docs:
    - https://libclang.readthedocs.io/en/latest/_modules/clang/cindex.html
    - https://clang.llvm.org/doxygen/group__CINDEX__CURSOR__MANIP.html
"""


CLANG_PARSE_OPTIONS = (
    clang_index.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
    | clang_index.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES
)


def test_basic_model(clang_index_parser: clang_index.Index):
    src = """
    struct A {
        int a;
        float b;
    };
    """

    translation_unit = clang_index_parser.parse(
        "tmp.cpp",
        args=["-std=c++11"],
        unsaved_files=[("tmp.cpp", src)],
        options=CLANG_PARSE_OPTIONS,
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


def test_basic_model_with_namespace(clang_index_parser: clang_index.Index):
    src = """
    namespace ns1::ns2{
    struct A {
        int a;
        float b;
    };
    }

    namespace ns1{
    namespace ns2{
    struct B {
        int a;
        float b;
    };
    }
    }
    """

    translation_unit = clang_index_parser.parse(
        "tmp.cpp",
        args=["-std=c++11"],
        unsaved_files=[("tmp.cpp", src)],
        options=CLANG_PARSE_OPTIONS,
    )

    source_model = parse_source_model(translation_unit)

    assert source_model
    assert len(source_model.class_types) == 2
    assert source_model.class_types[0].name == "A"
    assert source_model.class_types[0].namespace == "::ns1::ns2"

    assert source_model.class_types[1].name == "B"
    assert source_model.class_types[1].namespace == "::ns1::ns2"

    assert len(source_model.class_types[0].fields) == 2
    assert source_model.class_types[0].fields[0].name == "a"
    assert source_model.class_types[0].fields[0].type == "int"
    assert source_model.class_types[0].fields[1].name == "b"
    assert source_model.class_types[0].fields[1].type == "float"


def test_basic_annotated_model(clang_index_parser: clang_index.Index):
    src = """
    #define SERIALIZABLE(type)
    #define FIELD(type)

    struct A {
        int a;
        float b;
    };

    SERIALIZABLE(A)
    FIELD(A::a)
    FIELD(A::b)
    """

    translation_unit = clang_index_parser.parse(
        "tmp.cpp",
        args=["-std=c++11"],
        unsaved_files=[("tmp.cpp", src)],
        options=CLANG_PARSE_OPTIONS,
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
