# PB-Touch: A Masso‑Grade LinuxCNC Frontend
_A comprehensive design spec for developers and GitHub Copilot_

---

## 1) Executive Summary & Overall Project Goal

**PB‑Touch** is a modern, touchscreen‑first frontend for **LinuxCNC 2.9+** built on **Probe Basic / QtPyVCP**.  
Its mission is to combine LinuxCNC’s open, industrial‑grade motion control with the **appliance‑like UX** of a **Masso G3 Touch** controller—without locking users to proprietary hardware.

### Why this matters
- **Production usability**: One polished interface for daily job setup, probing, tool management, ATC, and diagnostics.
- **Approachable setup**: Visual pin mapping and machine config wizards reduce steep HAL/INI learning curves.
- **Reliability & safety**: Guardrails (interlocks, homing manager, soft‑limit overrides, recovery flows) make mistakes less likely.
- **Open & extensible**: QtPyVCP widgets, YAML wiring, HAL components, and NGC macros remain hackable and scriptable.

### Non‑Goals
- Replacing the LinuxCNC planner, kinematics, or HAL ecosystem.
- Achieving universal machine coverage in v0.1 (start with **mill**; lathe/plasma later).
- Shipping a closed bundle—PB‑Touch stays **upstream‑friendly** and **open source**.

---

## 2) Target Platform & Dependencies

- **LinuxCNC**: 2.9+ (mill focused)
- **Qt / Python**: Qt 5.15+, Python 3.10+
- **Framework**: QtPyVCP (latest stable), Probe Basic as base
- **Graphics/Preview**: gremlin (LinuxCNC toolpath preview)
- **Packaging**: AppImage, .deb
- **Testing**: pytest, pytest‑qt, headless LinuxCNC sim runs

---

## 3) Repository Layout

```
/ui/                   # Qt Designer .ui files, icons, QSS themes
/ui/themes/pb-touch.qss
/ui/icons/…

/vcp/                  # QtPyVCP app, screens & custom widgets
/vcp/pb_touch.py
/vcp/screens/          # Home, Job, PinMapper, Probing, ATC, Settings, Diagnostics
/vcp/widgets/          # StatusTiles, MPGWheel, PinMapTree, ATCPanel, etc.

/config/               # YAML bindings & app config
/config/pb_touch.yaml
/config/actions.yaml
/config/shortcuts.yaml
/config/pinmap.d/      # Saved pin mapping profiles

/hal/                  # HAL templates, stubs & custom components
/hal/pb_touch_sim.hal
/hal/components/pb_pinmap.comp  # optional helper for PinMap

/machines/             # INI/HAL templates (sim + sample hardware)
/machines/sim-mill/ini/pb_touch_sim.ini
/machines/sim-mill/hal/…

/wizards/              # Probing & ATC macros, conversational ops
/wizards/probing/      # o<probe_corner>, o<probe_boss>, etc.
/wizards/atc/
/wizards/conversational/

/docs/                 # User/dev docs & screenshots
/tests/                # unit + UI + sim smoke tests
/scripts/              # packaging, mounts, warmup, etc.
```

---

## 4) UX Principles (for every screen)

- **Touch‑first**: min 44 px tap targets; large sliders & toggles; generous spacing.
- **Status clarity**: red/amber/green state tiles for ESTOP, Machine On, Homed, Limits, Probe, Spindle.
- **One‑tap workflows**: dashboard → job → run; probing & ATC guided wizards.
- **Predictable navigation**: persistent top/bottom ribbons; softkeys consistent per screen.
- **Safe by default**: never allow force‑outputs in ESTOP/OFF; confirmation for risky actions.
- **Zero blocking UI**: long operations delegated to worker threads with progress + cancel.

---

## 5) Architecture Overview

**QtPyVCP / Probe Basic** supplies a VCP (Virtual Control Panel) where widgets bind to:
- **stat** (read): machine state, axis positions, overrides
- **halui / motion pins** (write): estop, cycle start, jog, override setpoints
- **vcp vars**: in‑app state (units, themes, wizard params)

**HAL/INI/NGC** split:
- **INI**: kinematics, I/O names, remaps (e.g., `M6`), UI options
- **HAL**: real pins & signals, IO drivers (Mesa/ethercat/hostmot2), safety chain
- **NGC macros**: probing routines, ATC change logic, warmup sequences

**Data Flow Example**
1. User taps **Cycle Start** → VCP emits action → `halui.program.run` pin toggles
2. LinuxCNC executes program; **stat** updates → DRO/modules refresh
3. On alarm → VCP AlarmPanel shows sticky entry until acknowledged → logs to file

---

## 6) Configuration Binding (example)

`/config/pb_touch.yaml`:
```yaml
widgets:
  droX.value:               { source: stat:axis.0.pos }
  droY.value:               { source: stat:axis.1.pos }
  droZ.value:               { source: stat:axis.2.pos }
  unitsToggle.state:        { source: vcp:units, sink: vcp:units }
  cycleStart.clicked:       { sink: halui.program.run }
  cycleHold.clicked:        { sink: halui.program.pause }
  cycleStop.clicked:        { sink: halui.program.stop }
  estopButton.clicked:      { sink: halui.estop.activate }
  machineOnToggle.toggled:  { sink: halui.machine.on }
  feedOverride.value:       { source: stat:motion:feed-override,  sink: halui.feed-override.value }
  rapidOverride.value:      { source: stat:motion:rapid-override, sink: halui.rapid-override.value }
  spindleOverride.value:    { source: stat:spindle.0:override,    sink: halui.spindle.override.value }
```

---

## 7) Phased Plan — Detailed

Each phase includes **Goals**, **Tasks**, **Acceptance Criteria**, and **Deliverables**.

### Phase 0 — Bootstrap & Theming
**Goals**
- Create PB‑Touch theme and app skeleton on top of Probe Basic.
- Loadable sim machine with nav + status ribbons wired.

**Tasks**
- Theme: `/ui/themes/pb-touch.qss`
  - Day/Night palettes, high contrast, flat cards, large tap areas
  - Focus outlines, keyboard access, scalable fonts (dpi‑aware)
- Screens (`.ui` or QML via Qt Designer):
  - Home, Job, PinMapper, Probing, ATC, Settings, Diagnostics
- Ribbons:
  - Left: ESTOP, Machine On/Off
  - Center: Mode (Auto/MDI/Manual), Cycle controls
  - Right: Feed/Rapid/Spindle overrides, active WCS, current Tool
- Actions config: `/config/actions.yaml`, keybinds in `/config/shortcuts.yaml`
- Sim machine: `/machines/sim-mill/ini/pb_touch_sim.ini` & `/hal/pb_touch_sim.hal`

**Acceptance Criteria**
- `linuxcnc -ini .../pb_touch_sim.ini` boots to Home.
- ESTOP and Machine On toggle sim pins.
- Override sliders animate and reflect `stat` reads.

**Deliverables**
- Theme, screens, nav skeleton; working sim machine; README quick start.

---

### Phase 1 — Dashboard Parity (Masso Main)
**Goals**
- Masso‑style dashboard providing complete at‑a‑glance status & control.

**Tasks**
- DRO widget (inch/mm toggle, soft zero per axis, WCS display).
- Modal groups HUD: G0/G1, G17/18/19, G90/91, G54–G59.3, G20/21, G40/41/42, G43/49.
- Cycle controls: Start/Hold/Stop; Single Block; Optional Stop.
- Status tiles: ESTOP, Machine On, Homed per axis, Limits, Probe present, Spindle state.
- Tool info: active tool, length/radius, notes, toolpath preview tile.
- Alarms panel: sticky entries with acknowledge, expand for details/log link.
- Spindle warmup button (hooks Phase 7 program).

**Acceptance Criteria**
- Running demo program updates DRO, modal HUD, tool preview.
- Cycle controls affect execution live.
- Triggered sim alarm appears and requires acknowledgment.

**Deliverables**
- Home screen complete; screenshot for docs; demo G‑code showcasing widgets.

---

### Phase 2 — Pin Mapper & Machine Config Wizard
**Goals**
- Visual mapping: Function ↔ Signal ↔ Pin, with safe regeneration of HAL snippets.
- High‑level machine wizard to generate base INI/HAL.

**Tasks**
- **PinMapTree** widget
  - Tree columns: Function | Signal | Pin | Notes
  - Filters (subsystem, search), validation (duplicates/conflicts)
  - Context menu: “Jump to HAL”, “Test (blink/edge)”, “Unmap”
- Mappings persistence: `/config/pinmap.d/<profile>.yaml`
- HAL generation pipeline:
  - Render Jinja2 template → append gated block to `/hal/pb_touch_sim.hal`
  - Dry‑run and diff preview before apply
  - Safe re‑load: if reload fails, revert to previous HAL & show errors
- **Machine Config Wizard**
  - Steps: Machine Type → Axes → Switches → Spindle → Coolant → ATC → Summary
  - Generates `/machines/<profile>/ini` + `/hal` from templates
  - Optionally sets `[RS274NGC] REMAP` for probing/ATC

**Acceptance Criteria**
- Create mapping (e.g., CycleStart→`hm2_7i76e.0.7i76.0.0.input-00`) and apply with clean reload.
- Wizard produces a runnable sim profile; app restarts into it.

**Deliverables**
- PinMap widget, YAML format, Jinja2 templates, wizard UI, rollback logic.

---

### Phase 3 — IO, Diagnostics, Jogging & MPG
**Goals**
- Real‑time IO view, diagnostics, safe output forcing; comprehensive jog/MPG.

**Tasks**
- IO Panel
  - Group by card/subsystem; live state; pulse/edge indicators; debounce display
  - Output forcing allowed only when `Machine On && !ESTOP`
  - Batch test scripts for user hardware verification
- Diagnostics
  - Live errors, HAL component list, loaded pins, thread rates, task latency
  - Export “support bundle” (logs, INI, HAL, pinmap, dmesg excerpt)
- Jog/MPG
  - Axis selector, increments (cont/1.0/0.1/0.01/0.001), continuous jog rate slider
  - On‑screen MPG wheel w/ acceleration
  - USB/Bluetooth MPG mapping; detent‑to‑feed mapping; configurable safety (require “Enable”)

**Acceptance Criteria**
- Sim inputs toggle & reflect correctly; forced outputs gated by safety.
- Jogging moves DRO as expected; MPG mock events jog in sim.

**Deliverables**
- IO & Diagnostics screens; MPG support docs; support bundle script.

---

### Phase 4 — Probing & Tool Setting
**Goals**
- Guided, safe probing flows and tool length setting that write offsets/tool table.

**Tasks**
- Probing wizards:
  - **Edges** X/Y (single, pair), **corner** (inside/outside), **boss/pocket** center, **hole** center, **Z touch‑off**
  - Visual diagram, safety checklist, dry‑run travel preview
  - Parameters: probe dia, approach feed, clearance, retract distances
- Toolsetter wizard:
  - Fixed touch‑off pad; safe height; update `tool.tbl` length
  - Optional breakage check (consecutive mismatches trigger alarm)
- Calibration:
  - Probe tip diameter calibration against known feature
  - Optional runout compensation (recorded as wizard meta)

**Acceptance Criteria**
- Probing routines update the active WCS (e.g., G54) in sim correctly.
- Toolsetter updates tool length; persisted in `tool.tbl`.
- Cancel/abort safely retracts and restores modes.

**Deliverables**
- NGC macros (`/wizards/probing/*.ngc`), UI flows, offset writers, calibration records.

---

### Phase 5 — ATC Management
**Goals**
- Multi‑style ATC support (carousel/linear) with state machine, recovery, and M6 remap UI.

**Tasks**
- ATC panel
  - Pocket map grid; assign tool→pocket; pocket state (empty, tool#, fault)
  - State tiles: Ready/Busy/Fault; interlock status (door/air/encoder)
- M6 Remap
  - `REMAP=M6 modalgroup=6 ngc=atc_change`
  - UI shows “in‑progress” with step logs; allow safe pause/cancel where legal
- Recovery wizard
  - Resume mid‑change; reconsider sensors; home ATC; manual jog to pocket

**Acceptance Criteria**
- Sim change `M6 Tn` updates DRO tool and pocket map as the sequence runs.
- Recovery wizard clears simulated jam/fault and returns to Ready.

**Deliverables**
- ATC NGC scripts, remap INI lines, ATC panel, recovery playbook.

---

### Phase 6 — Job Manager, File Browser & Conversational
**Goals**
- Manage programs and queue; conversational programming for common ops.

**Tasks**
- File Browser
  - Roots: local profile dir + mounted shares (SMB/NFS via `/scripts/mount_*`)
  - Preview using gremlin; metadata (modified, size, last run)
  - “Open containing folder” and “Duplicate to profile” actions
- Job Manager
  - Queue add/remove/reorder; run/hold/skip; persistent queue JSON
  - Job run history w/ status & duration
- Conversational
  - Facing; drilling/peck; circular/rect pockets; slots; bolt circles
  - Parameter UI → generate G‑code plus `.json` sidecar for re‑edit
  - Post templates for metric/imperial

**Acceptance Criteria**
- Queue three demo jobs → run sequentially with proper state transitions.
- Generate conversational pocket program → sim executes; preview matches.

**Deliverables**
- Job queue persistence; file preview; conversational templates & forms.

---

### Phase 7 — Safety, Homing, Limits, Overrides & Warmup
**Goals**
- Provide homing guidance, soft‑limit bypass flow, spindle warmup & maintenance timers.

**Tasks**
- Homing Manager
  - Per‑axis homed status; guide to home before jog/run; configurable order
- Limits
  - Soft‑limit hit → modal dialog with countdown; require explicit confirmation & reason
  - Time‑boxed bypass with auto‑revert
- Warmup
  - Configurable RPM ladder & durations; progress and stop button
  - Log spindle‑hours for maintenance
- Maintenance
  - Alerts based on hours/elapsed time; snooze/reschedule; checklist items

**Acceptance Criteria**
- Unhomed jog prompts homing dialog in sim.
- Soft‑limit triggers prompt; bypass permits limited action; auto‑reverts.
- Warmup sequence runs; spindle‑hours counter increments.

**Deliverables**
- Warmup NGC scripts; maintenance ledger (JSON); homing flows.

---

### Phase 8 — Offsets, Tool Table, Fixture Library
**Goals**
- Full offset editing, tool table CRUD, and simple fixture/WCS library.

**Tasks**
- Offsets grid
  - G54–G59.3 + G92; copy/paste & import/export CSV
  - Delta‑apply (apply measured deltas to a WCS)
- Tool Table editor
  - Add/remove; radius/length/notes; bulk ops; CSV import/export
- Fixture library
  - Named WCS presets with notes & thumbnails; apply to machine

**Acceptance Criteria**
- Changing offsets immediately reflects in `stat` and gremlin drawing.
- Tool table edits persist to `tool.tbl` and are respected in program runs.
- Export/import round‑trips cleanly.

**Deliverables**
- Offset/Tool editors; CSV schema; fixture library UI & store.

---

### Phase 9 — Settings, Profiles & Network
**Goals**
- Separate machine/operator settings; easy profile lifecycle; share mounts; backups.

**Tasks**
- Profiles
  - Create/clone/delete; profile bundle = INI + HAL + YAML + pinmap
  - Switch profile → restart app into new environment
- Settings
  - Units, UI scale, theme, touchscreen mode, language placeholder
- Network
  - SMB/NFS mount manager (scripted helpers, credentials vault file)
- Backup/Restore
  - Zip/unzip profile + app settings; factory reset

**Acceptance Criteria**
- Creating a new profile yields runnable sim with defaults.
- Mount manager reveals share in File Browser; persists across restarts.
- Backup archive restores identical environment on fresh start.

**Deliverables**
- Profile manager UI; mount scripts; backup/restore CLI.

---

### Phase 10 — Telemetry, Docs, Help & Packaging
**Goals**
- Operational readiness: logging, telemetry, docs, CI, packaged builds.

**Tasks**
- Logging
  - Python `logging` per subsystem; rotating file handler; user‑configurable levels
- Telemetry (local only by default)
  - Render status timeline/events; export CSV/JSON; off by default
- Docs
  - `/docs/` with Quick Start, Probing, ATC, Job Manager, Settings, Troubleshooting
  - “?” help overlay on each screen with contextual tips
- CI & Packaging
  - GitHub Actions: lint (ruff/black/mypy), pytest, pytest‑qt, sim smoke
  - Build AppImage & .deb; attach to Releases

**Acceptance Criteria**
- CI green on main; artifacts (AppImage/.deb) produced and runnable.
- Help overlay shows per‑widget hints; docs contain updated screenshots.

**Deliverables**
- CI workflows, packaging scripts, docs site (mkdocs or Sphinx), screenshots.

---

## 8) v0.1 Milestone — Definition of Done

- **Screens**: Home/Dashboard, Job/File Manager, IO/Diagnostics, Probing (Z + corner), Offsets/Tool Table basics.
- **Safety**: ESTOP flow, Homing Manager, Soft‑limit prompt, Warmup program.
- **Sim**: Reference sim machine fully functional; example jobs & probing macros.
- **Quality**: CI lint + unit/UI/sim smoke tests passing; quick‑start docs & screenshots.
- **Packaging**: AppImage artifact launches sim successfully.

---

## 9) Testing & QA

- **Unit/UI**: pytest, pytest‑qt for widget signals/slots; snapshot key screens.
- **Sim Smoke**: Headless `linuxcnc -ini ...` run three demo jobs; verify pins & states.
- **Wizard Tests**: Probe macros with pseudo contacts; assert offsets/tool table writes.
- **ATC Sim**: drive simulated pins; verify pocket map & state machine transitions.
- **Performance**: UI thread responsive under IO spam; jog latency target < 50 ms.
- **Recovery**: HAL reload rollback tests; mid‑ATC recovery; probe abort safe retract.

---

## 10) Logging & Diagnostics

- Log to `~/.pb-touch/logs/YYYY-MM-DD.log` with subsystem prefix.
- Error reports include: app version, OS, LinuxCNC version, INI/HAL summary, recent events (last 200 lines).
- “Support Bundle” ZIP contains logs, INI/HAL, pinmap YAML, and journalctl excerpt.

---

## 11) Internationalization & Accessibility

- Wrap user‑visible strings with Qt translation hooks.
- Provide alt text/descriptions for icons; ensure high contrast themes.
- Keyboard navigation for all actionable controls; large controls for touch.

---

## 12) Packaging & Distribution

- **AppImage**: self‑contained bundle; first‑run downloads sim profile if missing.
- **Debian package**: installs to `/opt/pb-touch` with desktop entry; optional udev rules helper.
- Release notes enumerate supported hardware templates & known issues.

---

## 13) Contribution Workflow

- Each **Phase** has a GitHub issue; PRs must reference the phase and tick checklists.
- Keep UI changes in `.ui` + QSS where possible; expose bindings in YAML.
- All HAL/INI changes go through templates & documented diffs.

---

## 14) Reference Snippets

**A) HAL gated block template (Jinja2):**
```jinja
# --- PB-TOUCH GENERATED (do not edit) ---
# begin: {{ block_id }}
{% for line in lines %}{{ line }}
{% endfor %}
# end: {{ block_id }}
```

**B) Example NGC (corner probe):**
```ngc
o<probe_corner_xy> sub
  (params: #<_safe_z> #<_probe_feed> #<_tip_dia>)
  G91
  G38.2 X20 F[#<_probe_feed>]
  G1 X-2
  G38.2 X20 F[#<_probe_feed>]
  (compute X0 from trip pos + tip radius)
  (repeat for Y)
  (write #5221/#5222 offsets for G54)
  G90
o<probe_corner_xy> endsub
M2
```

**C) Warmup sequence (excerpt):**
```ngc
o<spindle_warmup> sub
  (rpm ladder from ini or yaml: 1000/2000/4000/6000)
  M3 S1000
  G4 P60
  M3 S2000
  G4 P60
  M3 S4000
  G4 P120
  M5
o<spindle_warmup> endsub
M2
```

**D) GitHub Actions (CI smoke outline):**
```yaml
name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.10' }
      - run: pip install -r requirements-dev.txt
      - run: ruff check . && black --check . && mypy .
      - run: pytest -q
```

---

## 15) Glossary

- **HAL**: Hardware Abstraction Layer; wiring pins ↔ signals ↔ components.
- **INI**: LinuxCNC machine configuration (kinematics, limits, UI options).
- **NGC**: RS274NGC macros (G‑code subroutines) used for probing, ATC, warmup.
- **QtPyVCP**: Qt‑based framework enabling Python/Qt UIs for LinuxCNC.
- **Probe Basic**: Popular QtPyVCP skin; PB‑Touch builds on its concepts.

---

## 16) Copilot Usage Tips

- Use this doc to infer **file locations** and **widget/hal bindings**.
- Generate `.ui` first, then wire via `/config/pb_touch.yaml`.
- Prefer **stat/halui** sources/sinks; avoid hard‑coding pins in Python.
- For macros, emit `.ngc` to `/wizards/…` and register via INI remaps.
- Keep PRs aligned with **Phase acceptance criteria**; attach screenshots.

---

_© PB‑Touch contributors. Licensed under an open license compatible with LinuxCNC ecosystem (e.g., GPLv2+)._
