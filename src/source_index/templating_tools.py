from typing import List

import jinja2
import pathlib

from source_index.model import AnnotatedDescriptor


def _filter_with_annotations(items: List[AnnotatedDescriptor], annotation: str) -> List[AnnotatedDescriptor]:
    return filter(lambda item: annotation in set([a.name for a in item.annotations]), items)


def _sanitize_namespace(namespace: str) -> str:
    if namespace.startswith("::"):
        return namespace.split("::", 1)[1]
    return namespace


_JINJA_FILTERS = {
    "ns": _sanitize_namespace,
    "with_annotation": _filter_with_annotations,
}


def build_jinja_environment(root_dir: pathlib.Path) -> jinja2.Environment:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(root_dir)),
        trim_blocks=True,
    )

    env.filters.update(_JINJA_FILTERS)

    return env
