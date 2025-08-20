Probe Basic Quick Start Guide
============================

This guide will get you up and running with Probe Basic quickly and safely.

## Prerequisites

Before starting, ensure you have:

- LinuxCNC 2.8+ installed
- A properly configured CNC machine
- Basic understanding of CNC operations
- Emergency stop easily accessible

## First Launch

1. **Start Probe Basic**
   ```bash
   probe_basic
   ```

2. **Check Machine Status**
   - Verify ESTOP is released (green indicator)
   - Check all limit switches are clear
   - Ensure machine is not alarmed

3. **Home the Machine**
   - Click "Home All" or home axes individually
   - Wait for all axes to complete homing
   - Verify axis indicators turn green

## Dashboard Overview

The main dashboard provides:

- **DRO (Digital Read Out)**: Shows current position
- **Modal Groups**: Active G-code modes (G0/G1, G17-19, etc.)
- **Status Indicators**: ESTOP, homed, limits, spindle
- **Override Controls**: Feed rate and spindle speed adjustments
- **Cycle Controls**: Start, pause, stop program execution

## Basic Operations

### Loading a Program

1. Navigate to **Job Manager** tab
2. Browse to your G-code file
3. Select and load the program
4. Review the toolpath preview
5. Check estimated run time

### Setting Work Coordinates

1. **Manual Method**:
   - Jog to your work zero position
   - Select coordinate system (G54-G59.3)
   - Click "Zero X", "Zero Y", "Zero Z" as needed

2. **Using Probe** (if available):
   - Install touch probe
   - Go to **Probing** tab
   - Select edge or corner finding
   - Follow on-screen instructions

### Running a Program

1. **Pre-flight Checks**:
   - Machine is homed ✓
   - Work coordinates are set ✓
   - Correct tool is loaded ✓
   - Workpiece is secure ✓
   - Emergency stop is accessible ✓

2. **Start Program**:
   - Click **Cycle Start**
   - Monitor progress on dashboard
   - Use **Feed Hold** to pause if needed
   - Use **Cycle Stop** to abort operation

## Safety Features

### Emergency Stop
- Physical ESTOP button stops all motion immediately
- Software ESTOP available in UI
- Always test ESTOP before operation

### Soft Limits
- Prevent machine from exceeding travel limits
- Can be temporarily overridden with confirmation
- Set properly during machine configuration

### Safety Interlocks
- Door switches, limit switches, probe signals
- Monitored continuously during operation
- Will stop machine if activated

## Common Controls

### Jogging
- **Manual Positioning**: Use jog panel
- **Incremental Mode**: Move exact distances
- **Continuous Mode**: Hold button to move
- **MPG Support**: Connect USB MPG for fine control

### Overrides
- **Feed Rate**: 10% to 200% of programmed rate
- **Spindle Speed**: 10% to 200% of programmed RPM
- **Rapid Override**: Slow down rapid moves

### Tool Changes
- **Manual**: Follow tool change prompts
- **ATC (if equipped)**: Automatic tool changing
- **Tool Length**: Measure with probe or preset

## Troubleshooting

### Machine Won't Home
- Check limit switch wiring
- Verify limit switch polarity in HAL
- Ensure axes can move freely

### Program Won't Start
- Check for active alarms
- Verify machine is homed
- Ensure work coordinates are set
- Check tool number is available

### Probe Not Working
- Test probe continuity
- Check probe signal in IO panel
- Verify probe is properly connected
- Confirm probe polarity in configuration

### Emergency Procedures

1. **ESTOP Activated**: 
   - Identify cause of ESTOP
   - Clear any obstructions
   - Reset ESTOP when safe
   - Re-home machine if needed

2. **Collision or Crash**:
   - Press ESTOP immediately
   - Turn off spindle power
   - Assess damage before continuing
   - Check machine accuracy after incident

## Getting Help

- **Built-in Help**: Click "?" button on any screen
- **Documentation**: Access full manual in Help menu
- **Community Support**: LinuxCNC forums and IRC
- **Log Files**: Check `~/.probe_basic/logs/` for diagnostics

## Next Steps

Once comfortable with basic operations:

1. **Explore Probing**: Learn edge finding and work coordinate setup
2. **Configure ATC**: Set up automatic tool changing if available
3. **Customize Interface**: Adjust layouts and preferences
4. **Create Workflows**: Develop standard operating procedures
5. **Advanced Features**: Job queuing, conversational programming

Remember: **Safety First!** Always understand what the machine will do before pressing start.

---

For detailed information on any topic, refer to the full Probe Basic documentation or use the built-in help system.