import unittest
from parameterized import parameterized
from utilis.dataclasses_user_story import (
    Persona, Action, Entity,
    Trigger, Target, Containment,
    UserStoryRecord, AtomicUserStoryRecord,
)
from relationship_analysers_classifier.crud_classifier.crud_actions import CrudAction


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _minimal_dict(**overrides) -> dict:
    """Return the smallest valid raw dict accepted by UserStoryRecord.factory_import."""
    base = {
        "PID": "G01",
        "Text": "As a user, I want to manage a profile.",
        "Benefit": "",
        "Persona": ["user"],
        "Action": {"Goal": ["manage"], "Benefit": []},
        "Entity": {"Goal": ["profile"], "Benefit": []},
        "Triggers": [["user", "manage"]],
        "Targets": [["manage", "profile"]],
        "Contains": [],
        "GoalActionCrud": "create",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Persona
# ---------------------------------------------------------------------------

class TestPersona(unittest.TestCase):

    def test_str(self):
        self.assertEqual(str(Persona("admin")), "admin")

    def test_equality(self):
        self.assertEqual(Persona("admin"), Persona("admin"))

    def test_inequality_different_name(self):
        self.assertNotEqual(Persona("admin"), Persona("user"))

    def test_inequality_different_type(self):
        self.assertNotEqual(Persona("admin"), "admin")

    def test_hash_equal_objects(self):
        self.assertEqual(hash(Persona("admin")), hash(Persona("admin")))

    def test_usable_in_set(self):
        s = {Persona("admin"), Persona("admin"), Persona("user")}
        self.assertEqual(len(s), 2)


# ---------------------------------------------------------------------------
# Action
# ---------------------------------------------------------------------------

class TestAction(unittest.TestCase):

    def test_str(self):
        self.assertEqual(str(Action("delete")), "delete")

    def test_equality(self):
        self.assertEqual(Action("delete"), Action("delete"))

    def test_inequality(self):
        self.assertNotEqual(Action("delete"), Action("create"))

    def test_inequality_different_type(self):
        self.assertNotEqual(Action("delete"), "delete")

    def test_hash_equal_objects(self):
        self.assertEqual(hash(Action("delete")), hash(Action("delete")))

    def test_usable_in_set(self):
        s = {Action("delete"), Action("delete"), Action("create")}
        self.assertEqual(len(s), 2)


# ---------------------------------------------------------------------------
# Entity
# ---------------------------------------------------------------------------

class TestEntity(unittest.TestCase):

    def test_str(self):
        self.assertEqual(str(Entity("profile")), "profile")

    def test_equality(self):
        self.assertEqual(Entity("profile"), Entity("profile"))

    def test_inequality(self):
        self.assertNotEqual(Entity("profile"), Entity("account"))

    def test_inequality_different_type(self):
        self.assertNotEqual(Entity("profile"), "profile")

    def test_hash_equal_objects(self):
        self.assertEqual(hash(Entity("profile")), hash(Entity("profile")))

    def test_usable_in_set(self):
        s = {Entity("profile"), Entity("profile"), Entity("account")}
        self.assertEqual(len(s), 2)


# ---------------------------------------------------------------------------
# Trigger / Target / Containment
# ---------------------------------------------------------------------------

class TestTrigger(unittest.TestCase):

    def test_str(self):
        t = Trigger(src=Persona("user"), trg=Action("delete"))
        self.assertEqual(str(t), "user -> delete")

    def test_equality(self):
        t1 = Trigger(Persona("user"), Action("delete"))
        t2 = Trigger(Persona("user"), Action("delete"))
        self.assertEqual(t1, t2)

    def test_inequality(self):
        self.assertNotEqual(
            Trigger(Persona("user"), Action("delete")),
            Trigger(Persona("admin"), Action("delete")),
        )

    def test_inequality_different_type(self):
        self.assertNotEqual(Trigger(Persona("user"), Action("delete")), "user -> delete")


class TestTarget(unittest.TestCase):

    def test_str(self):
        t = Target(src=Action("manage"), trg=Entity("profile"))
        self.assertEqual(str(t), "manage -> profile")

    def test_equality(self):
        t1 = Target(Action("manage"), Entity("profile"))
        t2 = Target(Action("manage"), Entity("profile"))
        self.assertEqual(t1, t2)

    def test_inequality(self):
        self.assertNotEqual(
            Target(Action("manage"), Entity("profile")),
            Target(Action("delete"), Entity("profile")),
        )

    def test_inequality_different_type(self):
        self.assertNotEqual(Target(Action("manage"), Entity("profile")), "manage -> profile")


class TestContainment(unittest.TestCase):

    def test_str(self):
        c = Containment(src=Entity("user"), trg=Entity("profile"))
        self.assertEqual(str(c), "user -> profile")

    def test_equality(self):
        c1 = Containment(Entity("user"), Entity("profile"))
        c2 = Containment(Entity("user"), Entity("profile"))
        self.assertEqual(c1, c2)

    def test_inequality(self):
        self.assertNotEqual(
            Containment(Entity("user"), Entity("profile")),
            Containment(Entity("user"), Entity("account")),
        )

    def test_inequality_different_type(self):
        self.assertNotEqual(Containment(Entity("a"), Entity("b")), "a -> b")


# ---------------------------------------------------------------------------
# UserStoryRecord.factory_import
# ---------------------------------------------------------------------------

class TestUserStoryRecordFactoryImport(unittest.TestCase):

    def test_basic_fields_parsed(self):
        record = UserStoryRecord.factory_import(_minimal_dict())
        self.assertEqual(record.pid, "G01")
        self.assertIn("manage", record.story)
        self.assertEqual(record.benefit, "")

    def test_pid_stripped_from_story(self):
        d = _minimal_dict(Text="#G01# As a user, I want to manage a profile.")
        record = UserStoryRecord.factory_import(d)
        self.assertNotIn("#G01#", record.story)

    def test_goal_extracted(self):
        d = _minimal_dict(
            Text="As a user, I want to manage a profile, so that I can stay organised.",
            Benefit="I can stay organised.",
        )
        record = UserStoryRecord.factory_import(d)
        self.assertIn("manage", record.goal)
        self.assertNotIn("so that", record.goal)

    def test_personas_parsed(self):
        record = UserStoryRecord.factory_import(_minimal_dict())
        self.assertEqual(len(record.personas), 1)
        self.assertEqual(record.personas[0].named_element, "user")

    def test_goal_actions_parsed(self):
        record = UserStoryRecord.factory_import(_minimal_dict())
        self.assertEqual(len(record.goal_actions), 1)
        self.assertEqual(record.goal_actions[0].named_element, "manage")

    def test_goal_entities_parsed(self):
        record = UserStoryRecord.factory_import(_minimal_dict())
        self.assertEqual(len(record.goal_entities), 1)
        self.assertEqual(record.goal_entities[0].named_element, "profile")

    def test_triggers_parsed(self):
        record = UserStoryRecord.factory_import(_minimal_dict())
        self.assertEqual(len(record.triggers), 1)
        self.assertEqual(record.triggers[0].src.named_element, "user")
        self.assertEqual(record.triggers[0].trg.named_element, "manage")

    def test_goal_targets_parsed(self):
        record = UserStoryRecord.factory_import(_minimal_dict())
        self.assertEqual(len(record.goal_targets), 1)
        self.assertEqual(record.goal_targets[0].src.named_element, "manage")
        self.assertEqual(record.goal_targets[0].trg.named_element, "profile")

    def test_crud_action_parsed(self):
        record = UserStoryRecord.factory_import(_minimal_dict())
        self.assertEqual(record.goal_action_crud, CrudAction.CREATE)

    def test_unknown_crud_on_missing_key(self):
        d = _minimal_dict()
        del d["GoalActionCrud"]
        record = UserStoryRecord.factory_import(d)
        self.assertEqual(record.goal_action_crud, CrudAction.UNKNOWN)

    def test_benefit_actions_and_entities_parsed(self):
        d = _minimal_dict(
            **{
                "Action": {"Goal": ["manage"], "Benefit": ["notify"]},
                "Entity": {"Goal": ["profile"], "Benefit": ["user"]},
                "Targets": [["manage", "profile"], ["notify", "user"]],
                "Benefit": "notify user",
            }
        )
        record = UserStoryRecord.factory_import(d)
        self.assertEqual(len(record.benefit_actions), 1)
        self.assertEqual(record.benefit_actions[0].named_element, "notify")
        self.assertEqual(len(record.benefit_entities), 1)
        self.assertEqual(record.benefit_entities[0].named_element, "user")

    def test_containment_parsed(self):
        d = _minimal_dict(
            **{
                "Entity": {"Goal": ["user", "profile"], "Benefit": []},
                "Contains": [["user", "profile"]],
            }
        )
        record = UserStoryRecord.factory_import(d)
        self.assertEqual(len(record.goal_contains), 1)
        self.assertEqual(record.goal_contains[0].src.named_element, "user")
        self.assertEqual(record.goal_contains[0].trg.named_element, "profile")

    def test_malformed_trigger_skipped(self):
        d = _minimal_dict(Triggers=[["user"], ["user", "manage"]])
        record = UserStoryRecord.factory_import(d)
        self.assertEqual(len(record.triggers), 1)

    def test_malformed_target_skipped(self):
        d = _minimal_dict(Targets=[["manage"], ["manage", "profile"]])
        record = UserStoryRecord.factory_import(d)
        self.assertEqual(len(record.goal_targets), 1)

    def test_empty_input_returns_defaults(self):
        record = UserStoryRecord.factory_import({})
        self.assertEqual(record.pid, "")
        self.assertEqual(record.personas, [])
        self.assertEqual(record.goal_actions, [])
        self.assertEqual(record.goal_action_crud, CrudAction.UNKNOWN)

    def test_action_objects_reused_across_goal_and_benefit(self):
        """An action appearing in both goal and benefit must be the same object."""
        d = _minimal_dict(
            **{
                "Action": {"Goal": ["manage"], "Benefit": ["manage"]},
                "Entity": {"Goal": ["profile"], "Benefit": ["account"]},
                "Targets": [["manage", "profile"], ["manage", "account"]],
            }
        )
        record = UserStoryRecord.factory_import(d)
        self.assertIs(record.goal_actions[0], record.benefit_actions[0])


# ---------------------------------------------------------------------------
# AtomicUserStoryRecord.factory_import
# ---------------------------------------------------------------------------

class TestAtomicUserStoryRecordFactoryImport(unittest.TestCase):

    def _make_us_record(self, **overrides) -> UserStoryRecord:
        return UserStoryRecord.factory_import(_minimal_dict(**overrides))

    def test_factory_import_single(self):
        us = self._make_us_record()
        atomic = AtomicUserStoryRecord.factory_import(us)
        self.assertIsInstance(atomic, AtomicUserStoryRecord)
        self.assertEqual(atomic.pid, us.pid)
        self.assertEqual(atomic.persona.named_element, "user")
        self.assertEqual(atomic.goal_action.named_element, "manage")
        self.assertEqual(atomic.goal_target.src.named_element, "manage")
        self.assertEqual(atomic.goal_target.trg.named_element, "profile")

    def test_factory_import_defaults_on_empty_lists(self):
        us = UserStoryRecord()  # all lists empty
        atomic = AtomicUserStoryRecord.factory_import(us)
        self.assertEqual(atomic.persona, Persona())
        self.assertEqual(atomic.goal_action, Action())
        self.assertEqual(atomic.goal_target, Target())

    def test_factory_bulk_import(self):
        us_records = [self._make_us_record() for _ in range(3)]
        atomics = AtomicUserStoryRecord.factory_bulk_import(us_records)
        self.assertEqual(len(atomics), 3)
        for a in atomics:
            self.assertIsInstance(a, AtomicUserStoryRecord)

    def test_factory_direct_import(self):
        atomic = AtomicUserStoryRecord.factory_direct_import(_minimal_dict())
        self.assertIsInstance(atomic, AtomicUserStoryRecord)
        self.assertEqual(atomic.pid, "G01")
        self.assertEqual(atomic.goal_action.named_element, "manage")

    def test_factory_bulk_direct_import(self):
        data = [_minimal_dict(), _minimal_dict(PID="G02")]
        atomics = AtomicUserStoryRecord.factory_bulk_direct_import(data)
        self.assertEqual(len(atomics), 2)
        pids = {a.pid for a in atomics}
        self.assertIn("G01", pids)
        self.assertIn("G02", pids)

    def test_crud_action_propagated(self):
        atomic = AtomicUserStoryRecord.factory_direct_import(_minimal_dict())
        self.assertEqual(atomic.goal_action_crud, CrudAction.CREATE)