"""Starter ROS 2 publisher for the middleware learning experience."""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

# Choose one message type. Publishers and subscribers on a topic must agree on it.
MSG_TYPE = String
# Publish once each second; change this only after the starter node works.
PUBLISH_RATE_HZ = 1.0
# Change this text after confirming the starter node runs.
MESSAGE_CONTENT = "Hello from ROS 2!"
# Change the topic name only when the subscriber uses the same name.
TOPIC_NAME = "chatter"
NODE_NAME = "talker"
# Keep up to this many messages while the subscriber catches up.
QUEUE_DEPTH = 10


class Talker(Node):
    """Publish a message periodically on the configured topic."""

    def __init__(self) -> None:
        """Create the publisher and its periodic timer."""
        # The Node superclass gives this object a ROS 2 name and graph APIs.
        super().__init__(NODE_NAME)

        # The message type, topic name, and queue depth define this publisher.
        self._publisher = self.create_publisher(
            MSG_TYPE, TOPIC_NAME, QUEUE_DEPTH
        )

        # Timers use seconds, so convert the publication rate from hertz first.
        timer_period = 1.0 / PUBLISH_RATE_HZ

        # ROS 2 calls this named method every timer period while the node spins.
        self._timer = self.create_timer(timer_period, self._publish_message)

    def _publish_message(self) -> None:
        """Create, log, and publish the configured message."""
        # Make a new message for this publication, then fill in its text field.
        message = MSG_TYPE()
        message.data = MESSAGE_CONTENT

        # The log shows what the node sends; publish sends it to the ROS 2 topic.
        self.get_logger().info(message.data)
        self._publisher.publish(message)


def main(args: list[str] | None = None) -> None:
    """Run the publisher node until it is interrupted."""
    # Initialize the process-wide ROS 2 client library before creating a node.
    rclpy.init(args=args)
    node: Talker | None = None
    try:
        node = Talker()

        # Keep processing timer and ROS 2 events until the user presses Ctrl-C.
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            # Release the publisher and timer before shutting down ROS 2.
            node.destroy_node()
        # Ctrl-C can already shut down the default context before this block runs.
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
