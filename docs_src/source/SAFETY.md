Probe Basic Safety Guide
=======================

**⚠️ CRITICAL: Read this entire safety guide before operating any CNC machine with Probe Basic.**

## General Safety Principles

### Before ANY Operation

1. **Understand Your Machine**
   - Know your machine's capabilities and limitations
   - Understand the coordinate systems and work envelopes
   - Be familiar with all safety devices and their locations

2. **Personal Protective Equipment (PPE)**
   - Safety glasses are MANDATORY
   - Hearing protection in noisy environments
   - No loose clothing, jewelry, or long hair near moving parts
   - Closed-toe shoes with non-slip soles

3. **Emergency Preparedness**
   - Know location of emergency stop buttons
   - Know how to shut off main power
   - Keep first aid kit accessible
   - Have emergency contact numbers available

## Pre-Operation Safety Checklist

### Machine Inspection
- [ ] Emergency stop button tested and functional
- [ ] All guards and enclosures secure
- [ ] Work area clean and well-lit
- [ ] No tools or debris in machine envelope
- [ ] Adequate ventilation for coolant/chips
- [ ] Fire extinguisher accessible

### Software Setup
- [ ] Machine properly homed
- [ ] Coordinate systems verified
- [ ] Tool table accurate and up-to-date
- [ ] Override settings at safe values
- [ ] Probe (if used) tested for continuity

### Workpiece Setup
- [ ] Workpiece securely clamped
- [ ] Clamps clear of tool path
- [ ] Work coordinates properly set
- [ ] Adequate material thickness for operations

## Operation Safety

### Starting Operations

1. **Program Verification**
   - Review G-code for obvious errors
   - Check tool numbers and offsets
   - Verify feed rates and spindle speeds
   - Use single block mode for new programs

2. **First Run Protocol**
   - Start with feed override at 50% or less
   - Keep hand near feed hold button
   - Watch first few moves carefully
   - Stop immediately if anything looks wrong

3. **Never Leave Unattended**
   - Always supervise machine operation
   - If you must leave, pause or stop the program
   - Never run overnight without supervision

### During Operation

1. **Continuous Monitoring**
   - Watch for unusual sounds or vibrations
   - Monitor cutting forces and quality
   - Check for proper chip evacuation
   - Verify coolant flow if applicable

2. **Override Usage**
   - Use feed override to control cutting
   - Keep rapid override at reasonable levels
   - Never exceed 100% on unfamiliar programs

3. **Tool Changes**
   - Always stop spindle before tool changes
   - Verify tool orientation and length
   - Test new tools at reduced feed rates

## Probing Safety

### Touch Probe Operations

1. **Pre-Probe Checklist**
   - Probe signal tested and verified
   - Probe tip clean and undamaged
   - Spindle completely stopped
   - Workpiece properly secured

2. **Probe Setup**
   - Use conservative feed rates (typically 10-50 IPM)
   - Set appropriate retract distances
   - Verify probe polarity (normally open vs. closed)
   - Test probe on known surface first

3. **During Probing**
   - Watch probe approach carefully
   - Be ready to hit feed hold
   - Never force probe against surface
   - Stop if probe doesn't trigger as expected

### Tool Setting

1. **Tool Setter Safety**
   - Verify tool setter signal
   - Use slow approach speeds
   - Ensure tool is properly secured in spindle
   - Check for runout before setting

## Emergency Procedures

### Emergency Stop Activation

1. **When to Use ESTOP**
   - Any unexpected behavior
   - Tool breakage or failure
   - Workpiece movement or clamping failure
   - Personal injury risk
   - Fire, smoke, or unusual odors

2. **After ESTOP**
   - Do NOT immediately restart
   - Identify and correct the problem
   - Inspect for damage
   - Re-home machine if necessary
   - Test safety systems before resuming

### Collision/Crash Response

1. **Immediate Actions**
   - Press ESTOP immediately
   - Turn off spindle power
   - Turn off main power if necessary
   - Stay clear of moving parts

2. **Assessment**
   - Check for injuries first
   - Assess machine damage
   - Check workpiece security
   - Inspect tooling and spindle

3. **Recovery**
   - Do not restart until thoroughly inspected
   - Check machine accuracy with test cuts
   - Replace damaged components
   - Document incident for future prevention

## Specific Hazards and Prevention

### Cutting Tool Hazards

1. **Sharp Tools**
   - Always handle tools carefully
   - Use proper tool handling procedures
   - Store tools securely
   - Dispose of broken tools safely

2. **Flying Debris**
   - Always use safety glasses
   - Ensure guards are in place
   - Control chip evacuation
   - Be aware of chip flow direction

### Electrical Safety

1. **Power Isolation**
   - Know location of main disconnect
   - Lock out power for major maintenance
   - Keep electrical panels closed
   - Report electrical problems immediately

2. **Wet Conditions**
   - Never operate with wet hands
   - Keep coolant and electrical separated
   - Use GFCI protection where required
   - Clean up spills immediately

### Mechanical Hazards

1. **Moving Parts**
   - Keep clear of moving axes
   - Never try to stop motion with hands
   - Be aware of rapid movements
   - Ensure proper guarding

2. **Pinch Points**
   - Keep hands clear of closing surfaces
   - Be aware of ATC movement
   - Never reach into machine during operation

## Software-Specific Safety

### Probe Basic Features

1. **Safety Interlocks**
   - Understand soft limit behavior
   - Know override procedures
   - Test safety systems regularly
   - Don't disable safety features

2. **Override Controls**
   - Start conservatively with new programs
   - Understand override ranges and effects
   - Use feed hold liberally when learning

3. **Homing and Limits**
   - Always home machine before operation
   - Understand limit switch behavior
   - Know recovery procedures for limit trips

## Training and Competency

### Required Knowledge

1. **CNC Fundamentals**
   - Coordinate systems
   - Tool offsets and compensation
   - Feed rates and spindle speeds
   - G-code basics

2. **Machine Specific**
   - Your machine's characteristics
   - Control system operation
   - Maintenance requirements
   - Emergency procedures

### Ongoing Safety

1. **Regular Training**
   - Stay current with safety practices
   - Learn from incidents and near-misses
   - Participate in safety meetings
   - Review procedures regularly

2. **Reporting**
   - Report all incidents and near-misses
   - Suggest safety improvements
   - Share lessons learned
   - Maintain safety documentation

## Remember

**When in doubt, STOP the machine and ask for help.**

**No part, schedule, or deadline is worth an injury.**

**Safety is everyone's responsibility.**

---

This safety guide should be reviewed regularly and updated based on experience and incident reports. Always follow your facility's specific safety procedures in addition to these guidelines.