from typing import List, Any
from dataclasses import dataclass
import enum

import clang.cindex as clang_index


class AccessSpecifier(enum.Enum):
    NONE = 0
    PRIVATE = 1
    PROTECTED = 2
    PUBLIC = 3


@dataclass
class Descriptor:
    name: str


@dataclass
class AnnotationDescriptor(Descriptor):
    arguments: List[Any]


@dataclass
class AnnotatedDescriptor(Descriptor):
    access_specifier: AccessSpecifier
    annotations: List[AnnotationDescriptor]


@dataclass
class TypeDescriptor(Descriptor):
    type: str


@dataclass
class FunctionTypeDescriptor(AnnotatedDescriptor):
    namespace: str
    return_type: TypeDescriptor
    argument_list: List[TypeDescriptor]


@dataclass
class FieldTypeDescriptor(AnnotatedDescriptor):
    type: str


@dataclass
class PropertyTypeDescriptor(AnnotatedDescriptor):
    setter: FunctionTypeDescriptor
    getter: FieldTypeDescriptor


@dataclass
class ClassTypeDescriptor(AnnotatedDescriptor):
    namespace: str
    fields: List[FieldTypeDescriptor]
    # members = List[FieldTypeDescriptor]


@dataclass
class SourceModel:
    class_types: List[ClassTypeDescriptor]
    function_types: List[FunctionTypeDescriptor]


# ---

# TODO: Optional Filter for public only
# TODO: Optional Filter for certain annotation types

_access_specifier_map = {
    clang_index.AccessSpecifier.PUBLIC: AccessSpecifier.PUBLIC,
    clang_index.AccessSpecifier.PRIVATE: AccessSpecifier.PRIVATE,
    clang_index.AccessSpecifier.PROTECTED: AccessSpecifier.PROTECTED,
}


def find_access_specifier(
    access_specifier: clang_index.AccessSpecifier,
) -> AccessSpecifier:
    return (
        _access_specifier_map[access_specifier]
        if access_specifier in _access_specifier_map
        else AccessSpecifier.NONE
    )


def fetch_fields(cursor: clang_index.Cursor) -> FieldTypeDescriptor:
    for child in cursor.get_children():
        if child.kind in [clang_index.CursorKind.FIELD_DECL]:
            yield FieldTypeDescriptor(
                name=child.spelling,
                access_specifier=find_access_specifier(child.access_specifier),
                annotations=[],
                type=child.type.spelling,
            )


def fetch_class_defintions(cursor: clang_index.Cursor) -> ClassTypeDescriptor:
    annotations = []
    if cursor.kind is clang_index.CursorKind.MACRO_INSTANTIATION:
        annotations.append(
            AnnotationDescriptor(
                name=cursor.spelling,
            )
        )
    elif cursor.kind in [
        clang_index.CursorKind.CLASS_DECL,
        clang_index.CursorKind.STRUCT_DECL,
    ]:
        fields = list(f for f in fetch_fields(cursor))
        yield ClassTypeDescriptor(
            namespace="::",
            name=cursor.spelling,
            access_specifier=find_access_specifier(cursor.access_specifier),
            annotations=[],
            fields=fields,
        )

    for child in cursor.get_children():
        yield from fetch_class_defintions(child)


def parse_class_types(
    translation_unit: clang_index.TranslationUnit,
) -> ClassTypeDescriptor:
    # + add annotations here
    return fetch_class_defintions(translation_unit.cursor)


def parse_function_types(
    translation_unit: clang_index.TranslationUnit,
) -> FunctionTypeDescriptor:
    return []


def parse_source_model(translation_unit: clang_index.TranslationUnit) -> SourceModel:
    # tu.cursor is always a new cursor
    if translation_unit:
        return SourceModel(
            class_types=list(c for c in parse_class_types(translation_unit)),
            function_types=list(f for f in parse_function_types(translation_unit)),
        )
    return None
