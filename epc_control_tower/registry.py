"""Explicit registration of checkers, grouping policies, and exporters.

Registration is in-tree and by hand. That is a deliberate stopping point: a
dynamic entry-point mechanism is a promise to third-party packages about names,
versions, and compatibility, and making that promise before anything outside
this repository depends on it would fix the wrong details. A fork adds its
implementation to :func:`default_registry` and moves on; when external plugins
actually exist, this is the one module that has to change.

Routing happens here too. Each :class:`~.domain.Requirement` names the checker
that evaluates it, and unknown or unsuitable names are rejected while planning
rather than part-way through a run.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

from .config import RunConfig
from .domain import ComponentFingerprint, Model, Requirement
from .protocols import Checker, Exporter, GroupingPolicy

__all__ = ["Registry", "default_registry"]


@dataclass
class Registry:
    checkers: dict[str, Checker] = field(default_factory=dict)
    grouping_policies: dict[str, GroupingPolicy] = field(default_factory=dict)
    exporters: dict[str, Exporter] = field(default_factory=dict)

    # -- registration ------------------------------------------------------

    def register_checker(self, checker: Checker) -> None:
        if checker.id in self.checkers:
            raise ValueError(f"Checker already registered: {checker.id}")
        self.checkers[checker.id] = checker

    def register_grouping_policy(self, policy: GroupingPolicy) -> None:
        if policy.id in self.grouping_policies:
            raise ValueError(f"Grouping policy already registered: {policy.id}")
        self.grouping_policies[policy.id] = policy

    def register_exporter(self, exporter: Exporter) -> None:
        if exporter.id in self.exporters:
            raise ValueError(f"Exporter already registered: {exporter.id}")
        self.exporters[exporter.id] = exporter

    # -- lookup ------------------------------------------------------------

    def checker(self, checker_id: str) -> Checker:
        try:
            return self.checkers[checker_id]
        except KeyError:
            raise KeyError(
                f"Unknown checker {checker_id!r}; registered: {sorted(self.checkers)}"
            ) from None

    def grouping_policy(self, policy_id: str) -> GroupingPolicy:
        try:
            return self.grouping_policies[policy_id]
        except KeyError:
            raise KeyError(
                f"Unknown grouping policy {policy_id!r}; "
                f"registered: {sorted(self.grouping_policies)}"
            ) from None

    def exporter(self, exporter_id: str) -> Exporter:
        try:
            return self.exporters[exporter_id]
        except KeyError:
            raise KeyError(
                f"Unknown exporter {exporter_id!r}; registered: {sorted(self.exporters)}"
            ) from None

    # -- routing -----------------------------------------------------------

    def route(
        self,
        requirements: Sequence[Requirement],
    ) -> dict[str, tuple[Requirement, ...]]:
        """Group requirements by the checker that will evaluate them.

        Raises on an unregistered checker id, so a typo in a rule definition is
        caught before any model is opened.
        """

        routed: dict[str, list[Requirement]] = {}
        for requirement in requirements:
            self.checker(requirement.checker)
            routed.setdefault(requirement.checker, []).append(requirement)
        return {
            checker_id: tuple(items) for checker_id, items in sorted(routed.items())
        }

    def validate_plan(
        self,
        routed: dict[str, tuple[Requirement, ...]],
        models: Iterable[Model],
    ) -> None:
        """Reject a plan its checkers cannot actually carry out.

        Both checks run before any model is opened, so a rule routed to the
        wrong checker — or a checker that does not speak the schema in front of
        it — fails with a clear message rather than an obscure one from deep
        inside a validation.

        A checker that declares no capability of a given kind is treated as
        making no claim, and is not second-guessed.
        """

        schemas = sorted({model.ifc_schema for model in models})
        for checker_id, requirements in routed.items():
            capabilities = self.checker(checker_id).capabilities

            if capabilities.ifc_schemas:
                unsupported = [
                    schema for schema in schemas if schema not in capabilities.ifc_schemas
                ]
                if unsupported:
                    raise ValueError(
                        f"Checker {checker_id!r} does not support IFC schema(s) "
                        f"{unsupported}; it supports {list(capabilities.ifc_schemas)}"
                    )

            if capabilities.facets:
                for requirement in requirements:
                    unsupported = [
                        facet
                        for facet in requirement.facet_kinds
                        if facet not in capabilities.facets
                    ]
                    if unsupported:
                        raise ValueError(
                            f"Requirement {requirement.rule_id!r} needs facet(s) "
                            f"{unsupported}, which checker {checker_id!r} does not "
                            f"evaluate; it handles {list(capabilities.facets)}"
                        )

    def fingerprints(self, checker_ids: Iterable[str]) -> tuple[ComponentFingerprint, ...]:
        """Fingerprint the given checkers for the validation identity."""

        return tuple(
            ComponentFingerprint(
                component_id=checker.id,
                version=checker.version,
                config_sha256=checker.config_sha256(),
            )
            for checker in (self.checker(checker_id) for checker_id in sorted(checker_ids))
        )

    def grouping_fingerprint(self, policy_id: str) -> ComponentFingerprint:
        """Fingerprint the grouping policy for the artifact bundle identity.

        The grouping choice shapes issues and therefore every exported byte, so
        its id, version and configuration belong in the artifact identity the
        same way a checker's belong in the validation identity.
        """

        policy = self.grouping_policy(policy_id)
        return ComponentFingerprint(
            component_id=policy.id,
            version=policy.version,
            config_sha256=policy.config_sha256(),
        )

    def exporter_fingerprints(
        self, exporter_ids: Iterable[str]
    ) -> tuple[ComponentFingerprint, ...]:
        """Fingerprint the given exporters for the artifact bundle identity."""

        return tuple(
            ComponentFingerprint(
                component_id=exporter.id,
                version=exporter.version,
                config_sha256=exporter.config_sha256(),
            )
            for exporter in (
                self.exporter(exporter_id) for exporter_id in sorted(exporter_ids)
            )
        )


def default_registry(config: RunConfig) -> Registry:
    """Build a registry with everything this package ships.

    Imports are local to keep module import order simple: implementations
    import the protocols, and the registry imports the implementations.

    Components are constructed here, configured from the run configuration, and
    they do their own lazy loading — building a registry opens no files, so
    listing what is available costs nothing and cannot fail on a missing
    fixture.

    This is the one place a fork adds its own checker, policy, or exporter.
    """

    from .bcf.schema import default_schema_dir
    from .checkers.completeness import CompletenessChecker
    from .checkers.ids_checker import IdsChecker
    from .exporters.bcf import BcfExporter
    from .exporters.canonical import CsvExporter, JsonExporter
    from .exporters.legacy_bcf import LegacyBcfExporter
    from .exporters.legacy_pbip import LegacyPbipAdapter
    from .exporters.legacy_compat import load_legacy_compatibility
    from .grouping.element import ElementGroupingPolicy
    from .rules import load_ruleset

    registry = Registry()
    registry.register_checker(IdsChecker(config.resolved_ruleset_path()))
    # Two checkers, which is the first time this registry has had to be one.
    # Both are handed the same rule library and take from it the rules that
    # name them; neither knows the other exists.
    registry.register_checker(CompletenessChecker(config.resolved_ruleset_path()))
    registry.register_grouping_policy(ElementGroupingPolicy())
    registry.register_exporter(CsvExporter())
    registry.register_exporter(JsonExporter())
    # The legacy writers are told which project and which rule set version they
    # publish. Everything else in this registry is agnostic to both.
    legacy_project_id = config.legacy_project_id or None
    frozen_ruleset = (
        load_ruleset(config.legacy_ruleset_path)
        if config.legacy_ruleset_path is not None
        else None
    )
    legacy_compat = (
        load_legacy_compatibility(
            config.legacy_compat_path, expected_sha256=config.legacy_compat_sha256
        )
        if config.legacy_compat_path is not None
        else None
    )
    # The general BCF writer projects the whole run — no project or rule-set
    # scope. Narrowing to a published slice is what the legacy adapters below
    # exist for, and conflating the two is what made this exporter publish three
    # topics for a run that had twenty-one issues.
    registry.register_exporter(
        BcfExporter(
            schema_dir=default_schema_dir(config.repository_root),
            project_name=config.bcf_project_name,
            creation_author=config.bcf_creation_author,
            topic_type=config.bcf_topic_type,
            role_domain=config.bcf_role_domain,
        )
    )
    registry.register_exporter(
        LegacyBcfExporter(
            schema_dir=default_schema_dir(config.repository_root),
            project_id=legacy_project_id,
            frozen_ruleset=frozen_ruleset,
            compat=legacy_compat,
        )
    )
    registry.register_exporter(
        LegacyPbipAdapter(
            project_id=legacy_project_id,
            frozen_ruleset=frozen_ruleset,
            compat=legacy_compat,
        )
    )
    return registry
