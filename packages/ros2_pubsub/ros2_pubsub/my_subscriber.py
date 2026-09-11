"""Starter ROS 2 subscriber for the middleware learning experience."""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

# Use the publisher's topic name for the first run.
TOPIC_TO_SUBSCRIBE = "chatter"
# Change this when you run an additional subscriber node.
NODE_NAME = "listener"
# Match the text message type used by the publisher.
MSG_TYPE = String
# Keep up to this many received messages while the callback catches up.
QUEUE_DEPTH = 10


class Listener(Node):
    """Log messages received on the configured topic."""

    def __init__(self) -> None:
        """Create the subscription."""
        # The Node superclass gives this object a ROS 2 name and graph APIs.
        super().__init__(NODE_NAME)

        # Pass the callback itself, not its result. ROS 2 calls it for each message.
        self._subscription = self.create_subscription(
            MSG_TYPE,
            TOPIC_TO_SUBSCRIBE,
            self._message_callback,
            QUEUE_DEPTH,
        )

    def _message_callback(self, message: String) -> None:
        """Log each received string message."""
        # `data` is the text field defined by the std_msgs/msg/String message type.
        self.get_logger().info(f"I heard: {message.data}")


def main(args: list[str] | None = None) -> None:
    """Run the subscriber node until it is interrupted."""
    # Initialize the process-wide ROS 2 client library before creating a node.
    rclpy.init(args=args)
    node: Listener | None = None
    try:
        node = Listener()

        # Keep processing received messages until the user presses Ctrl-C.
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            # Release the subscription before shutting down ROS 2.
            node.destroy_node()
        # Ctrl-C can already shut down the default context before this block runs.
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
