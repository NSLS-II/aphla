#!/usr/bin/env python3
"""Verify live C29 EPU aphla fields without printing PV values.

Run manually against live EPICS only. This script is intentionally named so it
is not collected by the repository's default pytest invocation.
"""

import argparse

import aphla as ap


def has_phy_unitsys(element, field, handle):
    """Return whether the field/handle exposes a physical unit system."""
    try:
        return "phy" in element.getUnitSystems(field, handle)
    except Exception:
        return False


def verify_element(element, exclude_csff):
    """Return success, skipped, and failure records for one live EPU."""
    successes = 0
    skipped_csff = 0
    skipped_no_phy = 0
    failures = []

    for field in element.fields():
        if exclude_csff and field.startswith("csff"):
            skipped_csff += 1
            continue

        action = element._field[field]
        for handle, pv_attr in (("readback", "pvrb"),
                                ("setpoint", "pvsp")):
            if not getattr(action, pv_attr, None):
                continue

            unit_systems = [None]
            if has_phy_unitsys(element, field, handle):
                unit_systems.append("phy")
            else:
                skipped_no_phy += 1

            for unitsys in unit_systems:
                try:
                    value = element.get(field, handle=handle, unitsys=unitsys)
                    if type(value).__name__ == "ca_nothing":
                        raise RuntimeError("Channel Access returned ca_nothing")
                    successes += 1
                except Exception as exc:
                    failures.append(
                        (field, handle, unitsys, type(exc).__name__, str(exc)))

    return successes, skipped_csff, skipped_no_phy, failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--exclude-csff",
        action="store_true",
        help="skip offline current-strip feedforward channels",
    )
    args = parser.parse_args()

    ap.machines.load("nsls2", "SR")
    sxn, ari = ap.getElements("epu*c29*")
    expected_names = ("epu50g1c29u", "epu70g1c29d")
    if (sxn.name, ari.name) != expected_names:
        raise RuntimeError(
            f"expected {expected_names}, got {(sxn.name, ari.name)}")

    total_successes = 0
    total_skipped_csff = 0
    total_skipped_no_phy = 0
    total_failures = []
    for element in (sxn, ari):
        successes, skipped_csff, skipped_no_phy, failures = verify_element(
            element, args.exclude_csff)
        total_successes += successes
        total_skipped_csff += skipped_csff
        total_skipped_no_phy += skipped_no_phy
        total_failures.extend((element.name, *failure) for failure in failures)
        print(f"{element.name}: {successes} passed, "
              f"{skipped_csff} csff skipped, "
              f"{skipped_no_phy} no-phy skipped, {len(failures)} failed")

    for element, field, handle, unitsys, exc_type, message in total_failures:
        print(f"FAIL {element} {field} {handle} {unitsys!r}: "
              f"{exc_type}: {message}")

    print(f"Total: {total_successes} passed, "
          f"{total_skipped_csff} csff skipped, "
          f"{total_skipped_no_phy} no-phy skipped, "
          f"{len(total_failures)} failed")
    return 1 if total_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
