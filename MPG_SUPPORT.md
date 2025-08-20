# MPG Support Documentation - Phase 3

This document describes the Manual Pulse Generator (MPG) support implemented in Phase 3 of Probe Basic.

## Overview

The Phase 3 implementation provides comprehensive MPG support through two main components:
1. **On-screen MPG wheel** - Visual representation with mouse/touch interaction
2. **USB/Bluetooth MPG device binding** - Framework for physical device integration

## On-Screen MPG Wheel

### Features
- Visual wheel with detent marks and position indicator
- Mouse/touch drag interaction for rotation
- Configurable acceleration multiplier
- Real-time position feedback
- Integration with axis selection and increment settings

### Configuration
The MPG wheel can be configured through the Jog Panel interface:

```python
# Counts per detent (configurable via spinbox)
mpg_wheel.counts_per_detent = 4  # Default: 4 counts per detent

# Acceleration multiplier
mpg_wheel.acceleration = 1.0  # Default: 1.0 (no acceleration)
```

### Usage
1. Select target axis (X, Y, or Z) using radio buttons
2. Choose jog increment (continuous, 1.0, 0.1, 0.01, 0.001)
3. Click and drag the MPG wheel to generate movement
4. Movement distance calculated based on:
   - Wheel rotation angle
   - Selected increment
   - Counts per detent setting

### Movement Calculation
```python
# Calculate movement from wheel rotation
angle_fraction = angle_diff / (2 * math.pi)  # Fraction of full rotation
counts_per_revolution = 100  # Standard MPG: 100 counts per revolution
movement_per_count = jog_increment / counts_per_detent
distance = angle_fraction * counts_per_revolution * movement_per_count
```

## USB/Bluetooth MPG Device Support

### Framework
The implementation provides a framework for integrating physical MPG devices:

```python
class MPGDevice:
    """Base class for physical MPG devices"""
    
    def __init__(self, device_path, counts_per_detent=4):
        self.device_path = device_path
        self.counts_per_detent = counts_per_detent
        self.axis_feed_config = {}
        
    def configure_axis_feed(self, axis, feed_rate):
        """Configure feed rate for specific axis"""
        self.axis_feed_config[axis] = feed_rate
        
    def read_counts(self):
        """Read count changes from physical device"""
        raise NotImplementedError
        
    def set_enable_required(self, required):
        """Configure whether enable signal is required"""
        self.enable_required = required
```

### Device Configuration
Physical MPG devices can be configured with:

#### Counts Per Detent
- Typical values: 1, 2, 4, 5, 10, 20
- Affects movement resolution per physical detent
- Configurable per device type

#### Axis Feed Mapping
```python
# Example feed configuration
mpg_device.configure_axis_feed('X', 100.0)  # 100 mm/min for X axis
mpg_device.configure_axis_feed('Y', 100.0)  # 100 mm/min for Y axis  
mpg_device.configure_axis_feed('Z', 50.0)   # 50 mm/min for Z axis (slower)
```

#### Safety Configuration
```python
# Require enable signal for MPG operation
mpg_device.set_enable_required(True)

# Configure enable pin (HAL integration)
# hal.Pin('mpg-enable') -> mpg_device.enable_pin
```

### Common MPG Devices

#### USB MPG Wheels
- Standard HID interface
- 100 counts per revolution typical
- Often include axis selector switches
- May have enable button/switch

#### Bluetooth MPG Pendants
- Wireless operation with battery
- Built-in axis selection
- Increment selection switches
- Emergency stop integration

#### Pendant MPG Controllers
- Wired connection via parallel/serial
- Multiple axes and increments
- Enable/disable switches
- Feed rate override controls

### HAL Integration

Physical MPG devices integrate with LinuxCNC through HAL pins:

```hal
# Example HAL configuration for USB MPG
loadrt encoder num_chan=1
addf encoder.update-counters servo-thread
addf encoder.capture-position servo-thread

# Connect MPG encoder to HAL
net mpg-a encoder.0.phase-A <= parport.0.pin-02-in
net mpg-b encoder.0.phase-B <= parport.0.pin-03-in

# Connect to jog panel
net mpg-counts encoder.0.counts => probe_basic.mpg-counts
net mpg-axis probe_basic.mpg-axis <= parport.0.pin-04-in
net mpg-enable probe_basic.mpg-enable <= parport.0.pin-05-in
```

### Integration with Jog Panel

The Jog Panel automatically detects and integrates with configured MPG devices:

```python
# In JogPanel.__init__()
self.physical_mpg = self.detect_mpg_devices()
if self.physical_mpg:
    self.physical_mpg.counts_changed.connect(self.handle_physical_mpg)
    
def handle_physical_mpg(self, axis, counts):
    """Handle counts from physical MPG device"""
    if not self.check_mpg_enable():
        return
        
    # Calculate movement based on counts and current increment
    distance = counts * self.jog_increment / self.physical_mpg.counts_per_detent
    
    # Execute jog command
    self.jog_axis(axis, distance)
```

## Safety Features

### Enable Signal Requirements
- Physical MPG devices can require enable signal
- On-screen MPG respects machine enable state
- All MPG operations blocked during ESTOP

### Interlocks
- Axis homing status checked before MPG operation
- Machine enabled state verified
- Limit switch status monitored
- Feed rate limits enforced

### Error Handling
```python
def safe_mpg_jog(self, axis, distance):
    """Perform MPG jog with safety checks"""
    try:
        # Check machine state
        if not self.status.enabled() or self.status.estop():
            LOG.warning("MPG jog blocked - machine not ready")
            return False
            
        # Check axis homing
        if not self.is_axis_homed(axis):
            LOG.warning(f"MPG jog blocked - {axis} axis not homed")
            return False
            
        # Perform jog
        return self.execute_jog(axis, distance)
        
    except Exception as e:
        LOG.error(f"MPG jog error: {e}")
        return False
```

## Configuration Examples

### Basic On-Screen MPG
```yaml
# probe_basic.yml
mpg:
  on_screen:
    enabled: true
    counts_per_detent: 4
    acceleration: 1.0
    enable_required: false
```

### USB MPG Device
```yaml
# probe_basic.yml  
mpg:
  usb_device:
    enabled: true
    device_path: "/dev/input/by-id/usb-MPG_Wheel"
    counts_per_detent: 4
    axis_feeds:
      X: 100.0
      Y: 100.0
      Z: 50.0
    enable_required: true
    enable_pin: "parport.0.pin-05-in"
```

### Bluetooth MPG Pendant
```yaml
# probe_basic.yml
mpg:
  bluetooth_pendant:
    enabled: true
    device_address: "00:11:22:33:44:55"
    counts_per_detent: 5
    axis_feeds:
      X: 200.0
      Y: 200.0
      Z: 100.0
    enable_required: true
    estop_integration: true
```

## Troubleshooting

### Common Issues

#### On-Screen MPG Not Responding
- Check mouse/touch interaction area
- Verify axis selection and increment settings
- Ensure machine is enabled and not in ESTOP

#### Physical MPG Not Working
- Verify device connection and HAL pin configuration
- Check enable signal requirements
- Confirm counts per detent setting matches device
- Test with HAL scope to verify encoder signals

#### Erratic Movement
- Check for electrical noise on encoder signals
- Verify proper grounding and shielding
- Adjust debounce settings if available
- Consider differential encoder signals for long runs

### Diagnostic Commands
```bash
# Check HAL pins
halcmd show pin mpg

# Monitor encoder counts
halscope
# Add pin encoder.0.counts to scope

# Test enable signal
halcmd sets probe_basic.mpg-enable 1
```

## Future Enhancements

### Planned Features
- **Multiple MPG Support**: Simultaneous on-screen and physical devices
- **Custom Device Drivers**: Support for proprietary MPG protocols
- **Advanced Acceleration**: Velocity-based acceleration curves
- **Axis Grouping**: Gang multiple axes with single MPG
- **Feed Rate Override**: Direct MPG control of feed rate override

### Integration Opportunities
- **Touch Screen Optimization**: Enhanced touch gestures for tablets
- **Haptic Feedback**: Vibration feedback for detent simulation
- **Audio Feedback**: Click sounds for detent positions
- **Visual Enhancements**: 3D wheel rendering with shadows/highlights

This MPG support provides a comprehensive foundation for manual machine control in both development and production environments.