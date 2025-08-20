PB Touch Installation Guide
============================

Complete installation instructions for PB Touch on LinuxCNC systems.

System Requirements
-------------------

Supported Operating Systems
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **LinuxCNC 2.9+** (recommended)
- **Debian 12 (Bookworm)** x64
- **Ubuntu 22.04 LTS** or newer

Hardware Requirements
~~~~~~~~~~~~~~~~~~~~~

- **Minimum**: 2GB RAM, dual-core processor
- **Recommended**: 4GB+ RAM, quad-core processor
- **Touch Screen**: 7" minimum, 10"+ recommended
- **Resolution**: 1024x600 minimum, 1920x1080+ recommended

Installation Methods
--------------------

Method 1: Package Installation (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For Debian/Ubuntu Systems:

.. code-block:: bash

   # Update package list
   sudo apt update

   # Install PB Touch package
   sudo apt install probe-basic-touch

   # Or download and install .deb package
   wget https://github.com/eghasemy/probe_basic/releases/latest/download/probe-basic-touch.deb
   sudo dpkg -i probe-basic-touch.deb
   sudo apt install -f  # Fix any dependency issues

Method 2: Development Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install dependencies
   sudo apt install python3-pip python3-venv git

   # Clone repository
   git clone https://github.com/eghasemy/probe_basic.git
   cd probe_basic

   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate

   # Install with Poetry
   pip install poetry
   poetry install

   # Run PB Touch
   poetry run probe_basic --touch

Initial Configuration
---------------------

LinuxCNC Integration
~~~~~~~~~~~~~~~~~~~~

Add to LinuxCNC INI File:

.. code-block:: ini

   [DISPLAY]
   DISPLAY = probe_basic --touch
   PROGRAM_PREFIX = /home/cnc/linuxcnc/nc_files
   INTRO_GRAPHIC = probe_basic_icon.png
   INTRO_TIME = 5
   POSITION_OFFSET = RELATIVE
   POSITION_FEEDBACK = ACTUAL
   MAX_FEED_OVERRIDE = 2.0
   MAX_SPINDLE_OVERRIDE = 2.0
   MIN_SPINDLE_OVERRIDE = 0.1
   DEFAULT_LINEAR_VELOCITY = 1.0
   MAX_LINEAR_VELOCITY = 25.0

   # Touch-specific settings
   TOUCH_OPTIMIZED = true
   TOUCH_THEME = default
   TOUCH_TARGET_SIZE = 44

Next Steps
----------

After Installation
~~~~~~~~~~~~~~~~~~

1. **Read Safety Guide** - Essential safety information
2. **Follow Quick Start Guide** - Get running quickly
3. **Configure your machine** using Configuration Guide
4. **Learn the interface** with User Interface Guide