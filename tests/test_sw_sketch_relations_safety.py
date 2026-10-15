"""Verify relation dispatch does not replay a possibly executed mutation."""
# Source: this repository, scripts/sw_sketch_relations.py existing calling contract.
# Location: specs/next-feature relation replay safety, offline regression tests.
# Official reference: C:/swapi/types/ISketchRelationManager/AddRelation.md,
# C:/swapi/types/ISketchSegment/GetRelationsCount.md (signature and readback only).
# License: repository MIT; no third-party implementation copied.
# Coverage: fake-host dispatch, preconditions, uncertain execution and compatibility.
from __future__ import annotations

import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "relation_safety_under_test", ROOT / "scripts" / "sw_sketch_relations.py"
)
RELATIONS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RELATIONS)


class Segment:
    def __init__(self):
        self.count = 0
        self.readable = True
        self.selectable = True

    def GetRelationsCount(self):
        if not self.readable:
            raise RuntimeError("readback unavailable")
        return self.count

    def Select4(self, append, callout):
        return self.selectable


class Manager:
    def __init__(self, segments, behavior="success"):
        self.segments = segments
        self.behavior = behavior
        self.calls = []
        self.alternate_calls = 0

    def AddRelation(self, entities, relation_type):
        self.calls.append((entities, relation_type))
        if self.behavior in ("success", "mutate_raise"):
            for seg in entities:
                seg.count += 1
        if self.behavior in ("raise", "mutate_raise"):
            raise RuntimeError("server fault after dispatch")
        if self.behavior == "lose_readback":
            for seg in entities:
                seg.readable = False
        return True

    def IAddRelation(self, *args):
        self.alternate_calls += 1
        return self.AddRelation(*args)


class Sketch:
    def __init__(self, segments, manager, status=2):
        self.GetSketchSegments = segments
        self.RelationManager = manager
        self.status = status

    def GetConstrainedStatus(self):
        return self.status


class Model:
    def __init__(self, behavior="success", manager=True, status=2):
        self.segments = [Segment(), Segment()]
        self.manager = Manager(self.segments, behavior) if manager else None
        self.sketch = Sketch(self.segments, self.manager, status)
        self.fallback_calls = 0
        self.cleanup_calls = 0
        self.fallback_behavior = behavior

    def ClearSelection2(self, all_selected):
        self.cleanup_calls += 1

    def SketchAddConstraints(self, name):
        self.fallback_calls += 1
        if self.fallback_behavior in ("success", "mutate_raise"):
            for seg in self.segments:
                seg.count += 1
        if self.fallback_behavior in ("raise", "mutate_raise"):
            raise RuntimeError("fallback fault after dispatch")
        return True


def run(model, relations=None, verify=True):
    part = types.ModuleType("sw_part")

    def get_com_member(obj, name, *args):
        value = getattr(obj, name)
        return value(*args) if callable(value) else value

    part.get_com_member = get_com_member
    part._empty_callout = lambda: None
    sketch = types.ModuleType("sw_sketch")
    sketch.active_sketch = lambda obj: obj.sketch
    request = relations if relations is not None else [{"type": "PARALLEL", "targets": [0, 1]}]
    array_module = types.ModuleType("sketch_relations")
    # Dispatch wrapper is a seam: these tests do not certify actual COM SAFEARRAYs.
    array_module._dispatch_array = lambda entities: entities
    with patch.dict(sys.modules, {"sw_part": part, "sw_sketch": sketch,
                                 "sketch_relations": array_module}):
        with contextlib.redirect_stdout(io.StringIO()):
            return RELATIONS.apply_sketch_relations(model, relations=request, verify=verify)


class RelationSafetyTests(unittest.TestCase):
    def test_success_retains_existing_keys_and_one_dispatch(self):
        model = Model()
        result = run(model)
        self.assertTrue(result["ok"])
        self.assertEqual(result["applied"], 1)
        self.assertEqual(result["total"], 1)
        self.assertEqual(len(model.manager.calls), 1)
        self.assertEqual(model.manager.alternate_calls, 0)
        self.assertEqual(model.fallback_calls, 0)
        self.assertEqual(result["results"][0]["relations_count"], [0, 1])
        self.assertEqual(result["results"][0]["relation_count_status"], "pass")
        self.assertEqual(result["results"][0]["effect_status"], "unknown")

    def test_true_without_effect_is_not_replayed_or_fallback(self):
        model = Model("no_effect")
        result = run(model)
        self.assertFalse(result["ok"])
        self.assertEqual(len(model.manager.calls), 1)
        self.assertEqual(model.manager.alternate_calls, 0)
        self.assertEqual(model.fallback_calls, 0)
        self.assertFalse(result["results"][0]["applied"])

    def test_exception_stops_batch_without_replay(self):
        model = Model("raise")
        result = run(model, ["PARALLEL:0,1", "EQUAL:0,1"])
        self.assertEqual(len(model.manager.calls), 1)
        self.assertEqual(model.fallback_calls, 0)
        self.assertEqual(result["execution_state"], "uncertain")
        self.assertEqual(result["results"][0]["execution_state"], "uncertain")
        self.assertEqual(result["results"][1]["execution_state"], "not_started")
        self.assertEqual(result["total"], 2)

    def test_mutation_before_exception_is_not_replayed(self):
        model = Model("mutate_raise")
        result = run(model)
        self.assertEqual(len(model.manager.calls), 1)
        self.assertEqual(model.segments[0].count, 1)
        self.assertEqual(model.fallback_calls, 0)
        self.assertFalse(result["ok"])
        self.assertEqual(result["execution_state"], "uncertain")
        self.assertEqual(result["results"][0]["relations_count"], [0, 1])

    def test_unavailable_post_readback_stops_remaining_work(self):
        model = Model("lose_readback")
        result = run(model, ["PARALLEL:0,1", "EQUAL:0,1"])
        self.assertEqual(len(model.manager.calls), 1)
        self.assertEqual(model.fallback_calls, 0)
        self.assertEqual(result["execution_state"], "uncertain")
        self.assertFalse(result["results"][0]["applied"])
        self.assertEqual(result["results"][1]["execution_state"], "not_started")

    def test_unavailable_pre_readback_rejects_before_mutation(self):
        model = Model()
        model.segments[0].readable = False
        result = run(model)
        self.assertEqual(len(model.manager.calls), 0)
        self.assertEqual(model.fallback_calls, 0)
        self.assertFalse(result["ok"])

    def test_incomplete_selection_rejects_before_mutation(self):
        model = Model()
        model.segments[1].selectable = False
        result = run(model)
        self.assertEqual(len(model.manager.calls), 0)
        self.assertEqual(model.fallback_calls, 0)
        self.assertFalse(result["ok"])

    def test_verify_false_does_not_bypass_sketch_status(self):
        model = Model(status=4)
        result = run(model, verify=False)
        self.assertEqual(len(model.manager.calls), 0)
        self.assertEqual(model.fallback_calls, 0)
        self.assertFalse(result["ok"])

    def test_absent_manager_selects_fallback_once_before_dispatch(self):
        model = Model(manager=False)
        result = run(model)
        self.assertEqual(model.fallback_calls, 1)
        self.assertTrue(result["ok"])
        self.assertEqual(result["results"][0]["via"], "SketchAddConstraints")

    def test_fallback_exception_is_uncertain_and_stops_batch(self):
        model = Model("mutate_raise", manager=False)
        result = run(model, ["PARALLEL:0,1", "EQUAL:0,1"])
        self.assertEqual(model.fallback_calls, 1)
        self.assertEqual(model.segments[0].count, 1)
        self.assertEqual(result["execution_state"], "uncertain")

    def test_noncallable_manager_member_uses_predispatch_fallback(self):
        model = Model()
        model.manager.AddRelation = None
        result = run(model)
        self.assertEqual(model.manager.alternate_calls, 0)
        self.assertEqual(model.fallback_calls, 1)
        self.assertTrue(result["ok"])

    def test_invalid_relation_preserves_error_and_no_mutation(self):
        model = Model()
        result = run(model, ["UNKNOWN:0,1"])
        self.assertFalse(result["ok"])
        self.assertEqual(len(model.manager.calls), 0)
        self.assertEqual(model.fallback_calls, 0)


if __name__ == "__main__":
    unittest.main()
