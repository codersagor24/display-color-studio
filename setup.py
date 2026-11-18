from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="display-color-studio",
    version="2.1.0",
    author="ab sagor",
    author_email="codersagor24@users.noreply.github.com",
    description="Professional Display Calibration & Color Profile Management for Linux Wayland",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/codersagor24/display-color-studio",
    project_urls={
        "Bug Tracker": "https://github.com/codersagor24/display-color-studio/issues",
        "Source Code": "https://github.com/codersagor24/display-color-studio",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: X11 Applications :: Gnome",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Desktop Environment :: Gnome",
        "Topic :: Multimedia :: Graphics",
    ],
    python_requires=">=3.10",
    install_requires=[
        "PyGObject>=3.42.0",
    ],
    entry_points={
        "console_scripts": [
            "display-color-studio = display_color_studio.cli:main",
        ],
    },
    package_data={
        "display_color_studio": ["*.css"],
    },
    include_package_data=True,
)
