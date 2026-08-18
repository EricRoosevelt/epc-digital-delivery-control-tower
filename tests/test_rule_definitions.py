"""Rules as data, and the properties that makes possible.

The one worth stating first: **adding a rule touches no Python.** It is a new
TOML file in a directory. Before this, a rule was a module-level call in
``generate_ids.py`` plus an entry in a literal list of identifiers that the
same module asserted against itself, so adding one meant editing code in two
places and a fixture count in a third.

The rest of the file is about the metadata that had nowhere to live: severity,
which was a prefix match on the rule identifier, and the owner, stage,
discipline scope and citation, which simply did not exist.
"""

from __future__ import annotations

import shutil
import unittest

from epc_control_tower.domain import Severity
from epc_control_tower.rule_definitions import (
    FACET_KINDS,
    compile_document,
    load_rule_definitions,
)
from epc_control_tower.rules import load_ruleset
from helpers import PROJECT_ROOT, frozen_ruleset, writable_test_directory

RULES = PROJECT_ROOT / "rules" / "epc-delivery"


class DeclaredRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.definition = load_rule_definitions(RULES)
        _document, cls.ruleset, cls.expectations = compile_document(cls.definition)

    def test_one_file_per_rule(self):
        files = sorted(p.stem for p in RULES.glob("*.toml") if p.stem != "ruleset")
        self.assertEqual(files, [rule.rule_id for rule in self.definition.rules])

    def test_the_declared_rules_reproduce_the_frozen_keys(self):
        # The rule library must keep publishing the same requirements it
        # published before it was a library, or every downstream key moves.
        frozen = {r.requirement_key for r in frozen_ruleset().requirements}
        declared = {r.requirement_key for r in self.ruleset.requirements}
        self.assertEqual(frozen, declared)

    def test_the_wording_of_each_requirement_is_unchanged(self):
        from epc_control_tower.checkers.ids_checker import load_ids_rule_source

        was = load_ids_rule_source(
            PROJECT_ROOT / "ids" / "epc_delivery_requirements_v0.1.ids"
        ).expectations
        for key, text in was.items():
            with self.subTest(requirement=key):
                self.assertEqual(self.expectations[key], text)

    def test_severity_is_declared_not_derived_from_the_identifier(self):
        by_rule = {r.rule_id: r.severity for r in self.ruleset.requirements}
        self.assertIs(by_rule["R-005A"], Severity.WARNING)
        self.assertIs(by_rule["R-005B"], Severity.WARNING)
        self.assertIs(by_rule["R-001"], Severity.ERROR)

        # And the rule file says so in words, rather than a module inferring it
        # from the identifier's first five characters.
        text = (RULES / "R-005A.toml").read_text(encoding="utf-8")
        self.assertIn('severity = "WARNING"', text)
        self.assertNotIn("startswith", text)

    def test_every_rule_carries_the_metadata_a_requirement_actually_has(self):
        for requirement in self.ruleset.requirements:
            with self.subTest(rule=requirement.rule_id):
                self.assertTrue(requirement.owner_role)
                self.assertTrue(requirement.stage)
                self.assertTrue(requirement.discipline_scope)
                self.assertTrue(requirement.citation)

    def test_the_rule_set_loads_through_the_ordinary_loader(self):
        self.assertEqual(load_ruleset(RULES).ruleset_id, "epc-delivery")


class AddingARuleTests(unittest.TestCase):
    """The property the whole exercise is for."""

    def test_a_new_rule_is_one_file_and_no_code(self):
        with writable_test_directory("rule-add") as scratch:
            target = scratch / "epc-delivery"
            shutil.copytree(RULES, target)
            (target / "R-900.toml").write_text(
                'rule_id = "R-900"\n'
                'title = "Windows must declare IsExternal"\n'
                'description = "Added by a test, as one file and nothing else."\n'
                'checker = "ids"\n'
                'severity = "WARNING"\n'
                'owner_role = "architecture-lead"\n'
                'stage = "Design"\n'
                'discipline_scope = ["Architecture"]\n'
                'citation = "IFC4 Pset_WindowCommon."\n'
                "\n"
                "[[applicability]]\n"
                'facet = "entity"\n'
                'name = "IFCWINDOW"\n'
                "\n"
                "[[requirements]]\n"
                'facet = "property"\n'
                'propertySet = "Pset_WindowCommon"\n'
                'baseName = "IsExternal"\n'
                'dataType = "IFCBOOLEAN"\n'
                'cardinality = "required"\n'
                'instructions = "Declare whether the window is external."\n',
                encoding="utf-8",
            )

            widened = load_ruleset(target)

        self.assertEqual(len({r.rule_id for r in widened.requirements}), 8)
        added = [r for r in widened.requirements if r.rule_id == "R-900"]
        self.assertEqual(len(added), 1)
        self.assertIs(added[0].severity, Severity.WARNING)
        self.assertEqual(added[0].requirement_id, "Pset_WindowCommon.IsExternal")


class MalformedRuleTests(unittest.TestCase):
    """A rule that cannot mean what it says is rejected at load time."""

    def _rules_with(self, scratch, name: str, body: str):
        target = scratch / "epc-delivery"
        if not target.exists():
            shutil.copytree(RULES, target)
        (target / name).write_text(body, encoding="utf-8")
        return target

    def test_an_unknown_facet_kind_is_named(self):
        with writable_test_directory("rule-bad-facet") as scratch:
            target = self._rules_with(
                scratch,
                "R-901.toml",
                'rule_id = "R-901"\ntitle = "t"\n\n'
                '[[applicability]]\nfacet = "entity"\nname = "IFCWALL"\n\n'
                '[[requirements]]\nfacet = "telepathy"\nname = "Name"\n',
            )
            with self.assertRaisesRegex(ValueError, "telepathy"):
                load_rule_definitions(target)

    def test_an_unknown_severity_is_named(self):
        with writable_test_directory("rule-bad-severity") as scratch:
            target = self._rules_with(
                scratch,
                "R-902.toml",
                'rule_id = "R-902"\ntitle = "t"\nseverity = "CATASTROPHIC"\n\n'
                '[[applicability]]\nfacet = "entity"\nname = "IFCWALL"\n\n'
                '[[requirements]]\nfacet = "attribute"\nname = "Name"\n',
            )
            with self.assertRaisesRegex(ValueError, "CATASTROPHIC"):
                load_rule_definitions(target)

    def test_two_requirements_that_would_share_a_key_are_refused(self):
        # Both would label as Pset_X.Y, so both would derive the same
        # requirement_key and one would silently overwrite the other.
        with writable_test_directory("rule-dup-label") as scratch:
            target = self._rules_with(
                scratch,
                "R-903.toml",
                'rule_id = "R-903"\ntitle = "t"\n\n'
                '[[applicability]]\nfacet = "entity"\nname = "IFCWALL"\n\n'
                '[[requirements]]\nfacet = "property"\n'
                'propertySet = "Pset_X"\nbaseName = "Y"\n\n'
                '[[requirements]]\nfacet = "property"\n'
                'propertySet = "Pset_X"\nbaseName = "Y"\n',
            )
            with self.assertRaisesRegex(ValueError, "would share a key"):
                compile_document(load_rule_definitions(target))

    def test_every_facet_kind_ids_defines_is_accepted(self):
        self.assertEqual(
            sorted(FACET_KINDS),
            ["attribute", "classification", "entity", "material", "partof", "property"],
        )


if __name__ == "__main__":
    unittest.main()
