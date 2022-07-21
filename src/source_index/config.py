from typing import List, Optional
from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin
import pathlib
import yaml


@dataclass
class TemplateConfig(DataClassJsonMixin):
    template: str
    filter_annotations: List[str]
    filename_suffix: str
    filename_prefix: Optional[str] = ""
    allow_public_members_only: Optional[bool] = True


@dataclass
class AppConfig(DataClassJsonMixin):
    templates: List[TemplateConfig]


def load_app_config(config_file: pathlib.Path) -> AppConfig:
    with open(config_file, "r") as f:
        return AppConfig.schema().load(yaml.safe_load(f))
