from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Pattern

from dataclasses_json import DataClassJsonMixin, LetterCase, config, dataclass_json


@dataclass
class SkipIf(Mapping):
    condition: str | bool
    reason: str = ""

    def __iter__(self):
        yield "condition"
        if self.reason:
            yield "reason"

    def __getitem__(self, key):
        return getattr(self, key)

    def __len__(self) -> int:
        return 2 if self.reason else 1

    # NOTE: pyright is not smart enough to let us use a `match` here, which
    # would work just fine.
    @staticmethod
    def decode(item: Optional[str | bool | dict]):
        if item is None:
            return None
        elif isinstance(item, dict):
            return SkipIf(**item)
        return SkipIf(item)


@dataclass
class ExpectedFail(Mapping):
    condition: str | bool
    reason: str = ""
    strict: bool = False
    run: bool = True

    def __iter__(self):
        yield from ["condition", "strict", "run"]
        if self.reason:
            yield "reason"

    def __getitem__(self, key):
        return getattr(self, key)

    def __len__(self) -> int:
        return 4 if self.reason else 3

    @staticmethod
    def decode(item: Optional[str | bool | dict]):
        if item is None:
            return None
        elif isinstance(item, dict):
            return ExpectedFail(**item)
        return ExpectedFail(item)


@dataclass_json(letter_case=LetterCase.KEBAB)
@dataclass
class VendorProperties(DataClassJsonMixin):
    """
    These can be applied across an entire file of presets *or* a single preset.
    Fixtures are currently unused (because really *what does that end up
    meaning* in our usecase???)

    Each of these are pulled from CMake's properties, with *some* exceptions
    where we've also added support for some of pytest's markers:

        skip-if: str (condition) | { condition: str, reason: str }
        expected-fail: ...

    """

    skip: str = ""
    xfail: Optional[ExpectedFail] = field(
        default=None,
        metadata=config(decoder=ExpectedFail.decode),
    )
    skip_if: Optional[SkipIf] = field(default=None, metadata=config(decoder=SkipIf.decode))

    will_fail: bool = False
    """ Inverts the pass/fail flag of the test. Useful for non-zero return codes """
    pass_regex: Optional[Pattern] = None
    """
    If the preset's stdout/stderr matches this regex, it is marked as passing,
    regardless of the process exit code."
    """
    fail_regex: Optional[Pattern] = None
    """
    If the preset's stdout/stderr matches this regex, it is marked as failing,
    regardless of the process exit code."
    """
    skip_regex: Optional[Pattern] = None
    """
    If the preset's stdout/stderr matches this regex, it is marked as skipping,
    regardless of the process exit code."
    """
    depends: list[str] = field(default_factory=list)
    """
    List of presets that must execute before the current one. This field is
    ignored if in the global vendor field.
    (currently ignored)
    """
    fixtures_cleanup: Optional[Any] = None
    """ (currently ignored) """
    fixtures_required: Optional[Any] = None
    """ (currently ignored) """
    fixtures_setup: Optional[Any] = None
    """ (currently ignored) """
    required_files: list[Path] = field(default_factory=list)
    """
    list of files that must exist prior to the test running. If any of them are
    missing, the test is skipped. Does not currently support macro expansion.
    """
    run_serial: bool = False
    """Do not run the test in parallel (currently ignored)"""
    skip_return_code: Optional[int] = None
    """ The test is marked as skipped if this return code is detected """
    timeout: Optional[int] = None
    """
    The test is marked as a failure if it takes longer to run than the number
    of seconds specified
    """
