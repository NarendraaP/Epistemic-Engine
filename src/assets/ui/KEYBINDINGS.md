# Epistemic Dashboard - Keybinding Instructions

## Overview

The Epistemic Dashboard implements **Invariant III (Access)** from the Constitution by providing a persistent Heads-Up Display (HUD) that shows which "Truth Filter" is currently active.

---

## Truth Levels

| Key | Level | Name | Color | Description | Visible Layers |
|:---:|:-----:|:-----|:------|:------------|:---------------|
| **1** | L0 | OBSERVED | Blue (#66CCFF) | Pure Measurement | L0 only |
| **2** | L1 | INFERRED | Gold (#FFD700) | Scientific Model | L0 + L1 |
| **3** | L2 | SIMULATED | Red (#FF4444) | Hypothetical | L0 + L1 + L2 (all) |

---

## Keybinding Setup

### Method 1: OpenSpace Configuration File

Add these lines to your OpenSpace configuration file (typically `openspace.cfg` or via user asset):

```lua
-- Load the epistemic dashboard
asset.require('epistemic_engine/epistemic_dashboard')

-- Bind keys 1, 2, 3 to truth levels
openspace.bindKey(
    "1",
    "epistemic_dashboard.set_truth_level(1)",
    "Set epistemic mode to L0 (OBSERVED)"
)

openspace.bindKey(
    "2",
    "epistemic_dashboard.set_truth_level(2)",
    "Set epistemic mode to L1 (INFERRED)"
)

openspace.bindKey(
    "3",
    "epistemic_dashboard.set_truth_level(3)",
    "Set epistemic mode to L2 (SIMULATED)"
)
```

### Method 2: Runtime Keybinding (Console)

If OpenSpace is already running, execute these commands in the Lua console:

```lua
-- Bind key '1' to OBSERVED mode
openspace.bindKey("1", [[
    local dashboard = asset.require('epistemic_engine/epistemic_dashboard')
    dashboard.set_truth_level(1)
]], "OBSERVED mode")

-- Bind key '2' to INFERRED mode
openspace.bindKey("2", [[
    local dashboard = asset.require('epistemic_engine/epistemic_dashboard')
    dashboard.set_truth_level(2)
]], "INFERRED mode")

-- Bind key '3' to SIMULATED mode
openspace.bindKey("3", [[
    local dashboard = asset.require('epistemic_engine/epistemic_dashboard')
    dashboard.set_truth_level(3)
]], "SIMULATED mode")
```

### Method 3: Direct Function Call (Testing)

For testing in the Lua console:

```lua
-- Load dashboard
local dashboard = asset.require('epistemic_engine/epistemic_dashboard')

-- Test truth levels
dashboard.set_truth_level(1)  -- OBSERVED
dashboard.set_truth_level(2)  -- INFERRED
dashboard.set_truth_level(3)  -- SIMULATED
```

---

## Asset Visibility Logic

The dashboard uses a "Gatekeeper" pattern to control which scene assets are visible:

### Level 1: OBSERVED Only
```lua
-- Assets shown:
- EarthInSolarSystem
- EarthHeliocentricTrail
- GaiaStarsObserved

-- Assets hidden:
- SunGalacticOrbitTrail (L1)
- CMBVelocityArrow (L2)
```

### Level 2: OBSERVED + INFERRED
```lua
-- Assets shown:
- All L0 assets (above)
- SunGalacticOrbitTrail (L1)
- SunInGalaxy (L1)
- VerticalOscillationLabel (L1)
- OrbitalPeriodLabel (L1)

-- Assets hidden:
- CMBVelocityArrow (L2)
```

### Level 3: ALL Layers
```lua
-- Assets shown:
- All L0 assets
- All L1 assets
- CMBVelocityArrow (L2)
```

---

## Customization

### Adding New Assets to Registry

Edit `epistemic_dashboard.lua` and add asset identifiers to the appropriate registry:

```lua
local AssetRegistry = {
    OBSERVED = {
        "YourNewL0Asset",  -- Add here
        -- ... existing assets
    },
    
    INFERRED = {
        "YourNewL1Asset",  -- Add here
        -- ... existing assets
    },
    
    SIMULATED = {
        "YourNewL2Asset",  -- Add here
        -- ... existing assets
    }
}
```

### Changing Keybindings

To use different keys (e.g., F1/F2/F3 instead of 1/2/3):

```lua
openspace.bindKey("F1", "epistemic_dashboard.set_truth_level(1)", "OBSERVED")
openspace.bindKey("F2", "epistemic_dashboard.set_truth_level(2)", "INFERRED")
openspace.bindKey("F3", "epistemic_dashboard.set_truth_level(3)", "SIMULATED")
```

---

## Constitution Compliance

✅ **Invariant III (Access)**: "The user must ALWAYS know which Truth Filter is active"

**How we comply:**
1. **Persistent Display**: Console output shows current mode (Screen-space overlay TODO)
2. **Explicit States**: Clear separation between L0/L1/L2 modes
3. **No Blending**: Assets are enabled/disabled explicitly, not faded
4. **User Control**: Direct keybindings give immediate access to truth levels

---

## Troubleshooting

### Assets Not Toggling?

**Check asset identifiers match scene graph:**
```lua
openspace.printInfo(openspace.sceneGraph())  -- List all nodes
```

**Verify asset has Renderable.Enabled property:**
```lua
openspace.printInfo(openspace.property("Scene.YourAssetName.Renderable.Enabled"))
```

### Keybindings Not Working?

**List current keybindings:**
```lua
openspace.printInfo(openspace.keyBindings())
```

**Unbind conflicting key:**
```lua
openspace.clearKey("1")  -- Remove existing binding
-- Then rebind to dashboard
```

### Dashboard Not Loading?

**Check Lua errors in console**
**Verify asset path is correct in `asset.require()`**

---

## Next Steps (Future Enhancement)

Current implementation uses **console output** for HUD display. Future versions should implement:

1. **ScreenSpaceRenderable**: Custom overlay with proper positioning
2. **ImGui Panel**: Native GUI panel in OpenSpace
3. **Color-coded Visual Indicator**: Corner badge showing active mode color
4. **Layer Count**: Show "X/Y objects visible" for each epistemic level

See OpenSpace documentation on GUI scripting for implementation details.

---

## Example Session

```lua
-- 1. Load dashboard
asset.require('epistemic_engine/epistemic_dashboard')

-- 2. Start with OBSERVED mode (default)
--    Console shows: "EPISTEMIC MODE: OBSERVED | Pure Measurement"

-- 3. Press '2' to add INFERRED layer
--    Sun's galactic orbit appears (gold trail)

-- 4. Press '3' to add SIMULATED layer
--    CMB velocity arrow appears (red)

-- 5. Press '1' to return to OBSERVED only
--    Gold and red layers disappear
```

---

## Constitution Reference

> **Invariant III: The Invariant of Access (User Interface)**
> 
> Rule: The "Truth Slider" must be the primary navigation control.
> 
> Constraint: A persistent On-Screen Display (OSD) or Dashboard must indicate the current epistemic filter mode at all times.

This dashboard fulfills this requirement by providing explicit, always-visible state indication and direct user control over epistemic layer visibility.
