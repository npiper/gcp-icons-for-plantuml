#!/usr/bin/env python3
# Copyright (c) 2026 Neil Piper (fork maintainer)
# Original copyright (c) 2020 David Holsgrove
# SPDX-License-Identifier: MIT (For details, see LICENSE-CODE)

"""icon-builderv2.py: Build GCP Icons for PlantUML using SVG sprites (v2).

Differences from icon-builder.py (v1):
  - No Java / plantuml.jar dependency.
  - No Pillow / PNG processing.
  - Reads SVG source files directly from source/official/.
  - Inlines CSS class-based fill colours into element style attributes so
    that PlantUML's SAX parser can render them correctly.
  - Emits sprite definitions using PlantUML's native SVG sprite syntax:
        sprite $target_name <svg ...>...</svg>
  - Adds '!pragma svgparser sax' to every generated .puml file.
  - Writes all output flat into dist/ (one .puml per product, no subdirs).
  - Requires only PyYAML (already in requirements.txt).
"""

import os
import re
import sys
import shutil
import argparse
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from subprocess import PIPE

from PIL import Image

import yaml
from scour import scour as _scour_lib

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CONFIG_FILE = "configv2.yml"

PUML_LICENSE_HEADER = """\
' Copyright (c) 2026 Neil Piper (fork maintainer)
' Copyright (c) 2020 David Holsgrove
' SPDX-License-Identifier: MIT (For details, see LICENSE-CODE)
"""

MARKDOWN_PREFIX_TEMPLATE = """\
<!--
Copyright (c) 2026 Neil Piper (fork maintainer)
Copyright (c) 2020 David Holsgrove
SPDX-License-Identifier: MIT (For details, see LICENSE-CODE)
-->
# GCP Symbols (v2 — SVG sprites)

The table below lists all GCP symbols in the `dist/` directory.

Include syntax:
```
!include <gcp/GCPCommon>
!include <gcp/cloud_run>
```

Product | Macro Name | Image (SVG) | PUML file
--- | --- | :---: | ---
"""

# XML namespace used in GCP SVGs — strip for cleaner sprite output
SVG_NS = "http://www.w3.org/2000/svg"

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

parser = argparse.ArgumentParser(
    description="Generates GCP SVG sprite icons for PlantUML (v2)"
)
parser.add_argument(
    "--check-env",
    action="store_true",
    default=False,
    help="Verifies all dependencies met to process icons",
)
args = vars(parser.parse_args())

config = {}
JAVA_BIN = "java"  # resolved in verify_environment

# ---------------------------------------------------------------------------
# Environment verification
# ---------------------------------------------------------------------------

def verify_environment():
    """Check working directory, config file, source directory, and Java."""
    global config, JAVA_BIN

    # Resolve java binary — respect JAVA_HOME if set
    java_home = os.environ.get("JAVA_HOME")
    JAVA_BIN = str(Path(java_home) / "bin" / "java") if java_home else "java"

    cur_dir = Path(".").absolute()
    if cur_dir.parts[-2:] != ("gcp-icons-for-plantuml", "scripts"):
        print(
            "Working directory for icon-builderv2.py must be "
            "gcp-icons-for-plantuml/scripts"
        )
        sys.exit(1)

    if not Path(CONFIG_FILE).exists():
        print(f"Config file '{CONFIG_FILE}' not found. Run from the scripts/ directory.")
        sys.exit(1)

    try:
        with open(CONFIG_FILE) as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"Error reading {CONFIG_FILE}: {e}")
        sys.exit(1)

    official = Path("../source/official")
    if not official.exists() or not any(official.iterdir()):
        print(
            "source/official must contain product icon directories. "
            "See README for setup instructions."
        )
        sys.exit(1)

    # Verify plantuml.jar + java are available (needed for PNG sprite encoding)
    plantuml_jar = Path("plantuml.jar")
    if not plantuml_jar.exists():
        print("plantuml.jar not found in scripts/ — required for PNG sprite encoding")
        sys.exit(1)
    try:
        result = subprocess.run(
            [JAVA_BIN, "-Djava.awt.headless=true", "-Dapple.awt.UIElement=true",
             "-jar", "plantuml.jar", "-version"],
            stdout=PIPE, stderr=PIPE
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.decode())
    except Exception as e:
        print(f"Error executing plantuml.jar with '{JAVA_BIN}': {e}")
        print("Set JAVA_HOME to a Java 11+ installation and retry.")
        sys.exit(1)

    if args["check_env"]:
        print("Prerequisites met, exiting")
        sys.exit(0)


# ---------------------------------------------------------------------------
# dist/ management
# ---------------------------------------------------------------------------

def clean_dist():
    """Remove and recreate the dist/ directory."""
    path = Path("../dist")
    if path.exists():
        shutil.rmtree(path)
    os.mkdir(path)


def copy_puml():
    """Copy source/*.puml files into dist/."""
    for f in Path("../source").glob("*.puml"):
        shutil.copy(f, Path("../dist"))


# ---------------------------------------------------------------------------
# SVG processing
# ---------------------------------------------------------------------------

# Register the SVG namespace so ElementTree does not add ns0: prefixes.
ET.register_namespace("", SVG_NS)


def _parse_css_classes(style_text):
    """Parse a <style> block and return {class_name: {prop: value}} dict.

    Handles simple rules like:
        .cls-1{fill:#aecbfa;}
        .cls-1,.cls-2{fill-rule:evenodd;}
    """
    classes = {}
    # Match one or more selectors followed by a declaration block
    rule_re = re.compile(r'([^{]+)\{([^}]*)\}')
    for match in rule_re.finditer(style_text):
        selectors = match.group(1).strip()
        declarations = match.group(2).strip()

        # Parse declarations into a dict
        props = {}
        for decl in declarations.split(";"):
            decl = decl.strip()
            if ":" in decl:
                prop, _, val = decl.partition(":")
                props[prop.strip()] = val.strip()

        # Apply to each selector
        for sel in selectors.split(","):
            sel = sel.strip()
            if sel.startswith("."):
                cls = sel[1:]  # strip leading dot
                if cls not in classes:
                    classes[cls] = {}
                classes[cls].update(props)
    return classes


def _inline_css_classes(root, class_map):
    """Walk the element tree and replace class="..." with presentation attributes.

    PlantUML's SAX parser does not understand CSS style= attributes, so we
    convert everything to SVG presentation attributes (fill="X", fill-rule="Y").
    """
    for elem in root.iter():
        cls_attr = elem.get("class")
        if not cls_attr:
            continue
        merged = {}
        for cls_name in cls_attr.split():
            if cls_name in class_map:
                merged.update(class_map[cls_name])
        if not merged:
            continue
        # Set as presentation attributes, not style=
        for prop, val in merged.items():
            if not elem.get(prop):  # don't override existing presentation attrs
                elem.set(prop, val)
        del elem.attrib["class"]



def _strip_element_by_tag(root, tag):
    """Remove all elements with the given local tag name (without namespace)."""
    # Collect first, then remove (cannot modify tree during iteration)
    ns_tag = f"{{{SVG_NS}}}{tag}"
    plain_tag = tag
    parents = {}
    for parent in root.iter():
        for child in list(parent):
            local = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if local == tag:
                parents.setdefault(id(parent), (parent, []))[1].append(child)
    for _, (parent, children) in parents.items():
        for child in children:
            parent.remove(child)


def _strip_attr(root, attr):
    """Remove a given attribute from all elements in the tree."""
    for elem in root.iter():
        elem.attrib.pop(attr, None)


def _convert_polygons_to_paths(root):
    """Convert <polygon points="..."> elements to <path d="..."> elements.

    PlantUML's SAX SVG parser crashes (Integer.MAX_VALUE dimensions) when two
    or more SVG sprites that contain <polygon> elements are used in the same
    diagram. Converting polygon to an equivalent closed path avoids this bug.
    """
    for parent in root.iter():
        for i, child in enumerate(list(parent)):
            local = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if local != "polygon":
                continue
            points_str = child.get("points", "")
            # Parse point pairs (space or comma separated)
            tokens = re.split(r'[\s,]+', points_str.strip())
            coords = []
            it = iter(tokens)
            for x, y in zip(it, it):
                coords.append((x, y))
            if not coords:
                continue
            d = "M " + " L ".join(f"{x} {y}" for x, y in coords) + " Z"
            # Build <path> with same attributes minus points
            ns_prefix = child.tag[: child.tag.index("}") + 1] if "}" in child.tag else ""
            path_elem = ET.Element(f"{ns_prefix}path")
            for attr, val in child.attrib.items():
                if attr != "points":
                    path_elem.set(attr, val)
            path_elem.set("d", d)
            parent[i] = path_elem


def _to_single_line(svg_string):
    """Collapse whitespace between tags to produce a compact single-line SVG."""
    # Collapse runs of whitespace (including newlines) to a single space
    svg_string = re.sub(r'\s+', ' ', svg_string)
    # Remove spaces immediately inside tag brackets: '< ' -> '<', ' >' -> '>'
    svg_string = re.sub(r'<\s+', '<', svg_string)
    svg_string = re.sub(r'\s+>', '>', svg_string)
    svg_string = re.sub(r'\s+/>', '/>', svg_string)
    return svg_string.strip()


def _scour_svg(svg_text):
    """Run scour on raw SVG text to remove editor metadata, comments, unused
    defs, and redundant whitespace before our ElementTree pipeline runs.

    Equivalent to:
        scour -i input.svg -o output.svg --enable-viewboxing \\
              --enable-id-stripping --enable-comment-stripping \\
              --shorten-ids --indent=none
    """
    opts = _scour_lib.generateDefaultOptions()
    opts.enable_viewboxing = True   # normalise viewport
    opts.strip_ids = True           # remove unused id= attributes
    opts.shorten_ids = True         # shorten remaining ids
    opts.strip_comments = True      # remove <!-- --> comments
    opts.indent_type = "none"       # no indentation → compact output
    opts.newlines = False           # no newlines → single line output
    opts.strip_xml_prolog = True    # remove <?xml ...?> declaration
    opts.remove_titles = True       # remove <title> elements
    opts.remove_descriptions = True # remove <desc> elements
    opts.remove_metadata = True     # remove <metadata> elements
    opts.remove_descriptive_elements = True
    opts.style_to_xml = True        # convert style="fill:X" → fill="X" presentation attrs
    opts.quiet = True               # suppress scour's progress output
    return _scour_lib.scourString(svg_text, opts)


def minify_svg_for_sprite(svg_path):
    """Read an SVG file and return a minified single-line string suitable
    for use as a PlantUML SVG sprite.

    Processing steps:
    0. Pre-process with scour: strips comments, editor metadata, unused defs,
       converts style= attributes to presentation attributes, removes title/desc.
    1. Parse with ElementTree.
    2. Extract CSS class rules from any remaining <defs><style> blocks and
       inline them as presentation attributes (scour does not resolve class= rules).
    3. Remove remaining <defs> elements.
    4. Strip unsupported SVG features: fill-rule, clip-rule, clip-path, mask
       (PlantUML SAX parser cannot handle these).
    5. Convert <polygon> to <path> (SAX parser crash workaround).
    6. Remove width/height from root; keep viewBox for scaling.
    7. Serialise to a compact single-line string.
    """
    # --- 0. Pre-process with scour ---
    try:
        raw_text = Path(svg_path).read_text(encoding="utf-8")
    except OSError as e:
        print(f"WARNING: Could not read {svg_path}: {e} — skipping")
        return None
    try:
        scoured_text = _scour_svg(raw_text)
    except Exception as e:
        print(f"WARNING: scour failed on {svg_path}: {e} — using raw input")
        scoured_text = raw_text

    # --- 1. Parse the scoured SVG ---
    try:
        root = ET.fromstring(scoured_text)
    except ET.ParseError as e:
        print(f"WARNING: Could not parse {svg_path}: {e} — skipping")
        return None


    # --- 1. Collect CSS class rules from <defs><style> ---
    class_map = {}
    ns = {"svg": SVG_NS}

    # Find all <style> elements anywhere in the tree
    for style_elem in root.iter(f"{{{SVG_NS}}}style"):
        if style_elem.text:
            class_map.update(_parse_css_classes(style_elem.text))

    # --- 2. Inline CSS class fills into element presentation attributes ---
    if class_map:
        _inline_css_classes(root, class_map)

    # --- 3. Remove <defs> elements ---
    # title, desc, metadata already removed by scour in step 0.
    _strip_element_by_tag(root, "defs")

    # --- 4. Strip noisy attributes and unsupported SVG features ---
    for attr in ("data-name", "xmlns:xlink", "xml:space"):
        _strip_attr(root, attr)
    # PlantUML's SAX SVG parser does not support fill-rule or clip-rule;
    # strip them entirely to avoid silent rendering errors.
    _strip_attr(root, "fill-rule")
    _strip_attr(root, "clip-rule")
    # clip-path references url(#id) into <defs>; defs are stripped in step 3,
    # so dangling clip-path refs would render shapes unclipped. Strip the refs.
    _strip_attr(root, "clip-path")
    # <mask> elements are not supported by PlantUML's SAX parser; strip them
    # and any mask= attribute references.
    _strip_element_by_tag(root, "mask")
    _strip_attr(root, "mask")
    # PlantUML's SAX parser crashes (Integer.MAX_VALUE) when two SVG sprites
    # containing <polygon> are used in the same diagram. Convert to <path>.
    _convert_polygons_to_paths(root)

    # Set explicit 72px display size on the root <svg> element; keep viewBox for
    # correct path scaling. PlantUML uses width/height to reserve layout space —
    # without them the viewBox numbers (~24) are used, making SVG sprites much
    # smaller than PNG sprites. 72px matches the PNG sprite target size.
    root.attrib["width"] = "72"
    root.attrib["height"] = "72"
    # Remove xmlns from root (ElementTree re-adds it on serialisation; handled below)

    # --- 5. Serialise ---
    raw = ET.tostring(root, encoding="unicode", xml_declaration=False)

    # ElementTree always emits the namespace as xmlns="..." on the root element.
    # PlantUML's SAX parser accepts this, but stripping it keeps the sprite compact.
    raw = re.sub(r'\s*xmlns="[^"]*"', '', raw, count=1)

    return _to_single_line(raw)


# ---------------------------------------------------------------------------
# PUML generation
# ---------------------------------------------------------------------------

def _resolve_color(entry, category, cfg):
    """Resolve fill color from service entry, then category, then Defaults."""
    color_name = (
        entry.get("Color")
        or category.get("Color")
        or cfg.get("Defaults", {}).get("Category", {}).get("Color")
    )
    if not color_name:
        return "#4284F3"
    colors = cfg.get("Defaults", {}).get("Colors", {})
    return colors.get(color_name, color_name)  # return hex if already hex


def _resize_png_for_sprite(src_path, max_size=72):
    """Return a Path to a temp PNG resized to max_size (longest side), alpha stripped."""
    try:
        img = Image.open(src_path)
        img.thumbnail((max_size, max_size), Image.LANCZOS)
        # Strip alpha — plantuml sprites need an opaque image
        if img.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            alpha = img.split()[-1] if img.mode in ("RGBA", "LA") else None
            bg.paste(img, mask=alpha)
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")
        # Use system temp dir with same filename — plantuml derives the sprite
        # name from the file stem, so keeping the original name is essential.
        tmp = Path(tempfile.gettempdir()) / src_path.name
        img.save(tmp, "PNG")
        return tmp
    except Exception as e:
        print(f"WARNING: PNG resize failed for {src_path}: {e}")
        return src_path  # fallback: encode the original


def _encode_png_sprite(png_path):
    """Call plantuml.jar -encodesprite 16z on a PNG and return the sprite lines."""
    try:
        result = subprocess.run(
            [JAVA_BIN, "-Djava.awt.headless=true", "-Dapple.awt.UIElement=true",
             "-jar", "plantuml.jar", "-encodesprite", "16z", str(png_path)],
            stdout=PIPE, stderr=PIPE
        )
        output = result.stdout.decode("UTF-8").strip()
        if not output:
            print(f"WARNING: plantuml.jar produced no sprite output for {png_path}")
            return None
        return output
    except Exception as e:
        print(f"WARNING: PNG sprite encoding failed for {png_path}: {e}")
        return None


def generate_puml(target, svg_string, color, png_sprite, out_dir):
    """Write a .puml with dual PNG (default) and SVG (!define GCP_USE_SVG) sprites.

    Default (no define): PNG sprite — works with any PlantUML version and remote
    !includeurl.  Sprite name is {target}_png.

    Opt-in SVG: add !pragma svgparser sax and !define GCP_USE_SVG before any
    !include.  Requires PlantUML >= 1.2026.x and local file includes.  Sprite
    name is {target} (no suffix), coloured and scalable.
    """
    p = target + "_png"

    content = PUML_LICENSE_HEADER
    content += "\n"

    if png_sprite:
        # PNG sprite block — default (no define required)
        # Rename the sprite to {target}_png so it coexists with the SVG sprite.
        content += png_sprite.replace(f"sprite ${target} ", f"sprite ${p} ", 1) + "\n"
        content += "\n"
        content += f"GCPEntityColoring({target})\n"
        content += f"!define {target}(e_alias, e_label, e_techn) GCPEntity(e_alias, e_label, e_techn, {color}, {p}, {target})\n"
        content += f"!define {target}(e_alias, e_label, e_techn, e_descr) GCPEntity(e_alias, e_label, e_techn, e_descr, {color}, {p}, {target})\n"
        content += f"!define {target}Participant(p_alias, p_label, p_techn) GCPParticipant(p_alias, p_label, p_techn, {color}, {p}, {target})\n"
        content += f"!define {target}Participant(p_alias, p_label, p_techn, p_descr) GCPParticipant(p_alias, p_label, p_techn, p_descr, {color}, {p}, {target})\n"
        content += "!ifdef GCP_USE_SVG\n"

    # SVG sprite block (opt-in via !define GCP_USE_SVG)
    content += f"sprite ${target} {svg_string}\n"
    content += "\n"
    content += f"GCPEntityColoring({target})\n"
    content += f"!define {target}(e_alias, e_label, e_techn) GCPEntity(e_alias, e_label, e_techn, {color}, {target}, {target})\n"
    content += f"!define {target}(e_alias, e_label, e_techn, e_descr) GCPEntity(e_alias, e_label, e_techn, e_descr, {color}, {target}, {target})\n"
    content += f"!define {target}Participant(p_alias, p_label, p_techn) GCPParticipant(p_alias, p_label, p_techn, {color}, {target}, {target})\n"
    content += f"!define {target}Participant(p_alias, p_label, p_techn, p_descr) GCPParticipant(p_alias, p_label, p_techn, p_descr, {color}, {target}, {target})\n"

    if png_sprite:
        content += "!endif\n"

    out_path = out_dir / f"{target}.puml"
    with open(out_path, "w") as f:
        f.write(content)


# ---------------------------------------------------------------------------
# Main build
# ---------------------------------------------------------------------------

def main():
    verify_environment()

    clean_dist()
    copy_puml()

    out_dir = Path("../dist")
    categories = config.get("Categories", [])

    markdown = MARKDOWN_PREFIX_TEMPLATE
    results = []  # (target, success)

    for cat in categories:
        source_dir = cat.get("SourceDir", cat["Name"])
        services = cat.get("Services", [])

        for svc in services:
            source_png = svc["Source"]               # e.g. "cloud_run.png"
            target = svc["Target"]                   # e.g. "cloud_run"

            # Derive SVG filename from the source PNG name
            source_svg = Path(source_png).stem + ".svg"
            svg_path = Path("../source/official") / source_dir / source_svg

            if not svg_path.exists():
                print(f"WARNING: SVG not found — {svg_path} — skipping {target}")
                results.append((target, False))
                continue

            svg_string = minify_svg_for_sprite(svg_path)
            if svg_string is None:
                results.append((target, False))
                continue

            color = _resolve_color(svc, cat, config)

            # Copy SVG and PNG (if present) into dist/ so they are versioned alongside the .puml
            shutil.copy2(svg_path, out_dir / f"{target}.svg")
            png_path = svg_path.with_suffix(".png")
            png_sprite = None
            if png_path.exists():
                dist_png = out_dir / f"{target}.png"
                shutil.copy2(png_path, dist_png)
                tmp_png = _resize_png_for_sprite(dist_png)
                png_sprite = _encode_png_sprite(tmp_png)
                if tmp_png != dist_png:
                    tmp_png.unlink(missing_ok=True)

            generate_puml(target, svg_string, color, png_sprite, out_dir)

            markdown += f"{target} | {target} | ![{target}](dist/{target}.svg) | {target}.puml\n"
            results.append((target, True))
            print(f"generated {target}.puml")

    # Write GCPSymbols.md
    with open(Path("../GCPSymbols.md"), "w") as f:
        f.write(markdown)

    total = len(results)
    ok = sum(1 for _, s in results if s)
    skipped = total - ok
    print(f"\nDone: {ok}/{total} icons generated, {skipped} skipped.")


if __name__ == "__main__":
    main()
