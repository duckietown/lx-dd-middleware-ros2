from setuptools import find_packages, setup

package_name = "ros2_pubsub"


setup(
    name=package_name,
    version="0.0.1",
    packages=find_packages(exclude=["test"]),
    data_files=[
        (
            "share/ament_index/resource_index/packages",
            [f"resource/{package_name}"],
        ),
        (f"share/{package_name}", ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Duckietown",
    maintainer_email="info@duckietown.com",
    description="Starter publisher and subscriber nodes for the ROS 2 middleware learning experience.",
    license="None",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "my_publisher = ros2_pubsub.my_publisher:main",
            "my_subscriber = ros2_pubsub.my_subscriber:main",
        ],
    },
)
