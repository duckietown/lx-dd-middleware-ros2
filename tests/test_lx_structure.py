"""Sanity tests for the ROS 2 publisher/subscriber starter package.

Run from the LX root with:

    pytest tests/

These tests validate notebook metadata and package structure without importing
the ROS runtime, so they can run both inside the editor container and on a plain
host Python.
"""

import ast
import json
import re
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"
PACKAGE_DIR = ROOT / "packages" / "ros2_pubsub"
CHECKPOINT_DATA_DIR = ROOT / "checkpoint_data"
CHECKPOINT_SELF_CHECK_PATH = ROOT / "packages" / "checkpoint_self_check.py"
VSCODE_HEADING_PUNCTUATION = "[]!/'\"#$%&()*+,./:;<=>?@\\^{}|~`"

REQUIRED_NOTEBOOKS = {
    "1-ros-2-foundations-and-architecture.ipynb": "# ROS 2 Foundations and Architecture",
    "2-ros-2-architecture-and-data-paths.ipynb": "# ROS 2 Architecture and Data Paths",
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


def cell_source(cell: dict[str, Any]) -> str:
    """Return a cell source regardless of its valid notebook representation."""
    source = cell["source"]
    if isinstance(source, list):
        if all(line.endswith("\n") for line in source[:-1]):
            return "".join(source)
        return "\n".join(source)
    return source


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

        markdown_cell = notebook["cells"][0]
        assert markdown_cell["cell_type"] == "markdown"
        assert markdown_cell["metadata"]["language"] == "markdown"
        assert cell_source(markdown_cell).splitlines()[0] == expected_heading

        code_cell = notebook["cells"][1]
        assert code_cell["cell_type"] == "code"
        assert code_cell["metadata"]["language"] == "python"


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
        "def display_checkpoint_self_checks",
        "Checkbox",
        "Reveal answer",
        "Try again",
    ):
        assert required_text in helper_source


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
