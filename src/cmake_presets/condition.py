from __future__ import annotations

from dataclasses import dataclass, field
from re import Pattern
from typing import Literal

from dataclasses_json import config


@dataclass
class Const:
    value: bool

    def __bool__(self) -> bool:
        return self.value


@dataclass
class Equals:
    lhs: str
    rhs: str

    def __bool__(self) -> bool:
        return self.lhs == self.rhs


@dataclass
class NotEquals:
    lhs: str
    rhs: str

    def __bool__(self) -> bool:
        return self.lhs != self.rhs


@dataclass
class InList:
    string: str
    items: list[str] = field(default_factory=list, metadata=config(field_name="list"))

    def __bool__(self) -> bool:
        return self.string in self.items


@dataclass
class NotInList(InList):
    def __bool__(self) -> bool:
        return not super().__bool__()


@dataclass
class Matches:
    string: str
    regex: Pattern

    def __bool__(self) -> bool:
        return self.regex.match(self.string) is not None


@dataclass
class NotMatches(Matches):
    def __bool__(self) -> bool:
        return not super().__bool__()


@dataclass
class AllOf:
    conditions: list[Condition] = field(default_factory=list)

    def __bool__(self) -> bool:
        return all(self.conditions)


@dataclass
class AnyOf:
    conditions: list[Condition] = field(default_factory=list)

    def __bool__(self) -> bool:
        return any(self.conditions)


@dataclass
class Not:
    condition: Condition

    def __bool__(self) -> bool:
        return not bool(self.condition)


Comparison = Literal["equals", "notEquals", "inList", "notInList", "matches", "notMatches"]
Aggregate = Literal["allOf", "anyOf"]
Inversion = Literal["not"]


@dataclass
class Condition:
    type: Literal["const"] | Comparison | Aggregate | Not

    def __bool__(self) -> bool:
        return bool(self.type)
