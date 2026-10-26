"""Load the single, explicit configuration file without silent fallbacks."""

from dataclasses import dataclass
import math
import os
from pathlib import Path
from types import MappingProxyType
from typing import Mapping
import tomllib
from urllib.parse import urlsplit


class ConfigError(ValueError):
    """Configuration is absent, malformed, or unsafe to use."""


DEFAULTS = {
    "paths": {"state": "state", "playbook": "playbook"},
    "model": {
        "host": "http://127.0.0.1:11434", "name": "qwen3.8:27b",
        "num_ctx": 65536, "temperature": 0.1, "timeout_s": 600,
    },
    "ocr": {"tesseract": "tesseract", "ocrmypdf": "ocrmypdf"},
}
KNOWN_KEYS = MappingProxyType({
    "paths": ("matters", "state", "playbook"),
    "model": ("host", "name", "num_ctx", "temperature", "timeout_s"),
    "ocr": ("tesseract", "ocrmypdf"),
})


@dataclass(frozen=True)
class Paths:
    matters: Path
    state: Path
    playbook: Path


@dataclass(frozen=True)
class Model:
    host: str
    name: str
    num_ctx: int
    temperature: float
    timeout_s: int


@dataclass(frozen=True)
class OCR:
    tesseract: str
    ocrmypdf: str


@dataclass(frozen=True)
class Config:
    paths: Paths
    model: Model
    ocr: OCR
    source: Path
    sources: Mapping[str, str]


def load(path: str | Path | None = None) -> Config:
    source = Path(path if path is not None else os.environ.get("CASEFILE_CONFIG", "config.toml"))
    source = source.expanduser().resolve()
    try:
        with source.open("rb") as stream:
            data = tomllib.load(stream)
    except FileNotFoundError as exc:
        raise ConfigError(f"no config file at {source}; copy config.example.toml to config.toml") from exc
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"cannot load config at {source}: {exc}") from exc

    # Validate before merging: a typo must never turn into a default.
    for table, entries in data.items():
        if table not in KNOWN_KEYS:
            raise ConfigError(f"unknown key [{table}]; known: {', '.join(KNOWN_KEYS)}")
        if not isinstance(entries, dict):
            raise ConfigError(f"[{table}]: expected table, got {type(entries).__name__}")
        for key in entries:
            if key not in KNOWN_KEYS[table]:
                raise ConfigError(f"unknown key [{table}].{key}; known: {', '.join(KNOWN_KEYS[table])}")
    if "matters" not in data.get("paths", {}):
        raise ConfigError("[paths].matters is required")

    values, sources = {}, {}
    for table, keys in KNOWN_KEYS.items():
        values[table] = {}
        for key in keys:
            supplied = key in data.get(table, {})
            value = data[table][key] if supplied else DEFAULTS[table][key]
            label = f"[{table}].{key}"
            expected = int if key in ("num_ctx", "timeout_s") else float if key == "temperature" else str
            valid = type(value) is expected
            if expected is float:
                valid = type(value) in (int, float)
            if not valid:
                raise ConfigError(f"{label}: expected {expected.__name__}, got {type(value).__name__}")
            if isinstance(value, str) and not value.strip():
                raise ConfigError(f"{label} must be non-empty")
            values[table][key] = value
            sources[f"{table}.{key}"] = "file" if supplied else "default"

    model = values["model"]
    if model["num_ctx"] < 65536:
        raise ConfigError("[model].num_ctx must be at least 65536")
    if model["timeout_s"] <= 0:
        raise ConfigError("[model].timeout_s must be positive")
    if not math.isfinite(model["temperature"]) or not 0 <= model["temperature"] <= 2:
        raise ConfigError("[model].temperature must be finite and between 0 and 2")
    try:
        host = urlsplit(model["host"])
        port = host.port
        safe = (host.scheme == "http" and host.hostname == "127.0.0.1"
                and host.username is None and host.password is None
                and host.path in ("", "/") and not host.query and not host.fragment
                and (port is None or port > 0))
    except ValueError:
        safe = False
    if not safe:
        raise ConfigError("[model].host must use http with hostname 127.0.0.1")

    paths = values["paths"]
    matters = Path(paths["matters"]).expanduser()
    checkout = Path(__file__).resolve().parents[2]
    if not matters.is_absolute():
        raise ConfigError("[paths].matters must be an absolute path")
    try:
        inside = matters.resolve().is_relative_to(checkout) or any(
            ancestor.exists() and os.path.samefile(ancestor, checkout)
            for ancestor in (matters, *matters.parents)
        )
    except OSError as exc:
        raise ConfigError(f"cannot verify [paths].matters is outside the checkout: {exc}") from exc
    if inside:
        raise ConfigError(f"[paths].matters must be outside the checkout {checkout}")
    paths["matters"] = matters.resolve()
    for key in ("state", "playbook"):
        paths[key] = (source.parent / Path(paths[key]).expanduser()).resolve()
    return Config(Paths(**paths), Model(**model), OCR(**values["ocr"]), source,
                  MappingProxyType(sources))
