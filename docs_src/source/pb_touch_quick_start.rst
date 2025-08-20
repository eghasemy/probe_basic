PB Touch Quick Start Guide
==========================

Get up and running with PB Touch in just a few minutes.

What is PB Touch?
-----------------

PB Touch is a modern, touch-optimized user interface for LinuxCNC that provides:

- **Touch-first design** with large, easy-to-use controls
- **Professional workflow** for setup, probing, and machining
- **Integrated help system** with contextual assistance
- **Safety-focused** operation with clear visual feedback

5-Minute Setup
--------------

1. Launch PB Touch
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # From terminal
   probe_basic --touch

   # Or use the desktop launcher

2. Initial Safety Check ⚠️
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Before operating any machine:**

- Emergency stop button is accessible and functional
- All machine guards and safety equipment are in place
- Work area is clean and well-lit
- You are wearing appropriate safety equipment

3. Home the Machine
~~~~~~~~~~~~~~~~~~~

1. **Press the "Home All" button** on the main screen
2. **Wait for all axes to complete homing** (indicators turn green)
3. **Verify positions** are correct in the DRO (Digital Readout)

4. Load Your First Job
~~~~~~~~~~~~~~~~~~~~~~

1. **Tap "Job Manager"** on the main navigation
2. **Browse** to your G-code file
3. **Load** the program
4. **Review** the toolpath preview

5. Set Work Coordinates
~~~~~~~~~~~~~~~~~~~~~~~

1. **Navigate to "Probing"** screen
2. **Use "Corner Probe"** or **"Edge Probe"** to find your workpiece
3. **Set Work Coordinate System** (typically G54)

6. Run Your Job
~~~~~~~~~~~~~~~

1. **Return to "Job"** screen  
2. **Press "Cycle Start"** (green play button)
3. **Monitor progress** and be ready to pause/stop if needed

Safety Reminders
-----------------

Always Remember
~~~~~~~~~~~~~~~

- **Keep emergency stop within reach**
- **Never leave machine unattended** during operation
- **Start new programs at reduced feed rates**
- **Verify tool offsets** before cutting
- **Monitor cutting forces** and machine sounds

When in Doubt
~~~~~~~~~~~~~

- **STOP the machine** immediately
- **Ask for help** from experienced operators
- **Consult the troubleshooting guide**
- **Never bypass safety systems**

Next Steps
----------

Learn More
~~~~~~~~~~

- **User Interface Guide** - Detailed screen-by-screen guide
- **Probing Guide** - Complete probing workflows
- **Configuration Guide** - Machine setup and customization
- **Safety Guide** - Comprehensive safety information

Get Help
~~~~~~~~

- **Use "?" buttons** for contextual help
- **Check Troubleshooting Guide** for common issues
- **Visit LinuxCNC Forum** for community support