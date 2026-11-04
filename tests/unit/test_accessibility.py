"""Tests for reading and describing axe-core results."""

from typing import TYPE_CHECKING, Any, cast

from webhook_studio_e2e.accessibility import SETTLED, WCAG_22_AA, Finding, describe, findings, scan

if TYPE_CHECKING:
    from playwright.sync_api import Page

CONTRAST_HELP = "Elements must meet minimum color contrast ratio thresholds"
RESPONSE = {
    "violations": [
        {
            "id": "color-contrast",
            "impact": "serious",
            "help": CONTRAST_HELP,
            "nodes": [{"target": ["button.send"]}, {"target": ["iframe", "span.badge"]}],
        },
        {"id": "label", "impact": None, "help": "Form elements must have labels", "nodes": [{"target": ["input"]}]},
    ]
}


class FakePage:
    """Stands in for a browser page: keeps each script it gets and answers the last with an axe-core result."""

    def __init__(self) -> None:
        """Start with no scripts."""
        self.scripts: list[str] = []
        self.waited_for: list[str] = []

    def wait_for_function(self, script: str) -> None:
        """Keep what the scan waited for.

        Args:
            script: The JavaScript condition.
        """
        self.waited_for.append(script)

    def evaluate(self, script: str) -> dict[str, Any]:
        """Keep the script and answer with the canned result.

        Args:
            script: The JavaScript to run.

        Returns:
            The axe-core result.
        """
        self.scripts.append(script)
        return RESPONSE


def test_given_axe_result_when_read_then_each_broken_rule_becomes_one_finding() -> None:
    """Given an axe-core result with two broken rules, when read, then each becomes a finding with all its elements."""
    # Given
    response = RESPONSE
    # When
    found = findings(response)
    # Then
    assert found == [
        Finding("color-contrast", "serious", CONTRAST_HELP, ("button.send", "iframe span.badge")),
        Finding("label", "unknown", "Form elements must have labels", ("input",)),
    ]


def test_given_findings_when_described_then_each_rule_and_element_has_a_line() -> None:
    """Given findings, or none, when described, then each rule and each element gets a line, or one line says none."""
    # Given
    found = findings(RESPONSE)
    # When
    text = describe(found)
    nothing = describe([])
    # Then
    assert text.splitlines() == [
        "color-contrast (serious): Elements must meet minimum color contrast ratio thresholds",
        "    button.send",
        "    iframe span.badge",
        "label (unknown): Form elements must have labels",
        "    input",
    ]
    assert nothing == "No findings."


def test_given_page_when_scanned_then_axe_runs_the_wcag_22_aa_rules_once_animations_end() -> None:
    """Given a page, when scanned, then the scan waits for animations, injects axe-core and runs WCAG 2.2 AA only."""
    # Given
    page = FakePage()
    # When
    found = scan(cast("Page", page))
    # Then
    assert [finding.rule for finding in found] == ["color-contrast", "label"]
    assert page.waited_for == [SETTLED]
    assert len(page.scripts) == 2
    assert "axe" in page.scripts[0]
    assert all(tag in page.scripts[1] for tag in WCAG_22_AA)
