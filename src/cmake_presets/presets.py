from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, final
import json

from dataclasses_json import DataClassJsonMixin, LetterCase, config, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Base:
    name: str
    hidden: Optional[bool] = False
    inherits: list[str] = field(default_factory=list)
    condition: Any = None
    vendor: dict = field(default_factory=dict)
    display: Optional[str] = field(default=None, metadata=config(field_name="displayName"))
    description: Optional[str] = None
    environment: dict = field(default_factory=dict)

    @property
    def display_name(self) -> str:
        return self.display or self.name


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
@final
class Configure(Base):
    generator: Optional[str] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
@final
class Build(Base):
    verbose: bool = False
    # This can't ever be empty, however, because of how python dataclasses
    # work, we can't *just* declare this
    configure_preset: str = field(default_factory=str)
    inherit_configure_environment: bool = False
    jobs: Optional[int] = None
    target: Optional[str | list[str]] = None
    clean_first: Optional[bool] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
@final
class Test(Base):
    configure_preset: str = field(default_factory=str)
    overwrite_configuration_file: list[str] = field(default_factory=list)
    # TODO: fill out the rest of the fields


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
@final
class Package(Base):
    pass


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
@final
class File(DataClassJsonMixin):
    version: int
    cmake_minimum_required: dict
    configure_presets: list[Configure] = field(default_factory=list)
    build_presets: list[Build] = field(default_factory=list)
    include: list[str] = field(default_factory=list)
    vendor: dict = field(default_factory=dict)
    path: Path = field(init=False)


def load(path: Path) -> File:
    with path.open() as presets:
        presets = File.from_dict(json.load(presets))
        presets.path = path
        return presets
