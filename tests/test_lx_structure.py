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
from importlib import import_module
from pathlib import Path
from typing import Any
from unittest.mock import patch
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"
PACKAGE_DIR = ROOT / "packages" / "ros2_pubsub"
README_PATH = ROOT / "README.md"
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
LINUX_NETWORKING_LX_URL = "https://github.com/duckietown/lx-dd-linux-and-networking"
IMU_SENSORS_LX_TITLE = "Duckiedrone IMU Sensors - Learning Experience"
IMU_SENSORS_LX_URL = "https://github.com/duckietown/lx-dd-sensors-imu-solution"
TOF_SENSORS_LX_TITLE = "Duckiedrone ToF Sensors - Learning Experience"
TOF_SENSORS_LX_URL = "https://github.com/duckietown/lx-dd-sensors-tof-solution"
UNLINKED_CROSS_LX_REFERENCE_PATTERN = re.compile(
    r"\b(?:Linux and )?Networking LX\b|\bsensor LXs?\b",
    re.IGNORECASE,
)

REQUIRED_NOTEBOOKS = {
    "1-ros-2-graph-and-software-layers.ipynb": "# ROS 2 Graph and Software Layers",
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
CAPTION_PATTERN = re.compile(r"<(?:caption|figcaption)\b(?P<attrs>[^>]*)>")


def cell_source(cell: dict[str, Any]) -> str:
    """Return a cell source regardless of its valid notebook representation."""
    source = cell["source"]
    if isinstance(source, list):
        return "".join(
            line if line.endswith("\n") else f"{line}\n"
            for line in source
        )
    return source


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
    markdown_source = cell_source(notebook["cells"][0])
    code_source = cell_source(notebook["cells"][1])
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
        assert len(notebook["cells"]) == 2

        for cell in notebook["cells"]:
            assert isinstance(cell["metadata"], dict)
            assert isinstance(cell["id"], str) and cell["id"]
            assert cell["metadata"]["id"] == cell["id"]
            if cell["cell_type"] == "markdown":
                assert_markdown_ends_with_one_newline(cell)

        markdown_cell = notebook["cells"][0]
        assert markdown_cell["cell_type"] == "markdown"
        assert markdown_cell["metadata"]["language"] == "markdown"
        source = cell_source(markdown_cell)
        logo_index = source.index('src="../assets/images/dtlogo.png"')
        first_h1_index = source.index(expected_heading)
        assert logo_index < first_h1_index

        markdown_headings = [
            line for line in source.splitlines() if line.startswith("# ")
        ]
        assert markdown_headings[0] == expected_heading
        assert_try_it_sections(source)

        code_cell = notebook["cells"][1]
        assert code_cell["cell_type"] == "code"
        assert code_cell["metadata"]["language"] == "python"
        assert_final_checkpoint_tail(notebook)


def test_tables_and_figures_use_shared_presentation_style() -> None:
    """Keep table and figure layout on the canonical shared CSS contract."""
    styled_notebooks = 0
    table_count = 0
    figure_count = 0

    for notebook_path in sorted(NOTEBOOK_DIR.glob("*.ipynb")):
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        source = cell_source(notebook["cells"][0])
        tables = TABLE_PATTERN.findall(source)
        figures = FIGURE_PATTERN.findall(source)

        if tables or figures:
            styled_notebooks += 1
            assert PRESENTATION_STYLE.search(source)
        else:
            assert "<style>" not in source

        for attributes in tables:
            assert 'class="lx-table"' in attributes
        for attributes in figures:
            assert 'class="lx-figure"' in attributes
        for attributes in CAPTION_PATTERN.findall(source):
            assert "style=" not in attributes

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
        markdown_source = cell_source(notebook["cells"][0])
        learner_sources[notebook_path] = markdown_source

        notebook_number = notebook_name.partition("-")[0]
        expected_link = f"[Notebook {notebook_number}](./notebooks/{notebook_name})"
        assert expected_link in readme_source

    for learner_path, learner_source in learner_sources.items():
        assert (
            UNLINKED_NOTEBOOK_REFERENCE_PATTERN.search(learner_source) is None
        ), learner_path


def test_cross_lx_references_use_full_linked_titles() -> None:
    """Keep external learning-experience references clear and actionable."""
    readme_source = README_PATH.read_text(encoding="utf-8")
    expected_readme_link = (
        f"[{LINUX_NETWORKING_LX_TITLE}]"
        f"({LINUX_NETWORKING_LX_URL})"
    )
    assert expected_readme_link in readme_source

    data_paths_path = NOTEBOOK_DIR / "2-ros-2-data-paths-and-duckiedrone-integration.ipynb"
    data_paths = json.loads(data_paths_path.read_text(encoding="utf-8"))
    data_paths_source = cell_source(data_paths["cells"][0])
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
    inspection_source = cell_source(inspection["cells"][0])
    expected_inspection_link = (
        f"[{LINUX_NETWORKING_LX_TITLE}]"
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


def test_readme_documents_test_and_checkpoint_requirements() -> None:
    """Keep the author test command and external checkpoint needs usable."""
    readme = README_PATH.read_text(encoding="utf-8")

    assert "python3 -m pytest tests/" in readme
    assert (
        "Interactive checkpoints require the notebook metadata supplied by "
        "`dts code editor`"
        in readme
    )
    assert (
        "compatible Jupyter/IPython kernel with `ipywidgets` available is "
        "not sufficient by itself"
        in readme
    )
