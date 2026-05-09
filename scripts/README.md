# Generating GCP Icons for PlantUML (v2)

This document describes how to generate the `dist/` directory using the v2 builder (`icon-builderv2.py`).

> **v1 reference:** The original `icon-builder.py`, `config.yml`, and `requirements.txt` are preserved in [`archive/v1/`](../archive/v1/) for reference. The v1 build instructions are in [`archive/v1/scripts-README.md`](../archive/v1/scripts-README.md).

---

## Prerequisites

### Python

Python 3.8+ with the packages listed in `requirements.txt`:

```bash
pip3 install -r requirements.txt
```

Dependencies:

| Package | Purpose |
|---|---|
| `PyYAML` | Reads `configv2.yml` |
| `Pillow` | Resizes PNG source icons to 72×72 for PNG sprites |
| `scour` | Optimises and sanitises SVG source files |

### Java

Java 18+ is required — the bundled `plantuml.jar` (PlantUML 1.2026.x) does not run on Java 8.

Set `JAVA_HOME` to a JDK 18+ installation before running the builder:

```bash
export JAVA_HOME=/path/to/jdk18
```

On macOS with the JDK installed in the default location:

```bash
export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-18.jdk/Contents/Home
```

### GCP Icon Sources

Download the latest [GCP Architecture Icons](https://cloud.google.com/icons) (PNG + SVG assets), unzip, and copy the product icon directories into `source/official/`.

The expected layout after extraction:

```
gcp-icons-for-plantuml/
  source/
    official/
      access_context_manager/
      app_engine/
      artifact_registry/
      bigquery/
      cloud_run/
      ... (one directory per GCP product)
```

Each product directory must contain at least one `.svg` file and one `.png` file matching the directory name.

---

## Configuration: configv2.yml

`configv2.yml` maps each product directory under `source/official/` to an output target name. The v2 config is **flat** — there are no category groups.

Example entry:

```yaml
icons:
  - SourceDir: cloud_run
    Source: cloud_run.png
    Target: cloud_run
    Color: GoogleBlue
```

| Key | Description |
|---|---|
| `SourceDir` | Exact directory name under `source/official/` |
| `Source` | PNG filename inside that directory |
| `Target` | Output file stem — used for `dist/{Target}.puml`, sprite names, and macro names |
| `Color` | PlantUML color name applied to the entity macro |

To generate a config template reflecting whatever is currently in `source/official/`:

```bash
cd scripts
python3 icon-builderv2.py --create-config-template
```

This writes `config-template.yml` to the `scripts/` directory, listing every discovered product directory as an entry. Edit it, rename it to `configv2.yml`, and run the builder.

---

## Running the Builder

From the `scripts/` directory:

```bash
cd scripts

# Verify all prerequisites are met
JAVA_HOME=/path/to/jdk18 python3 icon-builderv2.py --check-env

# Generate dist/
JAVA_HOME=/path/to/jdk18 python3 icon-builderv2.py
```

Or export `JAVA_HOME` once and run both:

```bash
export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-18.jdk/Contents/Home
cd scripts
python3 icon-builderv2.py --check-env
python3 icon-builderv2.py
```

---

## What the Builder Does

For each entry in `configv2.yml`:

1. Reads the source `.svg` from `source/official/{SourceDir}/`.
2. Optimises it with `scour` (strips comments, IDs, normalises viewBox).
3. Inlines CSS fill colours into element `style` attributes so PlantUML's SAX SVG parser renders them correctly.
4. Resizes the source `.png` to 72×72 using Pillow (longest-side thumbnail, white background).
5. Encodes the resized PNG as a PlantUML base64 sprite (`[72x72/16z]`).
6. Writes a single `dist/{Target}.puml` containing:
   - License header
   - The SVG sprite (default, used with local `!include`). The root `<svg>` has
     `width="72" height="72"` so PlantUML reserves the same layout space as the
     PNG sprite, giving consistent icon sizes across both modes.
   - The PNG sprite with `_png` suffix (used when `!define GCP_USE_PNG` is set)
   - Entity macros in snake_case: `!define {Target}(...)`.
7. Copies the full-size `.png` and `.svg` source files to `dist/{Target}.png` / `dist/{Target}.svg`.

After all icons are processed:

- `dist/GCPCommon.puml` is written with shared color constants and macro helpers.
- `dist/GCPSimplified.puml` is written with the simplified-view macro overrides.
- `dist/GCPRaw.puml` and `dist/GCPC4Integration.puml` are written.
- `GCPSymbols.md` is regenerated at the repository root with a full icon reference table.

**Output structure:**

```
dist/
  GCPCommon.puml
  GCPSimplified.puml
  GCPRaw.puml
  GCPC4Integration.puml
  access_context_manager.puml
  access_context_manager.png
  access_context_manager.svg
  app_engine.puml
  app_engine.png
  app_engine.svg
  ... (one set per product)
```

---

## Generating Example SVGs

After regenerating `dist/`, re-render the example diagrams to `docs/images/`:

```bash
JAVA=/Library/Java/JavaVirtualMachines/jdk-18.jdk/Contents/Home/bin/java
$JAVA -Djava.awt.headless=true -Dapple.awt.UIElement=true \
  -jar scripts/plantuml.jar -tsvg -o docs/images examples/*.puml
```

The `-Djava.awt.headless=true -Dapple.awt.UIElement=true` flags suppress the
Java GUI/dock-icon that PlantUML otherwise opens on macOS, even for non-interactive
operations. The builder passes these flags automatically when encoding PNG sprites;
use them here too for a fully silent render.

---

## v1 Archive

The following files have been moved to [`archive/v1/`](../archive/v1/) and are kept for reference only:

| File | Description |
|---|---|
| `archive/v1/icon-builder.py` | Original v1 builder (category-based output) |
| `archive/v1/config.yml` | v1 category mapping configuration |
| `archive/v1/requirements.txt` | v1 Python dependencies (subset of current) |
| `archive/v1/scripts-README.md` | v1 build instructions |

---

## License Summary

Code is made available under the MIT license in `LICENSE-CODE`.

The compiled [PlantUML jar](http://plantuml.com/download), `scripts/plantuml.jar`, is licensed under the MIT license in `LICENSE-CODE`.
