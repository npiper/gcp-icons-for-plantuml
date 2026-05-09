# Pull Request: v2 — Dual-Sprite Builder (SVG + PNG), 216 Icons, v1 Archive

## Summary

This PR overhauls the GCP Icons for PlantUML fork to work with modern PlantUML
(tested against 1.2026.3). The v2 builder generates dual-sprite `.puml` files
containing both a full-colour SVG sprite and a grayscale 128×128 PNG sprite per
icon. Users can choose the appropriate mode for their environment.

The v1 pipeline is preserved in `archive/v1/` for reference. The v1 category
taxonomy is removed entirely — `dist/` is now flat, mirroring Google's own
product-per-directory structure.

---

## What Changed

### New: `scripts/icon-builderv2.py`

Replaces `icon-builder.py` for v2 icon generation.

**Java 18+ and `plantuml.jar` are required at build time** (for PNG sprite
encoding). Set `JAVA_HOME` before running.

Key processing pipeline per icon:

1. **scour pre-pass** — strips editor metadata, XML comments, unused `<defs>`,
   shortens IDs, normalises the viewport, converts `style=` attributes to SVG
   presentation attributes.
2. **CSS class inlining** — resolves `.cls-1{fill:#aecbfa}` + `class="cls-1"`
   patterns into `fill="#aecbfa"` presentation attributes, which PlantUML's SAX
   parser requires.
3. **PlantUML SAX compatibility fixes** — strips `fill-rule`, `clip-rule`,
   `clip-path` and `mask` (unsupported by the SAX parser); converts `<polygon>`
   to equivalent `<path>` elements (crash workaround; see bug fix section).
4. **Minification** — sets `width="72" height="72"` on the root `<svg>` (keeps
   `viewBox` for path scaling), serialises to a compact single-line string.
   The explicit size tells PlantUML's layout engine how much space to reserve,
   matching the 72px PNG sprite target.
5. **PNG resize** — source PNG thumbnail to 72×72 (longest side, white
   background, Pillow LANCZOS). Keeps full-size PNG in `dist/` separately.
6. **PNG sprite encoding** — encodes the resized PNG via `plantuml.jar` to
   produce a `[128x128/16z]` base64 sprite.

### New: `scripts/configv2.yml`

Replaces the old per-category `config.yml`. Maps 216 GCP product icons from
`source/official/` SVG directories to their `dist/` target names and colours.

### New: `dist/` — flat dual-sprite layout

| | v1 | v2 |
|---|---|---|
| Format | PNG base64 sprite only | SVG sprite + PNG sprite (both per file) |
| Layout | Nested subdirs by category | Flat — all 220 files at `dist/` root |
| Java at build time | Required | Required (Java 18+ for PNG encoding) |
| Java at render time | Required | Required (PlantUML itself) |
| PlantUML pragma | None | `!pragma svgparser sax` (local SVG mode) |
| PNG mode | All diagrams | `!define GCP_USE_PNG` before includes |
| Icon count | ~155 | 216 |
| Colour (SVG) | Monochrome | Full colour (two-tone GCP palette) |
| Colour (PNG) | — | Grayscale 128×128 |

Each `.puml` file in `dist/` contains:
- An `!ifdef GCP_USE_PNG` / `!else` block switching between PNG and SVG sprites
- PNG sprite: `sprite $name_png [72x72/16z] { ... }`
- SVG sprite: `sprite $name <svg viewBox="0 0 24 24" width="72" height="72">...</svg>`
- `GCPEntityColoring(name)` macro
- 3-arg and 4-arg `name(alias, label, techn)` component macros — both PNG and
  SVG branches use the plain sprite name (no scale multiplier needed; size is
  set by the sprite dimensions directly)
- `nameParticipant(alias, label, techn)` sequence macros

### Updated: `GCPSymbols.md`

Regenerated icon index listing all 216 v2 icons with their macro names and
`.puml` filenames.

### Updated: `scripts/requirements.txt`

Added `scour>=0.38.2` (SVG pre-processing) and `Pillow>=6.2.0` (PNG resize).

### Updated: `README.md`

Fully rewritten. Now covers:
- Why v2 is a breaking change (flat layout rationale)
- Migration table from v1 include paths and macro names to v2
- Getting Started with remote `!includeurl` and local `!include` examples
- Usage examples with generated SVG previews in `docs/images/`
- Sprite mode guide (PNG vs SVG)
- v1 Reference Archive section

The previous `README-v2.md` draft has been deleted (content merged in).

### New: `docs/images/`

Seven rendered SVG example diagrams, generated from `examples/*.puml`:

| File | Source |
|------|--------|
| `Hello World.svg` | `examples/HelloWorld.puml` |
| `Basic Usage - GCP IoT Rules Engine.svg` | `examples/Basic Usage.puml` |
| `Raw usage - Sprites.svg` | `examples/Raw Sprite Usage.puml` |
| `Two Modes - Simple View.svg` | `examples/Two Modes - Simple View.puml` |
| `Two Modes - Technical View.svg` | `examples/Two Modes - Technical View.puml` |
| `Sprite Mode - PNG fallback (v2 local).svg` | `examples/Sprite Mode - PNG.puml` |
| `Sprite Mode - SVG (v2).svg` | `examples/Sprite Mode - SVG.puml` |

### Updated: `examples/` — all original examples rewritten for v2

All five original v1 example files updated to use the v2 remote URL, flat
include paths, `!define GCP_USE_PNG`, `!includeurl`, and snake_case macro names:

| File | Key changes |
|------|-------------|
| `examples/HelloWorld.puml` | v2 URL, `cloud_code`, `cloud_storage` |
| `examples/Basic Usage.puml` | `iot_core`, `pubsub` |
| `examples/Raw Sprite Usage.puml` | `vertexai_png`, `iot_core_png` sprites |
| `examples/Two Modes - Simple View.puml` | `cloud_endpoints`, `app_engine`, `GCPSimplified.puml` |
| `examples/Two Modes - Technical View.puml` | `cloud_endpoints`, `app_engine` (no simplified) |

Two new example files demonstrating both sprite modes:

| File | Description |
|------|-------------|
| `examples/Sprite Mode - PNG.puml` | PNG mode via `!define GCP_USE_PNG` + `!includeurl` |
| `examples/Sprite Mode - SVG.puml` | SVG mode via `!define GCPPuml` + `!includeurl` |

### New: `archive/v1/`

v1 files preserved for reference when upgrading existing diagrams:

| File | Description |
|------|-------------|
| `archive/v1/README.md` | Original v1 README |
| `archive/v1/config.yml` | v1 category mapping config |
| `archive/v1/icon-builder.py` | Original v1 builder |
| `archive/v1/requirements.txt` | v1 Python dependencies |
| `archive/v1/scripts-README.md` | v1 build instructions |

`scripts/icon-builder.py` and `scripts/config.yml` have been removed from
`scripts/` (git-tracked deletion).

---

## Bug Fixes (PlantUML upstream)

### SVG polygon space-separated coordinates crash

**Symptom:** Two or more GCP sprites in the same diagram rendered as a blank
image (Integer.MAX_VALUE bounding box).

**Root cause:** `SvgSaxParser.handlePolyShape` split the `points` attribute by
whitespace then by comma, only accepting `x,y x,y` format. GCP SVGs use
`x y x y` (whitespace-only separator), which is explicitly valid per SVG 1.1
§9.7.1 — `comma-wsp: (wsp+ comma? wsp*)` means whitespace alone is sufficient.

**Fix (PlantUML source):** `handlePolyShape` now uses a regex numeric token
extractor that handles all valid SVG point formats: `x,y x,y`, `x y x y`,
`x,y,x,y`, and mixed.

**Workaround (builder):** `_convert_polygons_to_paths()` in `icon-builderv2.py`
converts every `<polygon points="...">` to an equivalent `<path d="M x y L x y Z">`.
The `dist/` files are safe even when rendered with an older jar that has the bug.

---

## Usage

### Building icons

```bash
cd scripts/
pip3 install -r requirements.txt
JAVA_HOME=/path/to/jdk18 python3 icon-builderv2.py --check-env
JAVA_HOME=/path/to/jdk18 python3 icon-builderv2.py
```

### Using in a diagram (remote — any PlantUML version)

```plantuml
@startuml My Architecture
!define GCPPuml https://raw.githubusercontent.com/npiper/gcp-icons-for-plantuml/refs/heads/feature/2026-update/dist
!define GCP_USE_PNG
!includeurl GCPPuml/GCPCommon.puml
!includeurl GCPPuml/cloud_run.puml
!includeurl GCPPuml/pubsub.puml

cloud_run(myService, "My Service", "Cloud Run")
pubsub(myQueue, "Events", "Pub/Sub")

myService --> myQueue
@enduml
```

### Using in a diagram (local — SVG mode, full colour)

```plantuml
@startuml My Architecture
!pragma svgparser sax
!define GCPPuml path/to/dist
!include GCPPuml/GCPCommon.puml
!include GCPPuml/cloud_run.puml
!include GCPPuml/pubsub.puml

cloud_run(myService, "My Service", "Cloud Run")
pubsub(myQueue, "Events", "Pub/Sub")

myService --> myQueue
@enduml
```

**Requirements:**
- PlantUML **1.2026.3** (the only version this has been tested against)
- For SVG sprites: `!pragma svgparser sax` before any `!include` (local only)
- For PNG sprites: `!define GCP_USE_PNG` before any include (remote or local)

---

## Testing

> **Note:** All testing was done against **plantuml-1.2026.3.jar** with Java 18.

```bash
cd gcp-icons-for-plantuml

# Regenerate all example SVGs into docs/images/
JAVA=/Library/Java/JavaVirtualMachines/jdk-18.jdk/Contents/Home/bin/java
$JAVA -Djava.awt.headless=true -Dapple.awt.UIElement=true \
  -jar scripts/plantuml.jar -tsvg -o docs/images examples/*.puml
```
