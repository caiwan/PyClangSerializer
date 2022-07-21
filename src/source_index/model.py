from typing import List, Any
from dataclasses import dataclass
import enum
from dataclasses_json import DataClassJsonMixin


class AccessSpecifier(enum.Enum):
    NONE = 0
    PRIVATE = 1
    PROTECTED = 2
    PUBLIC = 3


@dataclass
class Descriptor(DataClassJsonMixin):
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
class SourceModel(DataClassJsonMixin):
    class_types: List[ClassTypeDescriptor]
    function_types: List[FunctionTypeDescriptor]
