"""Abwärtskompatibilität: startet Trashcan."""

from trashcan import main


if __name__ == "__main__":
    raise SystemExit(main())