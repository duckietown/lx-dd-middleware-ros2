"""Sanity tests for the ROS 2 publisher/subscriber starter package.

Run from the LX root with:

    python3 -m pytest tests/

These tests validate notebook metadata and package structure without importing
the ROS runtime, so they can run both inside the editor container and on a plain
host Python.
"""

import ast
import json
import re
from collections.abc import Callable
from html import unescape
from importlib import import_module
from pathlib import Path
from typing import Any
from unittest.mock import patch
from xml.etree import ElementTree as ET

import pytest

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"
PACKAGE_DIR = ROOT / "packages" / "ros2_pubsub"
README_PATH = ROOT / "README.md"
README_EXERCISE_TOPIC = "ROS 2"
CHECKPOINT_DATA_DIR = ROOT / "checkpoint_data"
CHECKPOINT_SELF_CHECK_PATH = ROOT / "packages" / "checkpoint_self_check.py"
checkpoint_self_check = import_module("packages.checkpoint_self_check")
VSCODE_HEADING_PUNCTUATION = "[]!/'\"#$%&()*+,./:;<=>?@\\^{}|~`"
UNLINKED_NOTEBOOK_REFERENCE_PATTERN = re.compile(
    r"(?<!\[)\bNotebooks?\s+\[?\d+",
    re.IGNORECASE,
)
LINUX_NETWORKING_LX_TITLE = (
    "Learning Experience (LX): Linux and Networking on the Duckiedrone"
)
LINUX_NETWORKING_NOTEBOOK_TITLE = (
    "Linux and Networking on the Duckiedrone"
)
LINUX_NETWORKING_LX_URL = "https://github.com/duckietown/lx-dd-linux-and-networking"
IMU_SENSORS_LX_TITLE = "Duckiedrone IMU Sensors - Learning Experience"
IMU_SENSORS_LX_URL = "https://github.com/duckietown/lx-dd-sensors-imu"
TOF_SENSORS_LX_TITLE = "Duckiedrone ToF Sensors - Learning Experience"
TOF_SENSORS_LX_URL = "https://github.com/duckietown/lx-dd-sensors-tof"
UNLINKED_CROSS_LX_REFERENCE_PATTERN = re.compile(
    r"\b(?:Linux and )?Networking LX\b|\bsensor LXs?\b",
    re.IGNORECASE,
)

REQUIRED_NOTEBOOKS = {
    "1-robot-operating-system-2-graph-and-software-layers.ipynb": "# Robot Operating System 2 Graph and Software Layers",
    "2-ros-2-data-paths-and-duckiedrone-integration.ipynb": "# ROS 2 Data Paths and Duckiedrone Integration",
    "3-ros-2-nodes-topics-and-interfaces.ipynb": "# ROS 2 Nodes, Topics, and Interfaces",
    "4-ros-2-discovery-domains-and-names.ipynb": "# ROS 2 Discovery, Domains, and Names",
    "5-ros-2-workspaces-and-packages.ipynb": "# ROS 2 Workspaces and Packages",
    "6-build-and-discover-a-ros-2-package.ipynb": "# Build and Discover a ROS 2 Package",
    "7-inspect-a-local-ros-2-graph.ipynb": "# Inspect a Local ROS 2 Graph",
    "8-inspect-a-duckiedrone-ros-2-graph.ipynb": "# Inspect a Duckiedrone ROS 2 Graph",
    "9-ros-2-node-lifecycles-and-publishers.ipynb": "# ROS 2 Node Lifecycles and Publishers",
    "10-ros-2-subscribers-and-diagnosis.ipynb": "# ROS 2 Subscribers and Diagnosis",
    "11-ros-2-names-and-remapping.ipynb": "# ROS 2 Names and Remapping",
}
INTERACTIVE_CHECKPOINT_NOTEBOOKS = set(REQUIRED_NOTEBOOKS)
TRY_IT_HEADING_PATTERN = re.compile(r"^### Try it(?:[: ].*)?$", re.MULTILINE)
SECTION_HEADING_PATTERN = re.compile(r"^#{2,3} .+$", re.MULTILINE)
CHECKPOINT_CODE_SOURCE = [
    "import sys",
    "from pathlib import Path",
    "",
    "working_directory = Path.cwd()",
    "parent_directory = working_directory.parent",
    'if (parent_directory / "packages").is_dir():',
    "    parent_directory_path = str(parent_directory)",
    "    sys.path.insert(0, parent_directory_path)",
    "",
    "from packages.checkpoint_self_check import display_checkpoint_self_checks",
    "",
    "display_checkpoint_self_checks()",
]
CHECKPOINT_TAIL = (
    "## Checkpoint\n\n"
    "Run the self-check in the next cell. Write or select a response before revealing the answer.\n"
)
PRESENTATION_STYLE = re.compile(
    r"<style>\n"
    r"\.lx-table \{\n"
    r"\s+margin: 1\.5em auto;\n"
    r"\s+text-align: left;\n"
    r"\}\n\n"
    r"\.lx-table caption \{\n"
    r"\s+caption-side: top;\n"
    r"\s+font-size: 0\.9em;\n"
    r"\s+margin-bottom: 0\.6em;\n"
    r"\s+text-align: center;\n"
    r"\}\n\n"
    r"\.lx-figure \{\n"
    r"\s+margin: 1\.5em auto;\n"
    r"\s+text-align: center;\n"
    r"\}\n\n"
    r"\.lx-figure figcaption \{\n"
    r"\s+font-size: 0\.9em;\n"
    r"\s+margin-top: 0\.6em;\n"
    r"\s+text-align: center;\n"
    r"\}\n\n"
    r"table \{\n"
    r"\s+margin: 0 auto 1\.5em;\n"
    r"\}\n\n"
    r"p:has\(> a\[id\^='table-'\]\) \{\n"
    r"\s+margin: 0;\n"
    r"\}\n\n"
    r"p:has\(> a\[id\^='table-'\]\) \+ p,\n"
    r"a\[id\^='table-'\] \+ p \{\n"
    r"\s+font-size: 0\.9em;\n"
    r"\s+margin: 1\.5em 0 0\.6em;\n"
    r"\s+text-align: center;\n"
    r"\}\n\n"
    r"p\.lx-figure \{\n"
    r"\s+margin: 1\.5em auto 0;\n"
    r"\}\n\n"
    r"p\.lx-figure \+ p \{\n"
    r"\s+font-size: 0\.9em;\n"
    r"\s+margin: 0\.6em 0 1\.5em;\n"
    r"\s+text-align: center;\n"
    r"\}\n</style>"
)
TABLE_PATTERN = re.compile(r"<table\b(?P<attrs>[^>]*)>.*?</table>", re.DOTALL)
FIGURE_PATTERN = re.compile(r"<figure\b(?P<attrs>[^>]*)>.*?</figure>", re.DOTALL)
CAPTION_PATTERN = re.compile(r"<(?P<tag>caption|figcaption)\b(?P<attrs>[^>]*)>")
MEDIA_PATTERN = re.compile(
    r"<(?P<tag>figure|table)\b(?P<attrs>[^>]*)>.*?</(?P=tag)>"
    r'|<a\b(?P<anchor_attrs>[^>]*\bid="(?:table|figure)-[^"]*"[^>]*)></a>',
    re.DOTALL,
)
MARKDOWN_LITERAL_PATTERN = re.compile(
    r"^[ \t]*(?P<fence>`{3,}|~{3,})[^\n]*\n.*?"
    r"^[ \t]*(?P=fence)[`~]*[ \t]*(?:\n|$)"
    r"|(?P<ticks>`+)(?!`).*?(?P=ticks)(?!`)"
    r"|<(?P<tag>pre|style|script)\b[^>]*>.*?</(?P=tag)>"
    r"|\$\$.*?\$\$|\$[^\n$]*\$"
    r"|(?<=\]\()[^\n)]*(?=\))"
    r"|<[^>\n]+>|\\.",
    re.MULTILINE | re.DOTALL,
)
ASTERISK_EMPHASIS_PATTERN = re.compile(
    r"(?<!\*)(?P<marker>\*+)(?![\s*])"
    r"(?:(?!\n[ \t]*\n).)*?\S(?P=marker)(?!\*)",
    re.DOTALL,
)
NON_ASCII_STYLE_PATTERN = re.compile(
    r"[\u00a0\u2000-\u200f\u2010-\u201f\u2026\u2028-\u202f"
    r"\u205f\u2060\ufeff\u2190-\u21ff\u2500-\u27ff"
    r"\u2900-\u297f\u2b00-\u2bff\U0001f300-\U0001faff]"
)


EDITORIAL_LITERAL_PATTERN = re.compile(
    r"<code\b[^>]*>.*?</code>|" + MARKDOWN_LITERAL_PATTERN.pattern,
    MARKDOWN_LITERAL_PATTERN.flags,
)
ROBOT_WORD = re.compile(r"(?<![\w/])robots?(?![\w/])", re.IGNORECASE)
GENERIC_ROBOT_CONTEXT = re.compile(
    r"\bgeneric robots?\b|\brobots? in general\b|\bany other robots?\b"
    r"|\bother types of robots?\b|\bfrom phones to robots\b",
    re.IGNORECASE,
)
NAME_INTRODUCTION = ", where `DUCKIEDRONE_NAME` is the name of your Duckiedrone"
NAME_EXPLANATION = re.compile(
    r"\bDUCKIEDRONE_NAME\b\s*(?:(?:is|means|represents|stands for|refers to|denotes"
    r"|should be replaced with|must be replaced with)\s+|[:=(]\s*)"
    r"[^.!?;\n]{0,100}?\b(?:name|hostname)\b"
    r"|\b(?:replace|substitute)\s+DUCKIEDRONE_NAME\s+with\s+"
    r"[^.!?;\n]{0,100}?\b(?:name|hostname)\b",
    re.IGNORECASE,
)
CONCEPT_ALIASES = {
    "PX4": ("PX4",),
    "ROS 2": (
        "ROS 2", "Robot Operating System 2", "Robot Operating System (ROS) 2", "Robot Operating System 2 (ROS 2)",
    ),
    "DTPS": ("DTPS", "Duckietown Postal Service", "Duckietown Postal Service (DTPS)"),
    "MAVLink": ("MAVLink", "Micro Air Vehicle Link", "Micro Air Vehicle Link (MAVLink)"),
    "MAVROS2": ("MAVROS2", "MAVROS"),
    "PID": ("PID", "PID controller", "Proportional Integral Derivative (PID)"),
    "Docker Engine": ("Docker Engine",),
    "Docker Hub": ("Docker Hub",),
    "Debian": ("Debian",),
    "Fedora": ("Fedora",),
    "Ubuntu": ("Ubuntu",),
    "Zenoh": ("Zenoh",),
    "NuttX": ("NuttX",),
    "QGroundControl": ("QGroundControl",),
    "Gimbal lock": ("Gimbal lock",),
    "shebang": ("shebang",),
    "DHCP": ("DHCP",),
    "TCP": ("TCP",),
    "UDP": ("UDP",),
    "curl": ("curl",),
}
EXTERNAL_LINK = re.compile(
    r"(?<!!)\[(?P<label>[^\]\n]+)\]\((?P<url>https?://[^\s)]+)\)"
    r"|<a\b[^>]*href=[\"']https?://[^\"']+[\"'][^>]*>(?P<html>.*?)</a>",
    re.DOTALL,
)
PROSE_WORDING_RULES = {
    "introduce examples with 'such as' or 'for example'": re.compile(
        r"\(\s*like\b|\b(?:commands?|tools?|programs?|languages?|libraries|services|things)\s+like\b"
        r"|,\s+like\s+(?:our|the)\s+(?:\w+\s+)?example\b"
        r"|\b(?:output|results?)\s+like\s+this\b",
        re.IGNORECASE,
    ),
    "replace informal wording with direct instructional prose": re.compile(
        r"\b(?:gonna|wanna|gotta|kinda|sorta)\b"
        r"|\b(?:check\s+out|a\s+bunch\s+of|pretty\s+much|you\s+guys|and\s+stuff)\b",
        re.IGNORECASE,
    ),
    "remove accidentally repeated words": re.compile(
        r"\b(?P<word>the|a|an|is|are|of|to|with|and)\s+(?P=word)\b",
        re.IGNORECASE,
    ),
    "replace prose dash punctuation with a comma, colon, parentheses or a sentence": re.compile(
        r"(?<=[^\s|])[ \t]+-{1,2}[ \t]+(?=[^\s|])|[\u2013\u2014]",
    ),
}


def reference_sections(source: str) -> list[tuple[int, int]]:
    """Locate further-reading sections through the next peer or higher heading."""
    headings = list(re.finditer(r"^[ \t]*(#{1,6})[ \t]+([^\n]+)", source, re.MULTILINE))
    sections = []
    for number, heading in enumerate(headings):
        if not re.match(
            r"(?:further reading|references?|sources?|additional resources?|external links|bibliography)\b",
            heading[2],
            re.IGNORECASE,
        ):
            continue
        end = next(
            (following.start() for following in headings[number + 1:] if len(following[1]) <= len(heading[1])),
            len(source),
        )
        sections.append((heading.start(), end))
    return sections


def mask_editorial_literal(match: re.Match[str]) -> str:
    """Retain a placeholder token without changing offsets or paragraph boundaries."""
    literal = match.group(0)
    masked = re.sub(r"[^\n]", " ", literal)
    if (
        literal.startswith(("`", "<code"))
        and not literal.startswith("```")
        and "DUCKIEDRONE_NAME" in literal
    ):
        position = literal.index("DUCKIEDRONE_NAME")
        end = position + len("DUCKIEDRONE_NAME")
        masked = masked[:position] + "DUCKIEDRONE_NAME" + masked[end:]
    return masked


def editorial_prose(source: str, *, exclude_references: bool = False) -> str:
    """Retain prose and placeholder tokens while excluding executable examples."""
    if exclude_references:
        for start, end in reversed(reference_sections(source)):
            source = source[:start] + re.sub(r"[^\n]", " ", source[start:end]) + source[end:]
    source = EDITORIAL_LITERAL_PATTERN.sub(mask_editorial_literal, source)
    source = re.sub(r"__|\*\*|(?<!\w)[*_]|[*_](?!\w)", "", source)
    return unescape(re.sub(r"^[ \t]*#+[^\n]*", "", source, flags=re.MULTILINE))


def assert_duckiedrone_name_explained_once(documents: list[tuple[str, str]]) -> None:
    """Use the standard introduction once, in the placeholder's first paragraph."""
    first_use = None
    definition = None
    for context, source in documents:
        prose = editorial_prose(source)
        for number, (raw, paragraph) in enumerate(zip(source.split("\n\n"), prose.split("\n\n"), strict=True)):
            if "DUCKIEDRONE_NAME" in raw and first_use is None:
                first_use = (context, number)
            for _match in NAME_EXPLANATION.finditer(paragraph):
                assert definition is None, f"{context}: repeated DUCKIEDRONE_NAME explanation; first at {definition}"
                assert first_use == (context, number), f"{context}: explain DUCKIEDRONE_NAME in its first-use paragraph ({first_use})"
                literal_spans = [literal.span() for literal in EDITORIAL_LITERAL_PATTERN.finditer(raw)]
                introductions = re.finditer(re.escape(NAME_INTRODUCTION), raw)
                assert any(
                    not any(start <= introduction.start() < end for start, end in literal_spans)
                    for introduction in introductions
                ), (
                    f"{context}: introduce DUCKIEDRONE_NAME using {NAME_INTRODUCTION!r}"
                )
                definition = (context, number)
    assert first_use is None or definition is not None, f"{first_use}: explain DUCKIEDRONE_NAME at its first use"


def concept_label(label: str) -> str:
    """Normalize emphasis and HTML without conflating reference titles with concepts."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]*>|[`*_]", "", unescape(label))).strip()


def explanatory_links(source: str) -> list[tuple[int, str]]:
    """Find term links outside literals, retaining their paragraph positions."""
    literals = [match.span() for match in EDITORIAL_LITERAL_PATTERN.finditer(source)]
    literals.extend(reference_sections(source))
    links = []
    for match in EXTERNAL_LINK.finditer(source):
        if any(start <= match.start() and end >= match.end() for start, end in literals):
            continue
        label = match.group("label") or match.group("html")
        if "`" not in label:
            links.append((source[:match.start()].count("\n\n"), concept_label(label)))
    return links


def explanatory_concepts(document_links: list[list[tuple[int, str]]]) -> dict[str, tuple[str, ...]]:
    """Recognize aliases and newly introduced single-term concept labels."""
    aliases_by_concept = dict(CONCEPT_ALIASES)
    for links in document_links:
        for _number, label in links:
            if re.fullmatch(r"[A-Za-z][A-Za-z0-9.+-]*", label) and label.casefold() not in {
                "source", "here", "documentation", "reference", "overview", "guide",
            }:
                aliases_by_concept.setdefault(label, (label,))
    return aliases_by_concept


def assert_explanatory_concept_links(documents: list[tuple[str, str]]) -> None:
    """Link a concept once at first use, allowing later reference citations."""
    document_links = [explanatory_links(source) for _context, source in documents]
    aliases_by_concept = explanatory_concepts(document_links)
    first_use: dict[str, tuple[str, int]] = {}
    linked: dict[str, tuple[str, int]] = {}
    for (context, source), links in zip(documents, document_links, strict=True):
        prose = editorial_prose(source, exclude_references=True)
        for number, paragraph in enumerate(prose.split("\n\n")):
            for concept, aliases in aliases_by_concept.items():
                for alias in aliases:
                    if re.search(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", paragraph, re.IGNORECASE):
                        first_use.setdefault(concept, (context, number))
                        break
            for link_number, label in links:
                if link_number != number:
                    continue
                linked_concept = next(
                    (name for name, aliases in aliases_by_concept.items() if label.casefold() in {alias.casefold() for alias in aliases}),
                    None,
                )
                if linked_concept is None:
                    continue
                assert linked_concept not in linked, f"{context}: repeated explanatory link for {linked_concept}; first at {linked.get(linked_concept)}"
                assert first_use.get(linked_concept) == (context, number), f"{context}: link {linked_concept} at its first use ({first_use.get(linked_concept)})"
                linked[linked_concept] = (context, number)


@pytest.mark.parametrize(
    "documents",
    [
        [],
        [("1", "Run the following command" + NAME_INTRODUCTION + ":\n\n```bash\nssh duckie@DUCKIEDRONE_NAME.local\n```")],
        [("1", "Run `dts duckiebot update DUCKIEDRONE_NAME`" + NAME_INTRODUCTION + "."), ("2", "`ssh duckie@DUCKIEDRONE_NAME.local`")],
        [("1", "Use this topic" + NAME_INTRODUCTION + "."), ("2", "```bash\necho DUCKIEDRONE_NAME\n```")],
        [("1", "Inspect the following path" + NAME_INTRODUCTION + ".\n\n<code>ssh duckie@DUCKIEDRONE_NAME.local\n\n</code>")],
    ],
)
def test_duckiedrone_name_explanations_accept_first_use(documents: list[tuple[str, str]]) -> None:
    assert_duckiedrone_name_explained_once(documents)


@pytest.mark.parametrize(
    "documents",
    [
        [("1", "`ssh duckie@DUCKIEDRONE_NAME.local`")],
        [("1", "`ssh duckie@DUCKIEDRONE_NAME.local`\n\nDUCKIEDRONE_NAME is your hostname.")],
        [("2", "`ssh duckie@DUCKIEDRONE_NAME.local`"), ("10", "DUCKIEDRONE_NAME is your hostname.")],
        [("1", "DUCKIEDRONE_NAME is your hostname."), ("2", "Replace DUCKIEDRONE_NAME with your Duckiedrone's name.")],
        [("1", "DUCKIEDRONE_NAME is your hostname. DUCKIEDRONE_NAME means the Duckiedrone name.")],
        [("1", "DUCKIEDRONE_NAME: your Duckiedrone's hostname."), ("2", "DUCKIEDRONE_NAME should be replaced with your Duckiedrone's name.")],
        [("1", "Use this topic, where `DUCKIEDRONE_NAME` is your Duckiedrone's name.")],
        [("1", "Use this topic, where `DUCKIEDRONE_NAME` is the Duckiedrone's name.")],
        [("1", "Use this topic, where DUCKIEDRONE_NAME is the name of your Duckiedrone.")],
        [("1", "DUCKIEDRONE_NAME is your Duckiedrone's name. <code>" + NAME_INTRODUCTION + "</code>")],
        [("1", "Use this topic" + NAME_INTRODUCTION + "."), ("2", "Use this command" + NAME_INTRODUCTION + ".")],
        [("1", "`ssh duckie@DUCKIEDRONE_NAME.local`\n\nUse this topic" + NAME_INTRODUCTION + ".")],
    ],
)
def test_duckiedrone_name_explanations_reject_missing_late_and_repeated(documents: list[tuple[str, str]]) -> None:
    with pytest.raises(AssertionError, match="DUCKIEDRONE_NAME"):
        assert_duckiedrone_name_explained_once(documents)


@pytest.mark.parametrize(
    "documents",
    [
        [("1", "[__PX4__](https://px4.io/) is autopilot software."), ("2", "PX4 publishes messages. See the [PX4 parameter reference](https://docs.px4.io/main/en/advanced_config/parameter_reference.html).")],
        [("1", '[Robot Operating System 2](https://docs.ros.org/) uses topics.\n<a href="https://dtps.org/">DTPS</a> carries messages.'), ("2", "ROS 2 and Duckietown Postal Service exchange data.")],
        [("1", "[Notebook 2](./2-example.ipynb) and [Figure 1](#figure-1)."), ("2", "[Notebook 2](./2-example.ipynb)")],
        [("1", "```text\n[PX4](https://px4.io/)\n\n[PX4](https://docs.px4.io/)\n```"), ("2", "[PX4](https://px4.io/) controls flight.")],
        [("1", "PX4 is autopilot software.\n\n## Further reading\n\n[PX4](https://px4.io/)"), ("2", "## Further reading\n\n[PX4](https://docs.px4.io/)")],
    ],
)
def test_explanatory_links_accept_first_use_and_reference_citations(documents: list[tuple[str, str]]) -> None:
    assert_explanatory_concept_links(documents)


@pytest.mark.parametrize(
    "documents",
    [
        [("1", "PX4 is autopilot software."), ("2", "[PX4](https://px4.io/) controls flight.")],
        [("1", "[__PX4__](https://px4.io/) controls flight."), ("2", "[PX4](https://docs.px4.io/main/) receives messages.")],
        [("1", "[Robot Operating System 2](https://docs.ros.org/) uses topics."), ("2", "[ROS 2](https://ros.org/) uses nodes.")],
        [("1", "[DTPS](https://dtps.org/) carries messages."), ("2", '<a href="https://docs.dtps.org/">Duckietown Postal Service</a> carries messages.')],
        [("1", "[PX4](https://px4.io/) and [__PX4__](https://docs.px4.io/) control flight.")],
        [("1", "[GNSS](https://example.org/gnss/) provides positioning."), ("2", "[GNSS](https://example.org/positioning/) provides positioning.")],
        [("1", "PX4 is autopilot software.\n\n## Further reading\n\n[PX4](https://px4.io/)\n\n## Flight software\n\n[PX4](https://docs.px4.io/) controls flight.")],
        [("1", "[Robot Operating System 2 (__ROS 2__)](https://www.ros.org/) uses topics."), ("2", "[ROS 2](https://docs.ros.org/) uses nodes.")],
    ],
)
def test_explanatory_links_reject_late_and_repeated_definitions(documents: list[tuple[str, str]]) -> None:
    with pytest.raises(AssertionError, match=r"first use|repeated explanatory"):
        assert_explanatory_concept_links(documents)


def assert_linked_acronym_style(source: str, context: str = "Markdown") -> None:
    """Keep a linked expansion and its parenthesized acronym inside one link."""
    literals = [match.span() for match in EDITORIAL_LITERAL_PATTERN.finditer(source)]
    for link in EXTERNAL_LINK.finditer(source):
        if any(start <= link.start() and end >= link.end() for start, end in literals):
            continue
        suffix = re.match(r"[ \t]*(?:\n[ \t]*)?\(([^()\n]+)\)", source[link.end():])
        if suffix is None:
            continue
        acronym = concept_label(suffix[1])
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9]*(?: (?:\d+|Code))?", acronym) is None:
            continue
        if re.search(r"[A-Z].*[A-Z]", acronym) is None:
            continue
        message = f"{context}: include {acronym} inside the link with its full name"
        raise AssertionError(message)


@pytest.mark.parametrize(
    "source",
    [
        "[Robot Operating System 2 (__ROS 2__)](https://www.ros.org/) uses topics.",
        '<a href="https://dtps.org/">Duckietown Postal Service (DTPS)</a> carries messages.',
        "[Micro Air Vehicle Link (MAVLink)](https://mavlink.io/) carries telemetry.",
        "[Visual Studio Code (VS Code)](https://code.visualstudio.com/) is an editor.",
        "[PX4](https://px4.io/) (autopilot software) controls flight.",
        "```markdown\n[Robot Operating System 2](https://www.ros.org/) (ROS 2)\n```",
        "`[Duckietown Postal Service](https://dtps.org/) (DTPS)` is a literal example.",
    ],
)
def test_linked_acronym_style_accepts_complete_labels_and_literals(source: str) -> None:
    assert_linked_acronym_style(source)


@pytest.mark.parametrize(
    "source",
    [
        "[Robot Operating System 2](https://www.ros.org/) (__ROS 2__) uses topics.",
        '<a href="https://dtps.org/">Duckietown Postal Service</a> (DTPS) carries messages.',
        "[Micro Air Vehicle Link](https://mavlink.io/) (MAVLink) carries telemetry.",
        "[Visual Studio Code](https://code.visualstudio.com/) (VS Code) is an editor.",
        "[Multicast DNS](https://www.rfc-editor.org/rfc/rfc6762)\n(mDNS) resolves names.",
    ],
)
def test_linked_acronym_style_rejects_split_definitions(source: str) -> None:
    with pytest.raises(AssertionError, match="inside the link"):
        assert_linked_acronym_style(source)


def test_notebook_linked_acronyms_include_the_acronym() -> None:
    for path in NOTEBOOK_DIR.glob("*.ipynb"):
        notebook = json.loads(path.read_text(encoding="utf-8"))
        for number, cell in enumerate(notebook["cells"], start=1):
            if cell["cell_type"] == "markdown":
                assert_linked_acronym_style(cell_source(cell), f"{path.name}, Cell {number}")


@pytest.mark.parametrize("rule", [assert_duckiedrone_name_explained_once, assert_explanatory_concept_links])
def test_notebook_explanations_follow_reading_order(rule: Callable[[list[tuple[str, str]]], None]) -> None:
    documents = []
    paths = sorted(NOTEBOOK_DIR.glob("*.ipynb"), key=lambda path: int(path.name.partition("-")[0]))
    for path in paths:
        notebook = json.loads(path.read_text(encoding="utf-8"))
        for number, cell in enumerate(notebook["cells"], start=1):
            if cell["cell_type"] == "markdown":
                documents.append((f"{path.name}, Cell {number}", cell_source(cell)))
    rule(documents)


def assert_duckiedrone_terminology(source: str, context: str = "Markdown") -> None:
    """Require Duckiedrone for this platform, retaining explicit generic references."""
    prose = EDITORIAL_LITERAL_PATTERN.sub(
        lambda match: (
            re.sub(r"<[^>]+>", "", match.group(0))
            if match.group(0).startswith("<pre")
            else re.sub(r"[^\n]", " ", match.group(0))
        ),
        source,
    )
    prose = re.sub(r"__|\*\*|(?<!\w)[*_]|[*_](?!\w)", "", prose)
    prose = re.sub(r"\brobot operating system(?:\s+2)?\b", "ROS", prose, flags=re.IGNORECASE)
    for paragraph in re.split(r"(?<=[.!?])\s+|\n\n", prose):
        if GENERIC_ROBOT_CONTEXT.search(paragraph):
            continue
        robot = ROBOT_WORD.search(paragraph)
        assert robot is None, (
            f"{context}: use Duckiedrone instead of {robot.group(0)!r} for "
            "this platform; make a genuinely generic robot reference explicit"
        )


@pytest.mark.parametrize(
    "source",
    [
        "Connect to your Duckiedrone. The DUCKIEDRONES share the network.",
        "Robot Operating System 2 (ROS 2) transports sensor data.",
        "__Robot Operating System 2__ transports sensor data.",
        "A generic robot may use different hardware.",
        "This applies to a Duckiedrone or any other robot.",
        "An IMU appears in devices from phones to robots.",
        "`robot/basics` and <code>ROBOT_NAME</code> are literal names.",
        "<code>robot</code> is a literal resource name.",
        "```bash\ndts duckiebot update ROBOT_NAME\n```\n",
        "[Architecture](https://example.org/robots/overview)",
        "<figure><pre>robot/basics -> driver</pre></figure>",
    ],
)
def test_duckiedrone_terminology_accepts_generic_and_literal_uses(source: str) -> None:
    """Keep generic examples, software names, paths, and commands unchanged."""
    assert_duckiedrone_terminology(source)


@pytest.mark.parametrize(
    "source",
    [
        "Connect to your robot.",
        "The Robot runs this service.",
        "Start the ROBOT before continuing.",
        "Inspect the robots.",
        "The ROBOTS are on this network.",
        "<table><tr><td>Robot resources</td></tr></table>",
        "<figure><pre>base station -> robot</pre></figure>",
        "A generic robot may use different hardware. Start your robot now.",
        "Connect to the __robot__.",
    ],
)
def test_duckiedrone_terminology_rejects_platform_robot_names(source: str) -> None:
    """Check capitalization, plural forms, table text, and diagram labels."""
    with pytest.raises(AssertionError, match="use Duckiedrone"):
        assert_duckiedrone_terminology(source)


def test_notebooks_use_duckiedrone_terminology() -> None:
    """Check every notebook Markdown cell without including the README."""
    for notebook_path in NOTEBOOK_DIR.glob("*.ipynb"):
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        for number, cell in enumerate(notebook["cells"], start=1):
            if cell["cell_type"] == "markdown":
                assert_duckiedrone_terminology(
                    cell_source(cell), f"{notebook_path.name}, Cell {number}",
                )


def mask_instruction_literal(match: re.Match[str]) -> str:
    """Exclude literals without joining the prose on either side."""
    literal = match.group(0)
    masked = re.sub(r"[^\n]", " ", literal)
    if re.fullmatch(r"</?[A-Za-z][A-Za-z0-9-]*(?:\s[^>]*)?\s*/?>", literal):
        return masked
    return "literal " + masked


def assert_clear_prose(source: str, context: str = "Markdown") -> None:
    """Apply concrete house-style checks, not an authorship detector."""
    source = EXTERNAL_LINK.sub(mask_instruction_literal, source)
    prose = EDITORIAL_LITERAL_PATTERN.sub(mask_instruction_literal, source)
    prose = re.sub(r"__|\*\*|(?<!\w)[*_]|[*_](?!\w)", "", prose)
    prose = unescape(prose)
    for message, pattern in PROSE_WORDING_RULES.items():
        match = pattern.search(prose)
        assert match is None, f"{context}: {message}: {match.group(0)!r}"
    depth = 0
    for token in re.finditer(r"[()]|\b(?:e\.g\.|i\.e\.)(?!\w)", prose, re.IGNORECASE):
        value = token.group(0)
        if value == "(":
            depth += 1
        elif value == ")":
            depth = max(0, depth - 1)
        else:
            assert depth, (
                f"{context}: spell out {value!r} outside parentheses; "
                "use 'for example', 'such as' or 'that is'"
            )


def assert_reference_presentation(source: str, context: str = "Markdown") -> None:
    """Integrate supporting links into prose, retaining reading-list entries."""
    visible = EDITORIAL_LITERAL_PATTERN.sub(mask_editorial_literal, source)
    references = reference_sections(source)
    quotes = {'"': '"', "'": "'", "\u201c": "\u201d", "\u2018": "\u2019"}
    for link in EXTERNAL_LINK.finditer(source):
        if not visible[link.start():link.end()].strip():
            continue
        prefix = source[:link.start()].rstrip()
        suffix = source[link.end():].lstrip()
        closing_quote = quotes.get(prefix[-1:])
        assert not (closing_quote and suffix.startswith(closing_quote)), (
            f"{context}: do not enclose a linked article title in quotation marks"
        )
        label = link.group("label") or link.group("html") or ""
        label = concept_label(label)
        visible_brackets = (
            label.startswith("[")
            or (prefix.endswith("[") and suffix.startswith(("]", "\\]")))
        )
        assert not visible_brackets, f"{context}: do not add visible square brackets around a reference link"
        if any(start <= link.start() < end for start, end in references):
            continue
        paragraph_start = source.rfind("\n\n", 0, link.start()) + len("\n\n")
        if paragraph_start == 1:
            paragraph_start = 0
        paragraph_end = source.find("\n\n", link.end())
        if paragraph_end < 0:
            paragraph_end = len(source)
        leading = source[paragraph_start:link.start()]
        trailing = source[link.end():paragraph_end]
        line_prefix = leading.rsplit("\n", 1)[-1]
        if re.fullmatch(r"[ \t]*(?:[-*+] |\d+[.)] )", line_prefix):
            continue
        trailing = EXTERNAL_LINK.sub("", trailing)
        trailing = re.sub(r"\b(?:and|or)\b|[\s.,;!?]", "", trailing)
        assert trailing or (
            leading.strip() and not leading.rstrip().endswith((".", "!", "?"))
        ), f"{context}: introduce a supporting reference with prose such as 'See ...'"


@pytest.mark.parametrize(
    "source",
    [
        "Containers look like real computers.",
        "An image is static, like an archive.",
        "This behaves like the preceding example.",
        "Use commands such as `docker ps`.",
        "Supported systems (e.g., Linux) share this behavior.",
        "Inspect its state (i.e., whether it is running).",
        "One case (including nested examples (e.g., Linux)) is sufficient.",
        "Read-write access uses a non-root account and a range of 0-10.",
        "Parameters:\n\n- First value.\n- Second value.",
        "| Quantity | Unit |\n| --- | --- |\n| Frame | - |",
        "<table><tr><td>Frame</td>\n<td>-</td></tr></table>",
        "Don't stop a service that isn't yours.",
        "Switch to `root` to inspect the file.",
        "The [Guide](https://example.org) is the reference.",
        "The [Sensors - Learning Experience](https://example.org/e.g.-guide) explains this.",
        "See <a href='https://example.org'>Representations - Part 1</a>.",
        "The YAML (YAML Ain't Markup Language) file records the settings.",
        "Read <strong>the</strong> file.",
        "```text\ncheck out commands like x - y, e.g., the the command\n```",
        "<pre>check out commands like x - y, i.e., the the command</pre>",
        "<code>check out commands like x - y, e.g., the the command</code>",
        "$x - y$ and $$x \\text{ i.e. } y$$ are mathematical literals.",
    ],
)
def test_clear_prose_accepts_comparisons_titles_and_literals(source: str) -> None:
    assert_clear_prose(source)


@pytest.mark.parametrize(
    ("source", "error"),
    [
        ("Use commands like `docker ps`.", "introduce examples"),
        ("Broad commands (like `docker system prune`) affect other work.", "introduce examples"),
        ("It is running, like our sleeper example.", "introduce examples"),
        ("It may produce output like this:", "introduce examples"),
        ("Use a local daemon, e.g., the base station's daemon.", "outside parentheses"),
        ("Check the state, i.e., whether it is running.", "outside parentheses"),
        ("Examples (e.g., Linux) differ, i.e., configurations vary.", "outside parentheses"),
        ("Check out the reference.", "informal wording"),
        ("We are gonna run a bunch of commands.", "informal wording"),
        ("You guys can pretty much inspect it.", "informal wording"),
        ("It records logs and stuff.", "informal wording"),
        ("Inspect the the file.", "repeated words"),
        ("Inspect the __the__ file.", "repeated words"),
        ("Inspect <strong>the the</strong> file.", "repeated words"),
        ("The image is ready - run it.", "dash punctuation"),
        ("The image is ready -- run it.", "dash punctuation"),
        ("The image is ready\u2014run it.", "dash punctuation"),
        ("The image is ready &mdash; run it.", "dash punctuation"),
        ("The image is ready &#8211; run it.", "dash punctuation"),
    ],
)
def test_clear_prose_rejects_example_shorthand_informal_wording_and_dashes(
    source: str, error: str,
) -> None:
    with pytest.raises(AssertionError, match=error):
        assert_clear_prose(source)


@pytest.mark.parametrize(
    "source",
    [
        "See [Docker's guide](https://example.org).",
        "See [the guide](https://example.org) and [the reference](https://example.net).",
        "The [Guide](https://example.org) explains this behavior.",
        "For details, see <a href='https://example.org'>the guide</a>.",
        "## Further reading\n\n[Guide](https://example.org).",
        "## References\n\n- [Guide](https://example.org).",
        "Consult these references:\n\n- [Guide](https://example.org).",
        '`"[Guide](https://example.org)"` is literal Markdown.',
        '<code>"[Guide](https://example.org)"</code>',
        '```markdown\nFact. "[Guide](https://example.org)"\n```',
        "```markdown\nFact. [[Guide](https://example.org)]\n```",
    ],
)
def test_reference_presentation_accepts_contextual_links_and_literals(source: str) -> None:
    assert_reference_presentation(source)


@pytest.mark.parametrize(
    ("source", "error"),
    [
        ("Containers share a kernel. [Guide](https://example.org)", "supporting reference"),
        ("Containers share a kernel. [Guide](https://example.org).", "supporting reference"),
        ("Fact. [Guide](https://example.org) and [Reference](https://example.net).", "supporting reference"),
        ("[Guide](https://example.org).", "supporting reference"),
        ('See "[Guide](https://example.org)".', "quotation marks"),
        ("See '[Guide](https://example.org)'.", "quotation marks"),
        ("See \u201c[Guide](https://example.org)\u201d.", "quotation marks"),
        ("See [[Guide](https://example.org)].", "visible square brackets"),
        ("See \\[[Guide](https://example.org)\\].", "visible square brackets"),
        ("See [ [Guide](https://example.org) ].", "visible square brackets"),
        ('See "<a href="https://example.org">Guide</a>".', "quotation marks"),
        ('## Further reading\n\n"[Guide](https://example.org)".', "quotation marks"),
        ('See <a href="https://example.org">[Guide]</a>.', "visible square brackets"),
        ('See <a href="https://example.org"> <strong>[Guide]</strong> </a>.', "visible square brackets"),
        ('See <a href="https://example.org">&#91;Guide&#93;</a>.', "visible square brackets"),
    ],
)
def test_reference_presentation_rejects_dangling_and_wrapped_titles(
    source: str, error: str,
) -> None:
    with pytest.raises(AssertionError, match=error):
        assert_reference_presentation(source)


@pytest.mark.parametrize("rule", [assert_clear_prose, assert_reference_presentation])
def test_notebook_prose_follows_editorial_style(rule: Callable[[str, str], None]) -> None:
    """Check notebook prose without applying new editorial rules to the README."""
    for path in NOTEBOOK_DIR.glob("*.ipynb"):
        notebook = json.loads(path.read_text(encoding="utf-8"))
        for number, cell in enumerate(notebook["cells"], start=1):
            if cell["cell_type"] == "markdown":
                rule(cell_source(cell), f"{path.name}, Cell {number}")


def cell_source(cell: dict[str, Any]) -> str:
    """Return a cell source regardless of its valid notebook representation."""
    source = cell["source"]
    if isinstance(source, list):
        return "".join(
            line if line.endswith("\n") else f"{line}\n"
            for line in source
        )
    return source


def assert_media_introductions(source: str, context: str = "Markdown") -> None:
    """Require a linked introductory sentence immediately before each media item."""
    media_items = list(MEDIA_PATTERN.finditer(source))
    for index, media in enumerate(media_items):
        attributes = media["attrs"] or media["anchor_attrs"]
        identifier = re.search(r'\bid="([^"]+)"', attributes)
        assert identifier is not None, f"{context}: media needs an anchor"
        anchor = identifier[1]
        kind = media["tag"] or anchor.split("-", 1)[0]
        label = kind.capitalize()
        numbered_anchor = re.fullmatch(rf"{kind}-([1-9]\d*)", anchor)
        assert numbered_anchor is not None, (
            f"{context}: {label} needs a positive {kind}-N anchor"
        )
        number = numbered_anchor[1]
        if media["tag"]:
            caption_tag = "caption" if kind == "table" else "figcaption"
            caption = re.search(
                rf"<{caption_tag}\b[^>]*>(.*?)</{caption_tag}>",
                media.group(0),
                re.DOTALL,
            )
            assert caption is not None, f"{context}: {label} needs a numbered {caption_tag}"
            caption_text = concept_label(caption[1])
            assert re.match(rf"{label}\s+{number}\s*:", caption_text), (
                f"{context}: {caption_tag} must start with '{label} {number}:'"
            )
        else:
            end = media_items[index + 1].start() if index + 1 < len(media_items) else len(source)
            following_source = source[media.end():end]
            caption_source = EDITORIAL_LITERAL_PATTERN.sub(mask_editorial_literal, following_source)
            next_heading = re.search(r"^[ \t]*#{1,6}[ \t]+", caption_source, re.MULTILINE)
            if next_heading is not None:
                caption_source = caption_source[:next_heading.start()]
            caption_texts = [concept_label(paragraph) for paragraph in caption_source.split("\n\n")]
            assert any(re.match(rf"{label}\s+{number}\s*:", text) for text in caption_texts), (
                f"{context}: {label} needs a matching numbered caption before the next media item or section"
            )
        reference = f"[{label} {number}](#{anchor})"
        preceding_source = source[:media.start()].rstrip()
        introduction = preceding_source.rsplit("\n\n", 1)[-1]
        assert reference in introduction, (
            f"{context}: the leading sentence must link to {reference}"
        )
        assert introduction.endswith((".", "!", "?")), (
            f"{context}: the introduction to {reference} must end as a "
            "sentence, not with a colon"
        )


def asterisk_emphasis_matches(source: str) -> list[re.Match[str]]:
    """Find emphasis delimiters without treating literal code as prose."""
    prose = MARKDOWN_LITERAL_PATTERN.sub(
        lambda match: re.sub(r"[^\n]", "x", match.group(0)), source,
    )
    return list(ASTERISK_EMPHASIS_PATTERN.finditer(prose))


def assert_markdown_formatting(source: str, context: str = "Markdown") -> None:
    """Require underscore emphasis, ASCII typography, and ASCII figures."""
    assert not asterisk_emphasis_matches(source), (
        f"{context}: use _ for italic and __ for bold, not asterisk emphasis"
    )
    decoded_source = unescape(source)
    disallowed = NON_ASCII_STYLE_PATTERN.search(decoded_source)
    assert disallowed is None, (
        f"{context}: use ASCII instead of Unicode arrows, line graphics, "
        f"smart punctuation, decorative symbols, or invisible spacing "
        f"(U+{ord(disallowed.group(0)):04X})"
    )
    figures = re.finditer(r"<figure\b[^>]*>.*?</figure>", source, re.DOTALL)
    for figure in figures:
        figure_source = figure.group(0)
        entities = re.finditer(
            r"&(?:#(?:[xX][0-9a-fA-F]+|\d+)|[A-Za-z][A-Za-z0-9]*);?",
            figure_source,
        )
        for entity in entities:
            decoded_entity = unescape(entity.group(0))
            assert not decoded_entity.startswith(("<", ">")), (
                f"{context}: use literal > and < in figures, not HTML entities"
            )
        decoded_figure = unescape(figure_source)
        assert decoded_figure.isascii(), (
            f"{context}: figures must contain only ASCII characters"
        )


@pytest.mark.parametrize(
    "source",
    [
        "_italic_ and __bold__ and ___both___",
        "`*args` and `**kwargs` and `*.py`",
        "``literal `*text*` ``",
        "```python\nresult = value * factor\n# **literal**\n```\n",
        "~~~text\n*not emphasis*\n~~~~\n",
        r"\*literal\* and \*\*literal\*\*",
        "* list item\n\n***\n",
        "$a*b*c$ and $$x**2$$",
        "<figure><pre>*literal* <--> **literal**</pre></figure>",
        "<figure><pre>a > b < c &amp; d &#38; e &quot;quoted&quot;</pre></figure>",
        "Scientific prose: \u03b1 at 30\u00b0 is allowed outside figures.",
        "ASCII diagram: +---+ -> next <- previous <-> peer",
    ],
)
def test_markdown_formatting_accepts_literal_content(source: str) -> None:
    """Do not mistake code, equations, or literal asterisks for emphasis."""
    assert_markdown_formatting(source)


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("*italic*", "asterisk emphasis"),
        ("**bold**", "asterisk emphasis"),
        ("***both***", "asterisk emphasis"),
        ("****nested bold****", "asterisk emphasis"),
        ("**bold `command` text**", "asterisk emphasis"),
        ("<figure><pre>a &gt; b</pre></figure>", "literal > and <"),
        ("<figure><pre>a &lt; b</pre></figure>", "literal > and <"),
        ("<figure><pre>a &GT; b &LT; c</pre></figure>", "literal > and <"),
        ("<figure><pre>a &#62; b</pre></figure>", "literal > and <"),
        ("<figure><pre>a &#60; b</pre></figure>", "literal > and <"),
        ("<figure><pre>a &#x3c; b</pre></figure>", "literal > and <"),
        ("<figure><pre>a &#x3e; b</pre></figure>", "literal > and <"),
        ("<figure><pre>a &#X003C; b</pre></figure>", "literal > and <"),
        ("<figure><pre>a &#00062; b</pre></figure>", "literal > and <"),
        ("<figure><pre>a &#62 b</pre></figure>", "literal > and <"),
        ("<figure><pre>a &#x3c b</pre></figure>", "literal > and <"),
        ("<figure><pre>a &gt b</pre></figure>", "literal > and <"),
        ("<figure><pre>a \u03b1 b</pre></figure>", "ASCII"),
        ("<figure><pre>a &#8594; b</pre></figure>", "ASCII"),
        ("<figure><figcaption>\u201cCaption\u201d</figcaption></figure>", "ASCII"),
        ("images \u2192 layers", "ASCII"),
        ("```text\nclient \u2500\u2500> daemon\n```\n", "ASCII"),
        ("```text\n\u2514\u2500 file\n```\n", "ASCII"),
        ("a &rarr; b", "ASCII"),
        ("a &#x2192; b", "ASCII"),
        ("\u201csmart quotes\u201d", "ASCII"),
        ("Docker\u2019s daemon", "ASCII"),
        ("word\u2014word", "ASCII"),
        ("word\u2026", "ASCII"),
        ("\u2713 complete", "ASCII"),
        ("\U0001f680 ready", "ASCII"),
        ("hidden\u200bspace", "ASCII"),
        ("nonbreaking\u00a0space", "ASCII"),
    ],
)
def test_markdown_formatting_rejects_disallowed_forms(
    source: str, message: str,
) -> None:
    """Reject each requested formatting violation independently."""
    with pytest.raises(AssertionError, match=message):
        assert_markdown_formatting(source)


def test_notebook_markdown_formatting() -> None:
    """Apply the formatting contract to every notebook Markdown cell."""
    for notebook_path in sorted(NOTEBOOK_DIR.glob("*.ipynb")):
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        for number, cell in enumerate(notebook["cells"], start=1):
            if cell["cell_type"] == "markdown":
                source = cell_source(cell)
                context = f"{notebook_path.name}, Cell {number}"
                assert_markdown_formatting(source, context)


def notebook_markdown_source(notebook: dict[str, Any]) -> str:
    """Read presentation and lesson Markdown in notebook order."""
    markdown_sources = [
        cell_source(cell)
        for cell in notebook["cells"]
        if cell["cell_type"] == "markdown"
    ]
    return "\n".join(markdown_sources)


def assert_markdown_ends_with_one_newline(cell: dict[str, Any]) -> None:
    """Require Markdown cell source to end without blank or space-only tails."""
    source = cell["source"]
    text = "".join(source) if isinstance(source, list) else source
    assert text.endswith("\n")
    assert not text.endswith("\n\n")
    assert not text.endswith(" \n")


def assert_try_it_sections(source: str) -> None:
    """Require each activity to stay inside a parent section with its result."""
    activity_headings = list(TRY_IT_HEADING_PATTERN.finditer(source))
    if not activity_headings:
        return

    section_headings = list(SECTION_HEADING_PATTERN.finditer(source))
    checkpoint_index = source.index("## Checkpoint")
    for index, activity_heading in enumerate(activity_headings):
        assert activity_heading.start() < checkpoint_index
        parent_headings = [
            heading
            for heading in section_headings
            if heading.start() < activity_heading.start()
            and not TRY_IT_HEADING_PATTERN.fullmatch(heading.group(0))
        ]
        assert parent_headings
        next_heading_start = next(
            (
                heading.start()
                for heading in section_headings
                if heading.start() > activity_heading.start()
            ),
            checkpoint_index,
        )
        activity_end = min(
            next_heading_start,
            (
                activity_headings[index + 1].start()
                if index + 1 < len(activity_headings)
                else checkpoint_index
            ),
        )
        activity_source = source[activity_heading.end() : activity_end]
        assert "<details>" in activity_source
        assert "</details>" in activity_source


def assert_final_checkpoint_tail(notebook: dict[str, Any]) -> None:
    """Require the standard final Further reading and checkpoint structure."""
    final_markdown = notebook["cells"][-2]
    assert final_markdown["cell_type"] == "markdown"
    source = cell_source(final_markdown)
    checkpoint_index = source.rfind("## Checkpoint\n")
    assert checkpoint_index >= 0
    assert source[checkpoint_index:] == CHECKPOINT_TAIL
    headings = re.findall(r"(?m)^## .+$", source[:checkpoint_index])
    assert headings[-1] == "## Further reading"


def checkpoint_data_path(notebook_name: str) -> Path:
    """Return the sidecar path implied by one numbered notebook name."""
    _, _, checkpoint_name = notebook_name.partition("-")
    return (
        CHECKPOINT_DATA_DIR / f"{checkpoint_name.removesuffix('.ipynb')}.json"
    )


def vscode_heading_fragment(heading: str) -> str:
    """Return the fragment assigned to an ASCII Markdown heading by VS Code."""
    normalized_heading = re.sub(r"\s+", "-", heading.strip().lower())
    return "".join(
        character
        for character in normalized_heading
        if character not in VSCODE_HEADING_PUNCTUATION
    ).strip("-")


def assert_reveal_self_check(notebook_name: str) -> None:
    """Check one interactive checkpoint without embedding its data in a notebook."""
    notebook_path = NOTEBOOK_DIR / notebook_name
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    markdown_source = notebook_markdown_source(notebook)
    code_source = cell_source(notebook["cells"][-1])
    checkpoint_data = json.loads(
        checkpoint_data_path(notebook_name).read_text(encoding="utf-8"),
    )

    assert set(checkpoint_data) == {"checkpoints"}
    assert code_source.splitlines() == CHECKPOINT_CODE_SOURCE
    assert (
        "Write or select a response before revealing the answer."
        in markdown_source
    )

    checkpoints = checkpoint_data["checkpoints"]
    assert isinstance(checkpoints, list) and checkpoints
    checkpoint_ids = set()
    for checkpoint in checkpoints:
        assert isinstance(checkpoint, dict)
        required_fields = {"id", "question", "model_answer", "evidence"}
        if "choices" in checkpoint:
            assert set(checkpoint) == required_fields | {
                "choices",
                "correct_choice",
            }
            choices = checkpoint["choices"]
            correct_choice = checkpoint["correct_choice"]
            assert isinstance(choices, list) and len(choices) >= 2
            assert len(choices) == len(set(choices))
            assert all(
                isinstance(choice, str) and choice.strip()
                for choice in choices
            )
            assert (
                isinstance(correct_choice, str) and correct_choice in choices
            )
        else:
            assert set(checkpoint) == required_fields

        checkpoint_id = checkpoint["id"]
        question = checkpoint["question"]
        model_answer = checkpoint["model_answer"]
        evidence = checkpoint["evidence"]
        assert isinstance(checkpoint_id, str) and checkpoint_id
        assert isinstance(question, str) and question
        assert isinstance(model_answer, str) and model_answer
        assert isinstance(evidence, list) and evidence
        assert question not in markdown_source
        assert model_answer not in markdown_source
        assert checkpoint_id not in checkpoint_ids
        checkpoint_ids.add(checkpoint_id)

        for evidence_item in evidence:
            assert set(evidence_item) == {"label", "anchor"}
            source_section = evidence_item["label"]
            anchor = evidence_item["anchor"]
            assert isinstance(source_section, str) and source_section
            assert isinstance(anchor, str) and anchor.startswith("#")
            assert f"## {source_section}" in markdown_source
            assert anchor == f"#{vscode_heading_fragment(source_section)}"


def test_notebook_cells_have_consistent_metadata() -> None:
    """Keep the granular notebook set usable in the editor."""
    expected_paths = {
        NOTEBOOK_DIR / notebook_name for notebook_name in REQUIRED_NOTEBOOKS
    }
    assert set(NOTEBOOK_DIR.glob("*.ipynb")) == expected_paths

    for notebook_name, expected_heading in REQUIRED_NOTEBOOKS.items():
        notebook_path = NOTEBOOK_DIR / notebook_name
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        assert notebook["nbformat"] == 4
        code_cells = [
            cell for cell in notebook["cells"] if cell["cell_type"] == "code"
        ]
        assert len(code_cells) == 1

        for cell in notebook["cells"]:
            assert cell["cell_type"] in {"markdown", "code"}
            assert isinstance(cell["metadata"], dict)
            assert isinstance(cell["id"], str) and cell["id"]
            if "id" in cell["metadata"]:
                assert cell["id"] == cell["metadata"]["id"]
            else:
                assert cell["cell_type"] == "markdown"
                presentation_source = cell_source(cell)
                assert presentation_source.startswith(
                    ("<style>\n", '<p align="center">\n')
                )
                assert re.search(r"^# ", presentation_source, re.MULTILINE) is None
            if cell["cell_type"] == "markdown":
                assert cell["metadata"]["language"] == "markdown"
                assert_markdown_ends_with_one_newline(cell)

        markdown_cell = notebook["cells"][0]
        assert markdown_cell["cell_type"] == "markdown"
        assert markdown_cell["metadata"]["language"] == "markdown"
        source = notebook_markdown_source(notebook)
        logo_index = source.index('src="../assets/images/dtlogo.png"')
        first_h1_index = source.index(expected_heading)
        assert logo_index < first_h1_index

        markdown_headings = [
            line for line in source.splitlines() if line.startswith("# ")
        ]
        assert markdown_headings[0] == expected_heading
        assert_try_it_sections(source)

        code_cell = notebook["cells"][-1]
        assert code_cell["cell_type"] == "code"
        assert code_cell["metadata"]["language"] == "python"
        assert_final_checkpoint_tail(notebook)


def test_presentation_blocks_use_standalone_markdown_cells() -> None:
    """Keep logos and stylesheet definitions separate from lesson Markdown."""
    expected_logo = (
        '<p align="center">\n'
        '<a href="https://duckietown.com"><img src="../assets/images/dtlogo.png" '
        'alt="Duckietown Logo" width="50%"></a>\n'
        '</p>\n'
    )
    for notebook_name, expected_heading in REQUIRED_NOTEBOOKS.items():
        notebook_path = NOTEBOOK_DIR / notebook_name
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        markdown_sources = [
            cell_source(cell)
            for cell in notebook["cells"]
            if cell["cell_type"] == "markdown"
        ]
        assert markdown_sources[0] == expected_logo
        lesson_index = 1
        if markdown_sources[1].startswith("<style>\n"):
            style_source = markdown_sources[1]
            assert PRESENTATION_STYLE.fullmatch(style_source[:-1])
            lesson_index = 2
        lesson_source = markdown_sources[lesson_index]
        assert lesson_source.startswith(f"{expected_heading}\n")
        for source in markdown_sources[lesson_index:]:
            assert "<style>" not in source
            assert 'src="../assets/images/dtlogo.png"' not in source


@pytest.mark.parametrize("kind", ["figure", "table"])
@pytest.mark.parametrize("markup", ["semantic", "mathjax"])
@pytest.mark.parametrize("number", ["1", "23"])
@pytest.mark.parametrize("caption_label", ["{label} {number}", "<strong>{label} {number}</strong>"])
def test_media_introductions_accept_linked_sentences(
    kind: str, markup: str, number: str, caption_label: str,
) -> None:
    """Accept matching numbers in both semantic and MathJax-safe media."""
    label = kind.capitalize()
    caption_label = caption_label.format(label=label, number=number)
    source = f"The comparison appears in [{label} {number}](#{kind}-{number}).\n\n"
    if markup == "semantic":
        caption_tag = "caption" if kind == "table" else "figcaption"
        source += (
            f'<{kind} id="{kind}-{number}">'
            f"<{caption_tag}>{caption_label}: Comparison.</{caption_tag}></{kind}>"
        )
    else:
        source += (
            f'<a id="{kind}-{number}"></a>\n\n'
            '<p class="lx-figure"><img alt="Comparison"></p>\n\n'
            f"{caption_label}: Comparison.\n"
        )
    assert_media_introductions(source)


@pytest.mark.parametrize("kind", ["figure", "table"])
@pytest.mark.parametrize("markup", ["semantic", "mathjax"])
@pytest.mark.parametrize(
    ("introduction", "error"),
    [
        ("The comparison follows.", "leading sentence must link"),
        ("See [{label} 1](#{kind}-2).", "leading sentence must link"),
        ("See [{label} 1](#{kind}-1):", "sentence, not with a colon"),
    ],
)
def test_media_introductions_reject_missing_links_and_colons(
    kind: str, markup: str, introduction: str, error: str,
) -> None:
    """Reject unlinked introductions, wrong targets, and colon-only lead-ins."""
    label = kind.capitalize()
    introduction = introduction.format(label=label, kind=kind)
    source = f"{introduction}\n\n"
    if markup == "semantic":
        caption_tag = "caption" if kind == "table" else "figcaption"
        source += (
            f'<{kind} id="{kind}-1">'
            f"<{caption_tag}>{label} 1: Comparison.</{caption_tag}></{kind}>"
        )
    else:
        source += f'<a id="{kind}-1"></a>\n\n{label} 1: Comparison.\n'
    with pytest.raises(AssertionError, match=error):
        assert_media_introductions(source)


@pytest.mark.parametrize("kind", ["figure", "table"])
@pytest.mark.parametrize("anchor", ["foo", "{kind}-foo", "{kind}-0", "{kind}-01", "other-1"])
def test_media_introductions_reject_invalid_numbered_anchors(kind: str, anchor: str) -> None:
    label = kind.capitalize()
    anchor = anchor.format(kind=kind)
    number = anchor.rsplit("-", 1)[-1]
    source = f'See [{label} {number}](#{anchor}).\n\n<{kind} id="{anchor}"></{kind}>'
    with pytest.raises(AssertionError, match=r"positive .* anchor"):
        assert_media_introductions(source)


@pytest.mark.parametrize("kind", ["figure", "table"])
@pytest.mark.parametrize(
    ("caption", "error"),
    [
        ("", "needs a numbered"),
        ("<wrong>Wrong caption element.</wrong>", "needs a numbered"),
        ("<{caption_tag}></{caption_tag}>", "must start with"),
        ("<{caption_tag}>A comparison.</{caption_tag}>", "must start with"),
        ("<{caption_tag}>{label} 2: Comparison.</{caption_tag}>", "must start with"),
        ("<{caption_tag}>Other 1: Comparison.</{caption_tag}>", "must start with"),
    ],
)
def test_media_introductions_reject_missing_and_mismatched_captions(
    kind: str, caption: str, error: str,
) -> None:
    label = kind.capitalize()
    caption_tag = "caption" if kind == "table" else "figcaption"
    caption = caption.format(caption_tag=caption_tag, label=label)
    source = f'See [{label} 1](#{kind}-1).\n\n<{kind} id="{kind}-1">{caption}</{kind}>'
    with pytest.raises(AssertionError, match=error):
        assert_media_introductions(source)


@pytest.mark.parametrize("kind", ["figure", "table"])
@pytest.mark.parametrize("anchor", ["{kind}-", "{kind}-foo", "{kind}-0", "{kind}-01"])
def test_media_introductions_reject_invalid_mathjax_anchors(kind: str, anchor: str) -> None:
    label = kind.capitalize()
    anchor = anchor.format(kind=kind)
    number = anchor.rsplit("-", 1)[-1]
    source = f'See [{label} {number}](#{anchor}).\n\n<a id="{anchor}"></a>'
    with pytest.raises(AssertionError, match=r"positive .* anchor"):
        assert_media_introductions(source)


@pytest.mark.parametrize("kind", ["figure", "table"])
@pytest.mark.parametrize(
    "following",
    [
        "",
        "{label} 2: Wrong number.",
        "```text\n{label} 1: A literal example.\n```",
        "<pre>{label} 1: A literal example.</pre>",
        "## Another section\n\n{label} 1: Unrelated caption.",
        'See [{label} 1](#{kind}-1).\n\n<a id="{kind}-1"></a>\n\n{label} 1: A later caption.',
    ],
)
def test_media_introductions_reject_missing_mathjax_captions(kind: str, following: str) -> None:
    label = kind.capitalize()
    following = following.format(label=label, kind=kind)
    source = f'See [{label} 1](#{kind}-1).\n\n<a id="{kind}-1"></a>\n\n{following}'
    with pytest.raises(AssertionError, match="matching numbered caption"):
        assert_media_introductions(source)


def test_notebook_media_introductions() -> None:
    """Introduce every notebook figure and table with a directly linked sentence."""
    for notebook_path in sorted(NOTEBOOK_DIR.glob("*.ipynb")):
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        for cell_number, cell in enumerate(notebook["cells"], 1):
            if cell["cell_type"] == "markdown":
                source = cell_source(cell)
                context = f"{notebook_path}: Cell {cell_number}"
                assert_media_introductions(source, context)


def test_tables_and_figures_use_shared_presentation_style() -> None:
    """Keep shared styling and cell-local alignment consistent across viewers."""
    styled_notebooks = 0
    table_count = 0
    figure_count = 0

    for notebook_path in sorted(NOTEBOOK_DIR.glob("*.ipynb")):
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        source = notebook_markdown_source(notebook)
        tables = TABLE_PATTERN.findall(source)
        figures = FIGURE_PATTERN.findall(source)

        if tables or figures:
            styled_notebooks += 1
            assert PRESENTATION_STYLE.search(source)
        else:
            assert "<style>" not in source

        for attributes in tables:
            assert 'class="lx-table"' in attributes
            assert 'style="margin:1.5em auto; text-align:left;"' in attributes
        for attributes in figures:
            assert 'class="lx-figure"' in attributes
            assert 'style="margin:1.5em auto; text-align:center;"' in attributes
        for tag, attributes in CAPTION_PATTERN.findall(source):
            if tag == "caption":
                expected_style = (
                    "caption-side:top; font-size:0.9em; "
                    "margin-bottom:0.6em; text-align:center;"
                )
            else:
                expected_style = (
                    "font-size:0.9em; margin-top:0.6em; text-align:center;"
                )
            assert f'style="{expected_style}"' in attributes

        table_count += len(tables)
        figure_count += len(figures)

    assert styled_notebooks == 5
    assert table_count == 2
    assert figure_count == 6


def test_numbered_notebook_references_are_individually_linked() -> None:
    """Keep numbered course references direct and individually actionable."""
    readme_source = README_PATH.read_text(encoding="utf-8")
    learner_sources = {README_PATH: readme_source}

    for notebook_name in REQUIRED_NOTEBOOKS:
        notebook_path = NOTEBOOK_DIR / notebook_name
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        markdown_source = notebook_markdown_source(notebook)
        learner_sources[notebook_path] = markdown_source

        notebook_number = notebook_name.partition("-")[0]
        expected_link = f"[Notebook {notebook_number}](./notebooks/{notebook_name})"
        assert expected_link in readme_source

    for learner_path, learner_source in learner_sources.items():
        assert (
            UNLINKED_NOTEBOOK_REFERENCE_PATTERN.search(learner_source) is None
        ), learner_path


def test_cross_lx_references_use_clear_linked_titles() -> None:
    """Keep external LX links clear and introductions concise."""
    readme_source = README_PATH.read_text(encoding="utf-8")
    expected_readme_link = (
        f"[{LINUX_NETWORKING_LX_TITLE}]"
        f"({LINUX_NETWORKING_LX_URL})"
    )
    assert expected_readme_link in readme_source

    data_paths_path = NOTEBOOK_DIR / "2-ros-2-data-paths-and-duckiedrone-integration.ipynb"
    data_paths = json.loads(data_paths_path.read_text(encoding="utf-8"))
    data_paths_source = notebook_markdown_source(data_paths)
    expected_imu_link = (
        f"[{IMU_SENSORS_LX_TITLE}]"
        f"({IMU_SENSORS_LX_URL})"
    )
    expected_tof_link = (
        f"[{TOF_SENSORS_LX_TITLE}]"
        f"({TOF_SENSORS_LX_URL})"
    )
    assert expected_imu_link in data_paths_source
    assert expected_tof_link in data_paths_source

    inspection_path = NOTEBOOK_DIR / "8-inspect-a-duckiedrone-ros-2-graph.ipynb"
    inspection = json.loads(inspection_path.read_text(encoding="utf-8"))
    inspection_source = notebook_markdown_source(inspection)
    expected_inspection_link = (
        f"[{LINUX_NETWORKING_NOTEBOOK_TITLE}]"
        f"({LINUX_NETWORKING_LX_URL})"
    )
    assert expected_inspection_link in inspection_source

    learner_sources = (
        readme_source,
        data_paths_source,
        inspection_source,
    )
    for learner_source in learner_sources:
        assert UNLINKED_CROSS_LX_REFERENCE_PATTERN.search(learner_source) is None


def test_checkpoint_data_matches_interactive_notebooks() -> None:
    """Keep every interactive ROS 2 notebook paired with one sidecar."""
    expected_paths = {
        checkpoint_data_path(notebook_name)
        for notebook_name in INTERACTIVE_CHECKPOINT_NOTEBOOKS
    }
    assert set(CHECKPOINT_DATA_DIR.glob("*.json")) == expected_paths

    for notebook_name in sorted(INTERACTIVE_CHECKPOINT_NOTEBOOKS):
        assert_reveal_self_check(notebook_name)


def test_shared_checkpoint_self_check_helper_is_valid() -> None:
    """Keep the reusable checkpoint implementation available and parseable."""
    helper_source = CHECKPOINT_SELF_CHECK_PATH.read_text(encoding="utf-8")
    ast.parse(helper_source, filename=str(CHECKPOINT_SELF_CHECK_PATH))

    for required_text in (
        "class CheckpointSelfCheck",
        "def load_checkpoint_definitions",
        "def render_model_answer",
        "def display_checkpoint_self_checks",
        "Checkbox",
        "Reveal answer",
        "Try again",
    ):
        assert required_text in helper_source


def test_model_answer_uses_compact_paragraph_spacing() -> None:
    """Keep wrapped model answers readable in the notebook renderer."""
    self_check = checkpoint_self_check.CheckpointSelfCheck(
        question_number=1,
        question="Question",
        checkpoint_id="checkpoint",
        checkpoint_data_relative_path=Path("checkpoint_data/checkpoint.json"),
    )

    model_answer_state = self_check.model_answer.get_state()
    assert "checkpoint-model-answer" in model_answer_state["_dom_classes"]
    assert (
        ".checkpoint-self-check .checkpoint-model-answer .widget-html-content p {"
        "line-height: 1.5;"
        "margin: 0 0 8px;"
        "}"
        in checkpoint_self_check.CHECKPOINT_WIDGET_STYLE
    )
    assert (
        ".checkpoint-self-check .checkpoint-model-answer .widget-html-content p:last-child {"
        "margin-bottom: 0;"
        "}"
        in checkpoint_self_check.CHECKPOINT_WIDGET_STYLE
    )

    self_check.answer.value = "Response"
    with patch.object(
        checkpoint_self_check,
        "load_model_answer",
        return_value=("Answer", [{"label": "Source", "anchor": "#source"}]),
    ):
        self_check.reveal_answer(self_check.reveal_button)

    assert self_check.model_answer.layout.display == ""
    assert "<strong>Model answer:</strong> Answer" in self_check.model_answer.value
    assert "<a href='#source'>Source</a>" in self_check.model_answer.value


def test_starter_nodes_are_valid_python() -> None:
    """Keep learner templates parseable before they are built in ROS 2."""
    node_paths = [
        PACKAGE_DIR / "ros2_pubsub" / "my_publisher.py",
        PACKAGE_DIR / "ros2_pubsub" / "my_subscriber.py",
    ]

    for node_path in node_paths:
        ast.parse(
            node_path.read_text(encoding="utf-8"), filename=str(node_path)
        )


def test_package_declares_its_ros_dependencies_and_executables() -> None:
    """Ensure the package stays buildable and launchable as the lesson evolves."""
    package_xml = ET.parse(PACKAGE_DIR / "package.xml")
    dependency_names = {
        dependency.text for dependency in package_xml.findall("depend")
    }
    assert {"rclpy", "std_msgs"}.issubset(dependency_names)

    setup_contents = (PACKAGE_DIR / "setup.py").read_text(encoding="utf-8")
    assert "my_publisher = ros2_pubsub.my_publisher:main" in setup_contents
    assert "my_subscriber = ros2_pubsub.my_subscriber:main" in setup_contents


def test_readme_has_shared_lx_structure() -> None:
    """Keep the README aligned with the reviewed LX structure."""
    readme = README_PATH.read_text(encoding="utf-8")
    assert "TODO" not in readme
    assert re.search(
        r"^# Learning Experience \(LX\): .+ on the Duckiedrone$",
        readme,
        re.MULTILINE,
    )
    assert "`Software: ente`; `Hardware: DD24-B`" in readme
    assert re.findall(r"^## .+$", readme, re.MULTILINE) == [
        "## Intended learning outcomes",
        "## Run this LX",
        "## Notebooks",
        "## Prerequisites",
        f"## Complete the {README_EXERCISE_TOPIC} exercise",
        "## Further reading",
        "## For LX authors",
    ]

    notebook_section = readme.split("## Notebooks\n", 1)[1].split("\n## ", 1)[0]
    assert "| # | Notebook | Description |\n| --- | --- | --- |" in notebook_section
    notebook_rows = re.findall(r"^\| \d+ \|.*\|$", notebook_section, re.MULTILINE)
    assert len(notebook_rows) == len(REQUIRED_NOTEBOOKS)
    for number, (notebook_name, row) in enumerate(
        zip(REQUIRED_NOTEBOOKS, notebook_rows, strict=True), start=1
    ):
        expected_prefix = (
            f"| {number} | [Notebook {number}](./notebooks/{notebook_name}) | "
        )
        assert row.startswith(expected_prefix)
        assert len(row.split("|")) == 5
        assert row.removeprefix(expected_prefix).strip(" |")

    prerequisite_section = readme.split("## Prerequisites\n", 1)[1].split(
        "\n## ", 1
    )[0]
    prerequisite_headings = re.findall(
        r"^### .+$", prerequisite_section, re.MULTILINE
    )
    assert len(prerequisite_headings) == 4
    assert prerequisite_headings[0] == "### Choose the terminal"
    assert prerequisite_headings[1] == (
        f"### {README_EXERCISE_TOPIC} foundations and local practice"
    )
    assert prerequisite_headings[-1] == "### Duckiedrone access"
    assert "python3 -m pytest tests/" in readme
    assert (
        "Interactive checkpoints require the notebook metadata supplied by "
        "`dts code editor` and a compatible Jupyter/IPython kernel with "
        "`ipywidgets` available"
        in readme
    )
