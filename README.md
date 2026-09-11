<p align="center">
<a href="https://duckietown.com"><img src="./assets/images/dtlogo.png" alt="Duckietown Logo" width="50%"></a>
</p>

# Learning Experience (LX): ROS 2 Middleware on the Duckiedrone

`Software: ente`; `Hardware: DD24-B`

Robot Operating System 2 (ROS 2) helps a robot divide work among small, independent programs that communicate through a
shared graph. In this learning experience (LX), you will learn the ROS 2 concepts and command-line
tools behind that graph, then build and run your own Python publisher and subscriber.

## Intended learning outcomes

After completing this learning experience, learners will be able to:

1. Describe the ROS 2 graph, client-library, and middleware layers, and explain how nodes, topics, messages, services, and parameters fit together in a robot.

2. Explain how ROS 2 discovery and `ROS_DOMAIN_ID` let nodes communicate without a Robot Operating System 1 (ROS 1) master.

3. Create, build, source, and inspect an `ament_python` ROS 2 package with `colcon` and `ros2`.

4. Write and run Python publisher and subscriber nodes with `rclpy` and `std_msgs/msg/String`.

5. Explain how the Duckietown Postal Service (DTPS), ROS 2 bridges, and the
    MAVROS bridge between the flight controller and ROS 2 make sensor data from a current Duckiedrone visible to application nodes.

## Notebooks

Start with required Module 1 before the Duckiedrone-specific architecture or ROS 2 commands. The
remaining notebooks can be assigned individually when their listed prerequisites are available:

| # | Notebook | Outcome | Prerequisites |
| --- | --- | --- | --- |
| 1 | `1-ros-2-foundations-and-architecture.ipynb` | Explain the ROS 2 graph, software layers, interfaces, and distributed communication model. | None |
| 2 | `2-ros-2-architecture-and-data-paths.ipynb` | Explain modular ROS 2 data paths and the Duckietown Postal Service (DTPS), sensor, PX4 autopilot firmware, MAVLink flight-controller messaging protocol, and MAVROS bridge boundaries. | Notebook 1 |
| 3 | `3-ros-2-nodes-topics-and-interfaces.ipynb` | Identify ROS 2 nodes, topics, messages, message contracts, services, actions, and parameters. | Notebook 1 |
| 4 | `4-ros-2-discovery-domains-and-names.ipynb` | Explain discovery, Zenoh, domains, names, and the relevant ROS 1 comparison. | Notebook 1 |
| 5 | `5-ros-2-workspaces-and-packages.ipynb` | Identify the exercise workspace and an `ament_python` package's source files. | ROS 2 exercise environment |
| 6 | `6-build-and-discover-a-ros-2-package.ipynb` | Build `ros2_pubsub`, source its overlay, and confirm package discovery. | ROS 2 exercise environment; Notebook 5 recommended |
| 7 | `7-inspect-a-local-ros-2-graph.ipynb` | Inspect a safe local publisher graph with `ros2` command-line tools. | ROS 2 exercise environment |
| 8 | `8-inspect-a-duckiedrone-ros-2-graph.ipynb` | Read an authorized Duckiedrone ROS 2 graph and its telemetry interfaces. | Owner-authorized physical or virtual Duckiedrone and Docker access |
| 9 | `9-ros-2-node-lifecycles-and-publishers.ipynb` | Run and safely modify the local `rclpy` publisher starter. | ROS 2 exercise environment |
| 10 | `10-ros-2-subscribers-and-diagnosis.ipynb` | Run the local subscriber and diagnose a missing message in a fixed order. | ROS 2 exercise environment |
| 11 | `11-ros-2-names-and-remapping.ipynb` | Start local nodes with unique names and topic remappings. | ROS 2 exercise environment |

## What you need

Module 1 needs no ROS 2 installation. Use the ROS 2 exercise environment supplied with this LX
for the local command-line and coding exercises. An optional physical or virtual Duckiedrone is
required only for Notebook 8, and only when the instructor or learner is authorized to inspect it.
That notebook is read-only: it does not arm, fly, or send commands to the Duckiedrone. Instructors
can assign all local modules without device access.

## Build the exercise package

The starter package lives in `packages/ros2_pubsub`. Each new terminal needs the ROS 2 environment
and the workspace overlay before it can find your package:

```bash
source /opt/ros/${ROS2_DISTRO}/setup.bash
cd "${COLCON_WS}"
colcon build --packages-select ros2_pubsub
source install/setup.bash
```

Notebook 6 explains package building and discovery. Notebooks 9 through 11 repeat the required
setup while using the two executable entry points in local exercises.

## Further reading

For further reading, see the [ROS 2 Jazzy documentation](https://docs.ros.org/en/jazzy/),
[Duckietown Postal Service documentation](https://docs.duckietown.com/ente/duckietown-manual/04-software-tools/duckietown-postal-service-dtps.html),
the [MAVLink Guide](https://mavlink.io/), [MAVROS documentation](https://github.com/mavlink/mavros),
the [PX4 Guide](https://docs.px4.io/main/), [Zenoh documentation](https://zenoh.io/docs/overview/what-is-zenoh/),
and the [Duckiedrone DD24 manual](https://docs.duckietown.com/ente/opmanual-dd24/).

## For LX authors

Learner material is in `notebooks/`. Learner code belongs in `packages/`, and structural checks
belong in `tests/`.
Run the structural checks from the LX root:

```bash
pytest tests/
```
