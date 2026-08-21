#!/usr/bin/env python3
"""Randomized tester for the custom auto-pricing form validator.

The tester deliberately does NOT use Pydantic to decide whether a test passed.
Pydantic/FastAPI are only the transport/parsing layer. A test is successful when
/submit returns the application's normal JSON response:

    {"status": "ok", "error": {}}
or
    {"status": "error", "error": {...}}

Random cases are generated from form_schema.json, then invalid cases are made by
mutating an otherwise-normal submission. Pydantic/server failures are treated as
tester failures, because those are not the custom validation errors we are trying
to exercise.

Every generated payload (normal + invalid, pass + fail) is written to a JSON file
under the log directory (default: logger/) so you can inspect exactly what was
sent and what came back, without re-running anything.
"""

from __future__ import annotations

import argparse
import json
import random
import string
import sys
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

try:
    from auto_pricing.main import app
    from auto_pricing.data import form_schema
except ImportError:
    from src.auto_pricing.main import app
    from src.auto_pricing.data import form_schema


ALWAYS_REQUIRED = {
    "modularAck",
    "contactName",
    "contactMethod",
    "contactPhone",
    "contactEmail",
    "deviceType",
    "deviceBrand",
    "deviceProduct",
    "serviceType",
}

ALWAYS_OPTIONAL = {"deviceModel", "deviceCondition"}

TEXT_VALUES = [
    "John Doe",
    "Jane Smith",
    "Alex Johnson",
    "Test User",
    "Zach Example",
    "Acme Repair",
    "Example Device",
]

BRANDS = ["Apple", "Samsung", "Lenovo", "Sony", "Nintendo", "Microsoft", "Dell", "Asus"]
PRODUCTS = [
    "iPhone 13",
    "Galaxy S24",
    "ThinkPad T14",
    "PlayStation 5",
    "Xbox Series X",
    "Nintendo Switch",
    "Steam Deck",
    "Surface Laptop",
]


def random_text(rng: random.Random) -> str:
    """Return ordinary text, with occasional arbitrary printable text."""
    if rng.random() < 0.85:
        return rng.choice(TEXT_VALUES)

    length = rng.randint(1, 30)
    alphabet = string.ascii_letters + string.digits + " -_."
    return "".join(rng.choice(alphabet) for _ in range(length)).strip() or "x"


def random_single(options: dict[str, str], rng: random.Random) -> str:
    return rng.choice(list(options))


def random_multi(options: dict[str, str], rng: random.Random) -> list[str]:
    keys = list(options)
    if not keys:
        return []

    # Empty lists are useful for optional fields, but required multi fields
    # need a real value to form a normal/valid submission.
    count = rng.randint(1, len(keys))
    return rng.sample(keys, count)


def make_field(field_id: str, schema: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    field_type = schema["type"]
    options = schema.get("options", {})
    required = field_id in ALWAYS_REQUIRED

    if field_id in ALWAYS_OPTIONAL:
        required = False
    elif field_id not in ALWAYS_REQUIRED:
        # The optional/non-core fields are normally left unanswered, but are
        # randomly answered sometimes so the tester covers both states.
        required = rng.random() < 0.35

    if field_type == "text":
        if required or rng.random() < 0.45:
            if field_id == "deviceBrand":
                value = rng.choice(BRANDS)
            elif field_id == "deviceProduct":
                value = rng.choice(PRODUCTS)
            else:
                value = random_text(rng)
        else:
            value = None

    elif field_type == "single":
        # FIX: previously this rolled a 35% chance to attach a value even
        # when required=False, which produced "normal" cases that violated
        # the validator's own "optional field cannot be answered" rule.
        # A normal case must always be internally consistent: no value
        # unless the field is required.
        value = random_single(options, rng) if required else None

    elif field_type == "multi":
        # FIX: same issue as above (used to be a 20% chance of a stray
        # value on optional fields). The deliberate "answered when
        # optional" case is already covered on purpose by the
        # "optional_answered" mutation in invalidate() below.
        value = random_multi(options, rng) if required else []

    else:
        raise RuntimeError(f"Unknown field type in form_schema.json: {field_type!r}")

    return {
        "question": schema["question"],
        "type": field_type,
        "value": value,
        "required": required,
    }


def make_valid_payload(rng: random.Random) -> dict[str, Any]:
    """Generate an ordinary submission without deliberately violating rules."""
    payload: dict[str, Any] = {}

    for field_id, schema in form_schema.items():
        field = make_field(field_id, schema, rng)

        # The two always-optional fields are explicitly optional in the schema.
        if field_id in ALWAYS_OPTIONAL:
            field["required"] = False
            if rng.random() < 0.55:
                field["value"] = None

        # An optional field marked required must have a value.
        if field["required"]:
            if field["type"] == "multi" and not field["value"]:
                field["value"] = random_multi(schema.get("options", {}), rng)
            elif field["type"] != "multi" and field["value"] is None:
                options = schema.get("options", {})
                field["value"] = random_single(options, rng) if field["type"] == "single" else random_text(rng)

        # For an optional field, None/[] is the safest normal state. If it has
        # a value, the required flag above is already True.
        payload[field_id] = field

    return payload


def invalidate(payload: dict[str, Any], rng: random.Random) -> tuple[str, str]:
    """Make exactly one deliberate custom-validation violation.

    Returns (mutation_name, field_id) so the test output explains what was tried.
    """
    mutations: list[str] = [
        "required_false",
        "required_empty",
        "optional_answered",
        "invalid_single",
        "invalid_multi",
    ]

    for _ in range(20):
        mutation = rng.choice(mutations)

        if mutation == "required_false":
            candidates = list(ALWAYS_REQUIRED)
            field_id = rng.choice(candidates)
            payload[field_id]["required"] = False
            if payload[field_id]["type"] == "multi":
                payload[field_id]["value"] = []
            else:
                payload[field_id]["value"] = None
            return mutation, field_id

        if mutation == "required_empty":
            # ALWAYS_OPTIONAL fields are skipped entirely by the validator
            # (see check_text/check_single/check_multi's early return), so
            # forcing required=True + empty value there can never produce
            # an "error" - same reasoning as the other mutations above.
            candidates = [f for f in form_schema if f not in ALWAYS_OPTIONAL]
            field_id = rng.choice(candidates)
            field = payload[field_id]
            field["required"] = True
            field["value"] = [] if field["type"] == "multi" else None
            return mutation, field_id

        if mutation == "optional_answered":
            # ALWAYS_OPTIONAL fields (deviceModel, deviceCondition) are
            # skipped entirely by the validator - answering them is never
            # invalid by design, so they can't be used to produce an
            # expected "error" case here.
            candidates = [
                f for f in form_schema
                if f not in ALWAYS_REQUIRED and f not in ALWAYS_OPTIONAL
            ]
            field_id = rng.choice(candidates)
            field = payload[field_id]
            field["required"] = False
            if field["type"] == "multi":
                options = form_schema[field_id].get("options", {})
                field["value"] = [next(iter(options))] if options else []
            elif field["type"] == "single":
                options = form_schema[field_id].get("options", {})
                field["value"] = next(iter(options)) if options else "unexpected"
            else:
                field["value"] = random_text(rng)
            return mutation, field_id

        if mutation == "invalid_single":
            # ALWAYS_OPTIONAL fields are skipped entirely by the validator
            # (see check_single's early return), so an invalid value there
            # can never produce an "error" - excluded for the same reason
            # as optional_answered above.
            candidates = [
                f for f, schema in form_schema.items()
                if schema["type"] == "single" and schema.get("options")
                and f not in ALWAYS_OPTIONAL
            ]
            field_id = rng.choice(candidates)
            payload[field_id]["required"] = True
            payload[field_id]["value"] = "__INVALID_RANDOM_VALUE__"
            return mutation, field_id

        if mutation == "invalid_multi":
            # Same reasoning as invalid_single above.
            candidates = [
                f for f, schema in form_schema.items()
                if schema["type"] == "multi" and schema.get("options")
                and f not in ALWAYS_OPTIONAL
            ]
            field_id = rng.choice(candidates)
            options = form_schema[field_id]["options"]
            payload[field_id]["required"] = True
            payload[field_id]["value"] = [rng.choice(list(options)), "__INVALID_RANDOM_VALUE__"]
            return mutation, field_id

    raise RuntimeError("Could not create an invalid test case")


def run_case(client: TestClient, payload: dict[str, Any], expected_status: str) -> tuple[bool, str, dict[str, Any] | None]:
    """Send one request and verify that the application returned custom JSON."""
    response = client.post("/submit", json=payload)

    if response.status_code != 200:
        return False, f"HTTP {response.status_code}: server/Pydantic failure", None

    try:
        data = response.json()
    except ValueError:
        return False, "Response was not JSON", None

    status = data.get("status")
    errors = data.get("error")

    if status not in {"ok", "error"} or not isinstance(errors, dict):
        return False, f"Malformed application response: {data!r}", data

    if status != expected_status:
        return False, f"Expected status={expected_status!r}, got {status!r}", data

    if expected_status == "error" and not errors:
        return False, "Validator reported error status but returned no custom errors", data

    if expected_status == "ok" and errors:
        return False, f"Validator reported ok but returned errors: {errors!r}", data

    return True, "", data


def next_run_dir(log_dir: str) -> Path:
    """Pick the next sequential 'run N' folder under log_dir (run 1, run 2, ...).

    Scans existing 'run N' subfolders and returns log_dir/run <max+1>, so each
    invocation of the script gets its own folder instead of piling files into
    a shared logger/ directory.
    """
    base = Path(log_dir)
    base.mkdir(parents=True, exist_ok=True)

    highest = 0
    for entry in base.iterdir():
        if not entry.is_dir():
            continue
        parts = entry.name.split(" ")
        if len(parts) == 2 and parts[0] == "run" and parts[1].isdigit():
            highest = max(highest, int(parts[1]))

    return base / f"run {highest + 1}"


def write_log(log_path: Path, index: int, ok: bool, kind: str, target: str,
              expected: str, reason: str, response: dict[str, Any] | None,
              payload: dict[str, Any]) -> str:
    """Write one generated test case (request + result) to its own JSON file.

    Returns the filename written, so the caller can print it alongside the
    pass/fail line.
    """
    status_tag = "PASS" if ok else "FAIL"
    filename = f"{index:04d}_{status_tag}_{kind}.json"

    record = {
        "index": index,
        "kind": kind,
        "field": target,
        "expected_status": expected,
        "passed": ok,
        "reason": reason,
        "response": response,
        "payload": payload,
    }

    with open(log_path / filename, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

    return filename


def run_tests(iterations: int, seed: int | None, valid_ratio: float,
              show_payload: bool, log_dir: str | None) -> int:
    rng = random.Random(seed)
    client = TestClient(app)

    log_path: Path | None = None
    if log_dir:
        log_path = next_run_dir(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

    print("--- Random custom-validator test suite ---")
    print(f"tests={iterations}  valid_ratio={valid_ratio:.2f}  seed={seed if seed is not None else 'random'}")
    if log_path:
        print(f"logging every generated case to: {log_path}")
    print()

    passed = 0
    valid_cases = 0
    invalid_cases = 0
    failures = 0

    for index in range(1, iterations + 1):
        payload = make_valid_payload(rng)

        if rng.random() < valid_ratio:
            kind = "normal"
            target = "-"
            expected = "ok"
            valid_cases += 1
        else:
            kind = "invalid"
            mutation, target = invalidate(payload, rng)
            expected = "error"
            kind = mutation
            invalid_cases += 1

        try:
            ok, reason, response = run_case(client, payload, expected)
        except Exception as exc:
            ok = False
            reason = f"Unexpected tester exception: {type(exc).__name__}: {exc}"
            response = None

        filename = None
        if log_path:
            filename = write_log(log_path, index, ok, kind, target, expected, reason, response, payload)

        name_tag = f" [{filename}]" if filename else ""

        if ok:
            passed += 1
            print(f"✅ {index:04d} {kind:<20} field={target}{name_tag}")
        else:
            failures += 1
            print(f"❌ {index:04d} {kind:<20} field={target}{name_tag} -> {reason}")
            if response is not None:
                print("   response:", json.dumps(response, ensure_ascii=False))
            if show_payload:
                print("   payload:")
                print(json.dumps(payload, indent=2, ensure_ascii=False))

    print()
    print("--- Summary ---")
    print(f"Passed:  {passed}/{iterations}")
    print(f"Failed:  {failures}/{iterations}")
    print(f"Normal:  {valid_cases}")
    print(f"Invalid: {invalid_cases}")

    if log_path:
        summary = {
            "tests": iterations,
            "seed": seed,
            "valid_ratio": valid_ratio,
            "passed": passed,
            "failed": failures,
            "normal_cases": valid_cases,
            "invalid_cases": invalid_cases,
        }
        with open(log_path / "_run_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

    if failures:
        print("\nFAIL: the application did not consistently return the expected custom validation response.")
        return 1

    print("\nPASS: every generated case stayed on the custom validation response path.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Randomized tester for the custom auto-pricing validator")
    parser.add_argument("-n", "--tests", type=int, default=100, help="number of random requests (default: 100)")
    parser.add_argument("--seed", type=int, default=None, help="random seed for reproducible failures")
    parser.add_argument(
        "--valid-ratio",
        type=float,
        default=0.35,
        help="fraction of requests that should be ordinary valid submissions (default: 0.35)",
    )
    parser.add_argument("--show-payload", action="store_true", help="print a failing JSON payload")
    parser.add_argument(
        "--log-dir",
        default="logger",
        help="directory to write every generated payload + response to, as JSON (default: logger)",
    )
    parser.add_argument("--no-log", action="store_true", help="skip writing JSON logs to disk")
    args = parser.parse_args()

    if args.tests <= 0:
        parser.error("--tests must be greater than zero")
    if not 0.0 <= args.valid_ratio <= 1.0:
        parser.error("--valid-ratio must be between 0.0 and 1.0")

    return run_tests(
        args.tests,
        args.seed,
        args.valid_ratio,
        args.show_payload,
        log_dir=None if args.no_log else args.log_dir,
    )


if __name__ == "__main__":
    sys.exit(main())