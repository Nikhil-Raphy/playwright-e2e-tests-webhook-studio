"""Scan a page with axe-core for WCAG 2.2 AA and describe what it finds."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast

from axe_playwright_python.sync_playwright import Axe

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from playwright.sync_api import Page

WCAG_22_AA = ("wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa")
"""The axe-core tags for every WCAG 2.0, 2.1 and 2.2 rule at levels A and AA."""
SETTLED = "() => document.getAnimations().every((animation) => animation.playState !== 'running')"
"""True once no animation runs; colours measured mid-fade would fail the contrast rule."""


@dataclass(frozen=True, slots=True)
class Finding:
    """One axe-core rule that a page breaks.

    Attributes:
        rule: The rule id, such as "color-contrast".
        impact: How much it hurts users: minor, moderate, serious or critical.
        help: What the rule asks for.
        targets: CSS selectors of the elements that break it.
    """

    rule: str
    impact: str
    help: str
    targets: tuple[str, ...]


def findings(response: Mapping[str, Any]) -> list[Finding]:
    """Read the rules broken in an axe-core result.

    Args:
        response: The result of `axe.run`.

    Returns:
        One finding per broken rule, in axe-core's order.
    """
    violations = cast("list[dict[str, Any]]", response.get("violations", []))
    return [
        Finding(
            rule=str(violation["id"]),
            impact=str(violation.get("impact") or "unknown"),
            help=str(violation.get("help", "")),
            targets=tuple(" ".join(map(str, node["target"])) for node in violation.get("nodes", [])),
        )
        for violation in violations
    ]


def describe(found: Sequence[Finding]) -> str:
    """Write findings as text for a test failure.

    Args:
        found: The findings.

    Returns:
        One line per rule and one indented line per element, or "No findings." when there are none.
    """
    if not found:
        return "No findings."
    lines: list[str] = []
    for finding in found:
        lines.append(f"{finding.rule} ({finding.impact}): {finding.help}")
        lines.extend(f"    {target}" for target in finding.targets)
    return "\n".join(lines)


def scan(page: Page) -> list[Finding]:
    """Run axe-core on what the page shows once its animations end, for the WCAG 2.2 AA rules.

    Args:
        page: The browser page.

    Returns:
        The rules the page breaks.
    """
    page.wait_for_function(SETTLED)
    options = {"runOnly": {"type": "tag", "values": list(WCAG_22_AA)}, "resultTypes": ["violations"]}
    return findings(cast("dict[str, Any]", Axe().run(page, options=options).response))
