from typing import Dict, Tuple, List, Union, Callable
from collections import defaultdict

from more_itertools import always_iterable

import clang.cindex as clang_index

from source_index.model import (
    AccessSpecifier,
    AnnotationDescriptor,
    ClassTypeDescriptor,
    FieldTypeDescriptor,
    FunctionTypeDescriptor,
    SourceModel,
)

import logging

logger = logging.getLogger(__name__)


# TODO: Extract this
class Filter:
    def __init__(self) -> None:
        self._filter_list: List[Tuple[List[clang_index.CursorKind], Callable[[clang_index.Cursor], bool]]] = []

    def add_filter(
        self,
        kinds: Union[clang_index.CursorKind, List[clang_index.CursorKind]],
        filter_fn: Callable[[clang_index.Cursor], bool],
    ):
        self._filter_list.append((always_iterable(kinds), filter_fn))

    def __call__(self, cursor: clang_index.Cursor) -> bool:
        return self.do_filter(cursor)

    def do_filter(self, cursor: clang_index.Cursor) -> bool:
        return (
            all(
                fn(cursor)
                for _, fn in filter(
                    lambda k: cursor.kind in k,
                    [(k, fn) for k, fn in self._filter_list],
                )
            )
            if self._filter_list
            else True
        )


# TODO: Extract this
def build_filter(**kwargs) -> Filter:
    public_only = kwargs.get("allow_public_members_only", True)
    accepted_annotations = kwargs.get("filter_annotations", [])

    filter_fn = Filter()

    if public_only:
        filter_fn.add_filter(
            [
                clang_index.CursorKind.FIELD_DECL,
                clang_index.CursorKind.CLASS_DECL,
                clang_index.CursorKind.STRUCT_DECL,
            ],
            lambda cursor: cursor.access_specifier == clang_index.AccessSpecifier.PUBLIC,
        )

    if accepted_annotations:
        filter_fn.add_filter(
            clang_index.CursorKind.MACRO_INSTANTIATION,
            # TODO: Does it get lost after we may get rid of the object?
            lambda cursor: cursor.spelling in accepted_annotations,
        )

    return filter_fn


_access_specifier_map = {
    clang_index.AccessSpecifier.PUBLIC: AccessSpecifier.PUBLIC,
    clang_index.AccessSpecifier.PRIVATE: AccessSpecifier.PRIVATE,
    clang_index.AccessSpecifier.PROTECTED: AccessSpecifier.PROTECTED,
}


def find_access_specifier(
    access_specifier: clang_index.AccessSpecifier,
) -> AccessSpecifier:
    return _access_specifier_map.get(access_specifier, None)


def fetch_annotation_tokens(cursor: clang_index.Cursor) -> Tuple[str, str, List[str]]:
    extracted_tokens = []
    token_group = []
    for token in cursor.get_tokens():
        token_str = token.spelling
        if token_str not in ["(", ")", ","]:
            token_group.append(token_str)
        else:
            extracted_tokens.append("".join(token_group))
            token_group.clear()

    # TODO Throw an error here if the annotation is malformed
    # At this point only predefied annotations should appear
    return extracted_tokens[0], extracted_tokens[1], extracted_tokens[2:]


def fetch_annotations(
    cursor: clang_index.Cursor,
    filter_fn: Callable[[clang_index.Cursor], bool],
    namespace: str = "",
):
    if cursor.kind in [clang_index.CursorKind.MACRO_INSTANTIATION] and filter_fn(cursor):
        (name, target, arguments) = fetch_annotation_tokens(cursor)
        yield namespace + "::" + target, AnnotationDescriptor(arguments=arguments, name=name)

    elif cursor.kind is clang_index.CursorKind.NAMESPACE:
        namespace += f"::{cursor.spelling}"

    for child in cursor.get_children():
        yield from fetch_annotations(child, filter_fn, namespace)


def fetch_fields(
    cursor: clang_index.Cursor,
    annotation_map: Dict[str, List[AnnotationDescriptor]],
    filter_fn: Callable[[clang_index.Cursor], bool],
    namespace: str,
) -> FieldTypeDescriptor:
    for child in cursor.get_children():
        full_name = f"{namespace}::{child.spelling}"
        annotations = annotation_map.get(full_name, [])
        if child.kind in [clang_index.CursorKind.FIELD_DECL] and filter_fn(cursor):
            yield FieldTypeDescriptor(
                name=child.spelling,
                access_specifier=find_access_specifier(child.access_specifier),
                annotations=annotations,
                type=child.type.spelling,
            )


def fetch_class_defintions(
    cursor: clang_index.Cursor,
    annotation_map: Dict[str, List[AnnotationDescriptor]],
    filter_fn: Callable[[clang_index.Cursor], bool],
    namespace: str = "",
) -> ClassTypeDescriptor:
    if cursor.kind in [
        clang_index.CursorKind.CLASS_DECL,
        clang_index.CursorKind.STRUCT_DECL,
    ] and filter_fn(cursor):
        full_name = f"{namespace}::{cursor.spelling}"
        annotations = annotation_map.get(full_name, [])
        fields = list(fetch_fields(cursor, annotation_map, filter_fn, full_name))
        yield ClassTypeDescriptor(
            namespace=namespace if namespace else "::",
            name=cursor.spelling,
            access_specifier=find_access_specifier(cursor.access_specifier),
            annotations=annotations,
            fields=fields,
        )
    elif cursor.kind is clang_index.CursorKind.NAMESPACE:
        namespace += f"::{cursor.spelling}"

    for child in cursor.get_children():
        yield from fetch_class_defintions(child, annotation_map, filter_fn, namespace)


# ---


def parse_annotations(
    translation_unit: clang_index.TranslationUnit,
    filter_fn: Callable[[clang_index.Cursor], bool],
) -> Dict[str, List[AnnotationDescriptor]]:
    res: Dict[str, List[AnnotationDescriptor]] = defaultdict(list)
    for k, v in fetch_annotations(translation_unit.cursor, filter_fn):
        res[k].append(v)
    return res


def parse_class_types(
    translation_unit: clang_index.TranslationUnit,
    annotation_map: Dict[str, List[AnnotationDescriptor]],
    filter_fn: Callable[[clang_index.Cursor], bool],
) -> ClassTypeDescriptor:
    return list(fetch_class_defintions(translation_unit.cursor, annotation_map, filter_fn))


def parse_function_types(
    translation_unit: clang_index.TranslationUnit,
    annotation_map: Dict[str, List[AnnotationDescriptor]],
    filter_fn: Callable[[clang_index.Cursor], bool],
) -> FunctionTypeDescriptor:
    # TODO
    return []


def parse_source_model(
    translation_unit: clang_index.TranslationUnit,
    filter_fn: Callable[[clang_index.Cursor], bool] = lambda _: True,
) -> SourceModel:
    if translation_unit:
        annotation_map = parse_annotations(translation_unit, filter_fn)

        return SourceModel(
            class_types=parse_class_types(translation_unit, annotation_map, filter_fn),
            function_types=parse_function_types(translation_unit, annotation_map, filter_fn),
        )
    return None


# ---
def _debug_walk_source_model(cursor: clang_index.Cursor, indent=""):
    if not str(cursor.spelling).startswith("_"):
        logger.debug(
            f"{indent} {cursor.spelling} \t {cursor.kind} [{' '.join([j.spelling for j in cursor.get_tokens()])}]"
        )
        for child in cursor.get_children():
            _debug_walk_source_model(child, indent=indent + "  ")


def debug_walk_source_model(translation_unit: clang_index.TranslationUnit):
    _debug_walk_source_model(translation_unit.cursor)
