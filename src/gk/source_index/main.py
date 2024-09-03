from typing import Any, Dict, List, Optional, Tuple
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

from gk.source_index import config
from gk.source_index import parse_source
from gk.source_index import templating_tools


LOGGER = logging.getLogger(__name__)

CLANG_PARSE_OPTIONS = (
    clang_index.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
    | clang_index.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES
    | clang_index.TranslationUnit.PARSE_INCOMPLETE
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

    args.add_argument(
        "--clang-path",
        "-C",
        dest="clang_path",
        type=str,
        required=False,
        help="Path to clang library",
        default=None, #os.getenv("CLANG_PATH"),
    )

    return args


def fetch_args() -> Any:
    return build_argparser().parse_args()

# TOOD -> utils
def find_relative_path(
    file_path: pathlib.Path, directories: List[pathlib.Path]
) -> Optional[pathlib.Path]:
    for directory in sorted(directories, key=lambda path: len(path.parts), reverse=True):
        try:
            relative_path = file_path.relative_to(directory)
            return relative_path
        except ValueError:
            continue
    return None


def create_translation_units(
    source_files: List[str],
) -> Tuple[pathlib.Path, clang_index.TranslationUnit]:
    # TODO: Add Includes
    clang_index_parser = clang_index.Index.create()
    for source_file in source_files:
        source_path = pathlib.Path(source_file)
        if source_path.exists():
            logging.info(f"Creating translation unit for {source_path}")
            yield source_path.absolute(), clang_index_parser.parse(
                str(source_path),
                args=["-std=c++11"],
                options=CLANG_PARSE_OPTIONS,
            )
        else:
            raise RuntimeError(f"Cannot open file {source_path}")


# TODO: Typing
def write_template(j2_env, template_config, header_file, source_model, target_filename):
    template = j2_env.get_template(str(template_config.template))
    LOGGER.info(f"Generating code from {template_config.template}")
    with target_filename.open("w") as f:
        result = template.render(
            header=str(header_file),
            model=source_model,
        )
        f.write(result)


# TODO: Typing
def export_json(source_model, target_filename):
    target_json = target_filename.with_suffix(".json")
    with target_json.open("w") as f:
        LOGGER.info(f"Exporting model to {target_json}")
        json.dump(source_model, f, cls=CustomJSONEncoder)


def execute(app_config, args, root_dir):
    target_path = pathlib.Path(args.target_path)
    target_path.mkdir(parents=True, exist_ok=True)

    translation_units: Dict[pathlib.Path, clang_index.TranslationUnit] = dict(
        create_translation_units(args.input_files)
    )

    j2_env = (
        templating_tools.build_jinja_environment(root_dir)
        if not args.is_export_json
        else None
    )
    for template_config in app_config.templates:
        for header_file, translation_unit in translation_units.items():
            target_file = target_path / pathlib.Path(
                template_config.filename_prefix
                + header_file.stem
                + template_config.filename_suffix
            )

            # Skip if the target file is newer than the source file
            if header_file.stat().st_mtime < target_file.stat().st_mtime:
                LOGGER.info(f"Skipping {header_file} (target file is newer)")
                continue

            LOGGER.info(f"Parsing {header_file}")
            parsing_filter = parse_source.build_filter(**template_config.to_dict())
            source_model = parse_source.parse_source_model(
                translation_unit, parsing_filter
            )

            if not args.is_export_json:
                header_include_path = find_relative_path(header_file, args.includes) or header_file
                write_template(
                    j2_env,
                    template_config,
                    header_include_path,
                    source_model,
                    target_file,
                )
            else:
                export_json(source_model, target_file)


def main():
    logging.basicConfig(
        stream=sys.stdout, level=logging.INFO, format="[%(levelname)s] %(message)s"
    )  # noqa: E501

    args = fetch_args()

    if args.clang_path is not None:
        clang_index.Config.set_library_path(args.clang_path)
        logging.info(f"Using clang library path: {args.clang_path}")

    config_path = pathlib.Path(args.config_path)
    app_config = config.load_app_config(config_path)

    root_dir = pathlib.Path(config_path.parent)

    try:
        execute(app_config, args, root_dir)
    except Exception as e:
        LOGGER.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
