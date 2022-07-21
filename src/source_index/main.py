from typing import Any, Dict, List, Tuple
import argparse
import sys
import os
import pathlib
import json

import dataclasses_json
import enum
import uuid

import logging

import clang.cindex as clang_index

from source_index import config
from source_index import parse_source
from source_index import templating_tools


logger = logging.getLogger(__name__)

CLANG_PARSE_OPTIONS = (
    clang_index.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
    | clang_index.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES
)


# TODO -> utils
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)

        if issubclass(type(obj), enum.Enum):
            return str(obj)

        if issubclass(type(obj), dataclasses_json.DataClassJsonMixin):
            return obj.to_dict()

        return json.JSONEncoder.default(self, obj)


def build_argparser() -> argparse.ArgumentParser:
    args = argparse.ArgumentParser(
        description="Collects reflection info from c/c++ sources and renders a template of the reflected information"
    )

    args.add_argument(
        "--config",
        "-c",
        dest="config_path",
        type=str,
        required=True,
        help="App configuration file",
    )

    args.add_argument(
        "--dir",
        "-d",
        dest="target_path",
        type=str,
        required=False,
        help="Target directory of generated sources",
    )

    args.add_argument(
        "--json",
        dest="is_export_json",
        default=False,
        action="store_true",
        help="Exports source reflection as json from template config (skips template substitution)",
    )

    args.add_argument(
        "--input",
        "-i",
        dest="input_files",
        type=str,
        metavar="N",
        nargs="+",
        required=True,
        help="List of input files to be parsed",
    )

    args.add_argument(
        "--includes",
        "-I",
        dest="includes",
        type=str,
        required=False,
        help="Include directories",
    )

    return args


def fetch_args() -> Any:
    return build_argparser().parse_args()


def create_translation_units(
    source_files: List[str],
) -> Tuple[pathlib.Path, clang_index.TranslationUnit]:
    # TODO: Add Includes
    clang_index_parser = clang_index.Index.create()
    for source_file in source_files:
        source_path = pathlib.Path(source_file)
        if source_path.exists():
            yield source_path, clang_index_parser.parse(
                str(source_path),
                args=["-std=c++11"],
                options=CLANG_PARSE_OPTIONS,
            )
        else:
            raise RuntimeError(f"Cannot open file {source_path}")


def main():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    # TODO: Add this to config and/or param
    clang_index.Config.set_library_path(os.getenv("CLANG_PATH"))

    args = fetch_args()
    config_path = pathlib.Path(args.config_path)
    app_config = config.load_app_config(config_path)

    root_dir = pathlib.Path(config_path.parent)
    target_path = pathlib.Path(args.target_path)

    translation_units: Dict[pathlib.Path, clang_index.TranslationUnit] = dict(
        create_translation_units(args.input_files)
    )

    # TODO: Clean this part up
    j2_env = templating_tools.build_jinja_environment(root_dir) if not args.is_export_json else None
    for template_config in app_config.templates:

        for source_name, translation_unit in translation_units.items():
            logger.info(f"Parsing {source_name}")
            parsing_filter = parse_source.build_filter(**template_config.to_dict())
            source_model = parse_source.parse_source_model(translation_unit, parsing_filter)

            target_filename = target_path / pathlib.Path(
                template_config.filename_prefix + source_name.stem + template_config.filename_suffix
            )

            if not args.is_export_json:
                # TODO: Extract this to a function
                template = j2_env.get_template(str(template_config.template))
                logger.info(f"Generating code from {template_config.template}")
                with open(target_filename, "w") as f:
                    result = template.render(
                        header=str(source_name).replace("\\", "/"),
                        model=source_model,
                    )
                    f.write(result)

            else:
                # TODO: Extract this to a function
                json_file = target_filename.with_suffix(".json")
                with open(json_file, "w") as f:
                    logger.info(f"Exporting model to {json_file}")
                    json.dump(source_model, f, cls=CustomJSONEncoder)


if __name__ == "__main__":
    main()
