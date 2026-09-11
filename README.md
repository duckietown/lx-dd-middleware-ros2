<p align="center">
<a href="https://duckietown.com"><img src="./assets/images/dtlogo.png" alt="Duckietown Logo" width="50%"></a>
</p>

# Learning Experience (LX): ROS 2 Middleware on the Duckiedrone

`Software: ente`; `Hardware: DD24-B`

Robot Operating System 2 (ROS 2) helps a robot divide work among small, independent programs that communicate through a shared graph. In this learning experience (LX), you will learn the ROS 2 concepts and command-line tools behind that graph, then build and run your own Python publisher and subscriber.

## Intended learning outcomes

After completing this learning experience, learners will be able to:

1. Describe the ROS 2 graph, client-library, and middleware layers, and explain how nodes, topics, messages, services, and parameters fit together in a robot.

2. Explain how ROS 2 discovery and `ROS_DOMAIN_ID` let nodes communicate without a Robot Operating System 1 (ROS 1) master.

3. Create, build, source, and inspect an `ament_python` ROS 2 package with `colcon` and `ros2`.

4. Write and run Python publisher and subscriber nodes with `rclpy` and `std_msgs/msg/String`.

5. Explain how the Duckietown Postal Service (DTPS), ROS 2 bridges, and the MAVROS bridge between the flight controller and ROS 2 make sensor data from a current Duckiedrone visible to application nodes.

## Notebooks

Start with Notebook 1 before the Duckiedrone-specific architecture or ROS 2 commands. The remaining notebooks can be assigned individually when their listed prerequisites are available:

| # | Notebook | Outcome | Prerequisites |
| --- | --- | --- | --- |
| 1 | `1-ros-2-graph-and-software-layers.ipynb` | Explain the ROS 2 graph, software layers, interfaces, and distributed communication model. | None |
| 2 | `2-ros-2-data-paths-and-duckiedrone-integration.ipynb` | Explain modular ROS 2 data paths and the Duckietown Postal Service (DTPS), sensor, PX4 autopilot firmware, MAVLink flight-controller messaging protocol, and MAVROS bridge boundaries. | Notebook 1 |
| 3 | `3-ros-2-nodes-topics-and-interfaces.ipynb` | Identify ROS 2 nodes, topics, messages, message contracts, services, actions, and parameters. | Notebook 1 |
| 4 | `4-ros-2-discovery-domains-and-names.ipynb` | Explain discovery, Zenoh, domains, names, and the relevant ROS 1 comparison. | Notebook 1 |
| 5 | `5-ros-2-workspaces-and-packages.ipynb` | Identify the exercise workspace and an `ament_python` package's source files. | ROS 2 exercise environment |
| 6 | `6-build-and-discover-a-ros-2-package.ipynb` | Build `ros2_pubsub`, source its overlay, and confirm package discovery. | ROS 2 exercise environment; Notebook 5 recommended |
| 7 | `7-inspect-a-local-ros-2-graph.ipynb` | Inspect a safe local publisher graph with `ros2` command-line tools. | ROS 2 exercise environment |
| 8 | `8-inspect-a-duckiedrone-ros-2-graph.ipynb` | Read an authorized Duckiedrone ROS 2 graph and its telemetry interfaces. | Owner-authorized physical or virtual Duckiedrone and Docker access |
| 9 | `9-ros-2-node-lifecycles-and-publishers.ipynb` | Run and safely modify the local `rclpy` publisher starter. | ROS 2 exercise environment |
| 10 | `10-ros-2-subscribers-and-diagnosis.ipynb` | Run the local subscriber and diagnose a missing message in a fixed order. | ROS 2 exercise environment |
| 11 | `11-ros-2-names-and-remapping.ipynb` | Start local nodes with distinct names and topic remappings. | ROS 2 exercise environment |

## What you need

Before using this LX's editor, connection, or exercise workflows, complete the Duckietown Manual's [Initial Setup](https://docs.duckietown.com/ente/duckietown-manual/10-setup/setup-introduction.html) so Docker and the Duckietown Shell (`dts`) are installed and configured on the base station. The supplied ROS 2 exercise environment provides `ros2`, `colcon`, and `COLCON_WS`; this LX does not ask you to install them on the base station.

`dts code editor` is a separate browser editor and is distinct from the ROS 2 exercise environment. Use it to read and edit this LX. Run local `ros2` and `colcon` commands only in the supplied ROS 2 exercise terminal, where `ros2`, `colcon`, and `COLCON_WS` are available; do not assume the editor terminal provides that runtime.

Interactive checkpoints require the notebook metadata supplied by `dts code editor`; a compatible Jupyter/IPython kernel with `ipywidgets` available is not sufficient by itself.

| Task | Where to run it |
| --- | --- |
| Read conceptual Notebooks 1 through 4 and edit exercise files | `dts code editor` or another editor |
| Run local `ros2`, `colcon`, publisher, and subscriber exercises in Notebooks 5 through 7 and 9 through 11 | The supplied ROS 2 exercise terminal |
| Open an authorized physical SSH or virtual Duckiedrone connection using the Linux and Networking LX | A base-station terminal, outside `dts code editor` |
| Run Notebook 8 `docker ps` and `docker exec` commands | The authorized Duckiedrone shell after connecting |
| Inspect the Duckiedrone ROS 2 graph | The `ros2-mavros` service-container shell entered by Notebook 8 |

Notebook 1 needs no ROS 2 installation. An optional physical or virtual Duckiedrone is required only for Notebook 8, and only when its owner authorizes inspection. That notebook is read-only: it does not arm, fly, or send commands to the Duckiedrone. All local notebooks can be completed without device access. Notebook 7 uses two terminals. Notebooks 10 and 11 use two node terminals plus a third observation terminal in the ROS 2 exercise environment.

## Complete the ROS 2 exercise

The starter package lives in `packages/ros2_pubsub`. After source changes, build it once in a ROS 2 exercise terminal:

```bash
source /opt/ros/${ROS2_DISTRO}/setup.bash
cd "${COLCON_WS}"
colcon build --packages-select ros2_pubsub
```

Before running or inspecting the package in each terminal, source the ROS 2 environment and workspace overlay:

```bash
source /opt/ros/${ROS2_DISTRO}/setup.bash
cd "${COLCON_WS}"
source install/setup.bash
```

Notebook 6 explains package building and discovery. Notebooks 9 through 11 repeat the required setup while using the two executable entry points in local exercises.

## Further reading

See the [ROS 2 Jazzy documentation](https://docs.ros.org/en/jazzy/), [Duckietown Postal Service documentation](https://docs.duckietown.com/ente/duckietown-manual/04-software-tools/duckietown-postal-service-dtps.html), the [MAVLink Guide](https://mavlink.io/), [MAVROS documentation](https://github.com/mavlink/mavros), the [PX4 Guide](https://docs.px4.io/main/), [Zenoh documentation](https://zenoh.io/docs/overview/what-is-zenoh/), and the [Duckiedrone DD24 manual](https://docs.duckietown.com/ente/opmanual-dd24/).

## For LX authors

Learner material is in `notebooks/`. Learner code belongs in `packages/`, and structural checks belong in `tests/`. Run the structural checks from the LX root:

```bash
python3 -m pytest tests/
```
