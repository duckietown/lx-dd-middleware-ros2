<p align="center">
<a href="https://duckietown.com"><img src="./assets/images/dtlogo.png" alt="Duckietown Logo" width="50%"></a>
</p>

# Learning Experience (LX): ROS 2 Middleware on the Duckiedrone

`Software: ente`; `Hardware for optional telemetry: DD24-B`

ROS 2 provides libraries and tools for organizing robotics applications as communicating nodes. This learning experience follows data through those interfaces, then connects graph observations to the Python code that publishes and receives messages.

The LX is intended for undergraduate engineering students with basic Python and terminal experience. No previous ROS 2 knowledge is required; an optional comparison supports readers familiar with ROS 1. Most activities use a dedicated local exercise environment, while Duckiedrone inspection is optional.

## Intended learning outcomes

After completing this LX, learners will be able to:

1. Explain nodes, topics, message types, services, actions, parameters, and the roles of client libraries and middleware.
2. Investigate discovery and resolved names using domains, namespaces, and private names.
3. Inspect, build, and source the supplied `ament_python` package and locate its installed executables.
4. Relate `rclpy` timers, executors, and callbacks to publisher and subscriber behavior, then modify the publisher's payload and rate.
5. Observe delivery, QoS settings, arrival rate, and timestamp-based message age to diagnose missing messages.
6. Reuse installed nodes with different node names and topic remappings.
7. Explain the DTPS and MAVROS data paths and optionally inspect a Duckiedrone's flight-controller state interface.

## Run this LX

The Duckietown Manual's [LX General Instructions](https://docs.duckietown.com/ente/opmanual-dd24/50-learning-experiences/lx-general-procedure.html) introduce the workflow. The setup below selects the ROS 2 environment needed by this LX.

## Notebooks

Follow the notebooks in order, skipping the optional Duckiedrone activity when hardware is unavailable. The source changes made in [Notebook 9](./notebooks/9-ros-2-node-lifecycles-and-publishers.ipynb) carry forward into the final two activities.

| # | Notebook | Content |
| --- | --- | --- |
| 1 | [Notebook 1](./notebooks/1-robot-operating-system-2-graph-and-software-layers.ipynb) | ROS 2 graph, interfaces, and software layers |
| 2 | [Notebook 2](./notebooks/2-ros-2-data-paths-and-duckiedrone-integration.ipynb) | DTPS, sensor bridges, and the PX4–MAVLink–MAVROS data path |
| 3 | [Notebook 3](./notebooks/3-ros-2-nodes-topics-and-interfaces.ipynb) | Discover a publisher and receive typed messages |
| 4 | [Notebook 4](./notebooks/4-ros-2-discovery-domains-and-names.ipynb) | Compare domains and resolve absolute, relative, and private names |
| 5 | [Notebook 5](./notebooks/5-ros-2-workspaces-and-packages.ipynb) | Inspect package files, dependencies, and executable entry points |
| 6 | [Notebook 6](./notebooks/6-build-and-discover-a-ros-2-package.ipynb) | Build the package, source its overlay, and check discovery |
| 7 | [Notebook 7](./notebooks/7-inspect-a-local-ros-2-graph.ipynb) | Inspect endpoints and QoS; measure arrival rate and message age |
| 8 | [Notebook 8](./notebooks/8-inspect-a-duckiedrone-ros-2-graph.ipynb) | Optional: inspect the Duckiedrone's MAVROS state topic |
| 9 | [Notebook 9](./notebooks/9-ros-2-node-lifecycles-and-publishers.ipynb) | ROS 2 Node Lifecycles and Anatomy of a Publisher: modify payload and rate |
| 10 | [Notebook 10](./notebooks/10-ros-2-subscribers-and-diagnosis.ipynb) | Run the subscriber and diagnose missing messages |
| 11 | [Notebook 11](./notebooks/11-ros-2-names-and-remapping.ipynb) | Give instances distinct names and remap both ends of a topic |

## Prerequisites

Complete the Duckietown Manual's [Initial Setup](https://docs.duckietown.com/ente/duckietown-manual/10-setup/setup-introduction.html) so Docker and the Duckietown Shell (`dts`) are available on the base station or in the Duckietown Workspace. A separate host installation of ROS 2 is unnecessary.

### Open the dedicated environment

From the LX checkout in a base-station or Workspace terminal:

```bash
dts code editor --username duckietown
```

The exercise recipe supplies the ROS 2 Jazzy editor environment and prepares the build directories for the editor user.

Once the editor opens, select __Terminal > New Terminal__ for local `ros2` and `colcon` commands. Additional terminals opened through that menu share the exercise container.

### Choose the terminal

| Task | Execution environment |
| --- | --- |
| Start the editor | Base-station or Duckietown Workspace terminal |
| Build packages and run local ROS 2 experiments | Integrated terminals in the dedicated editor |
| Connect to a Duckiedrone and list its containers | Base-station connection followed by the Duckiedrone shell |
| Inspect Duckiedrone ROS 2 telemetry | The `ros2-mavros` shell entered in [Notebook 8](./notebooks/8-inspect-a-duckiedrone-ros-2-graph.ipynb) |

The editor supplies `ros2`, `colcon`, and `COLCON_WS=/code`. [Notebook 7](./notebooks/7-inspect-a-local-ros-2-graph.ipynb) and the subscriber and remapping activities use three terminals. Each notebook identifies which process runs in each terminal and when it should be stopped.

### Interactive checkpoints

Each notebook ends with an interactive self-check. Select a compatible Python kernel in the supplied editor and run the checkpoint cell. A response must be entered or selected before the answer can be revealed; “Try again” clears the response.

The helper uses the notebook path included in the editor's execution context to select its question file. It also requires Jupyter/IPython and `ipywidgets`. This execution context is distinct from the machine-specific interpreter metadata removed from the saved notebooks.

### Optional Duckiedrone inspection

[Notebook 8](./notebooks/8-inspect-a-duckiedrone-ros-2-graph.ipynb) requires a Duckiedrone with the ROS 2 stack running. Its connection procedure builds on the [Learning Experience (LX): Linux and Networking on the Duckiedrone](https://github.com/duckietown/lx-dd-linux-and-networking). The activity inspects telemetry inside `ros2-mavros`; subsequent publisher and subscriber exercises return to the dedicated local environment.

## Complete the ROS 2 exercise

[Notebook 5](./notebooks/5-ros-2-workspaces-and-packages.ipynb) introduces the supplied package, and [Notebook 6](./notebooks/6-build-and-discover-a-ros-2-package.ipynb) explains the first build. The following is a reference for rebuilding after saved source changes.

Starting in the LX checkout inside the editor:

```bash
source /opt/ros/${ROS2_DISTRO}/setup.bash
LX_DIR="$PWD"
cd "$COLCON_WS"
colcon build --base-paths "$LX_DIR/packages" --packages-select ros2_pubsub
source install/setup.bash
```

The build summary should report that `ros2_pubsub` finished successfully. Scoping discovery to the checkout avoids including another package copy elsewhere in the workspace.

In every additional exercise terminal:

```bash
source /opt/ros/${ROS2_DISTRO}/setup.bash
source "$COLCON_WS/install/setup.bash"
```

Sourcing normally produces no output. It makes the installed package available to that shell; source changes require rebuilding and restarting the affected node.

## Troubleshooting

### A publisher runs, but the node listing is empty

Confirm that the terminals belong to the same exercise environment and compare their `ROS_DOMAIN_ID` and `RMW_IMPLEMENTATION` settings. Then allow a fresh discovery window:

```bash
ros2 node list --no-daemon --spin-time 5
```

If direct discovery finds the publisher while the ordinary listing remains empty, restart the CLI's discovery helper from the same learner account and ROS 2 environment:

```bash
ros2 daemon stop
ros2 node list
```

The next query starts the helper again. This refreshes the observation state without establishing a particular underlying middleware fault. Avoid mixing privileged and ordinary-user inspection sessions.

### The package cannot be found

Check that the scoped build succeeded, then source `"$COLCON_WS/install/setup.bash"` in the terminal reporting the error. Check the selected installation with:

```bash
ros2 pkg prefix ros2_pubsub
```

In the prepared workspace, the expected prefix is `/code/install/ros2_pubsub`. [Notebook 6](./notebooks/6-build-and-discover-a-ros-2-package.ipynb) explains recovery and the specific byte-compilation warnings that can accompany a successful build.

## Further reading

Each notebook's `Further reading` section is the primary reference for its lesson. This guide groups the course's sources:

- __ROS 2 concepts and tools:__ the [ROS 2 Jazzy documentation](https://docs.ros.org/en/jazzy/).

- __Data transport:__ the [Duckietown Postal Service documentation](https://docs.duckietown.com/ente/duckietown-manual/04-software-tools/duckietown-postal-service-dtps.html) and [Zenoh documentation](https://zenoh.io/docs/overview/what-is-zenoh/).

- __Flight-controller integration:__ the [MAVLink Guide](https://mavlink.io/), [MAVROS documentation](https://github.com/mavlink/mavros), and [PX4 Guide](https://docs.px4.io/main/).

- __Duckiedrone setup and operation:__ the [Duckiedrone DD24 manual](https://docs.duckietown.com/ente/opmanual-dd24/).

## For LX authors

Learner material is in `notebooks/` and `packages/`; questions and answers are in `checkpoint_data/`. The companion recipe repository owns the exercise image. Local recipe development can use `dts code editor --recipe /absolute/path/to/lx-dd-middleware-ros2-recipe`, keeping author-specific paths outside the learner procedure.

From the LX root in an environment containing `pytest`, `IPython`, and `ipywidgets`, run:

```bash
python3 -m pytest tests/
```

These checks cover notebook structure, links, portable metadata, package files, and checkpoint behavior. They do not replace ROS 2 runtime verification or visual inspection in the editor.
