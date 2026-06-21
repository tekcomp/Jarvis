# core/spec/spec_loader.py

from core.spec.spec_v1 import SpecV1

CURRENT_SPEC = SpecV1()


def get_spec():
    return CURRENT_SPEC