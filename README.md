<!--
Copyright (c) 2026 Neil Piper (fork maintainer)
Original copyright (c) 2020 David Holsgrove
SPDX-License-Identifier: MIT (For details, see LICENSE-CODE)
-->

# GCP Icons for PlantUML

PlantUML sprites, macros, and includes for Google Cloud Platform (GCP) services. Used to create PlantUML diagrams with GCP components. All elements are generated from the official [GCP Architecture Icons](https://cloud.google.com/icons).

> **This is a maintained fork of [davidholsgrove/gcp-icons-for-plantuml](https://github.com/davidholsgrove/gcp-icons-for-plantuml),
> updated for the current (2025/2026) GCP icon set. This is a v2 release — include paths and macro names have changed from v1.**

---

## Table of Contents

- [GCP Icons for PlantUML](#gcp-icons-for-plantuml)
  - [Table of Contents](#table-of-contents)
  - [What Changed from v1](#what-changed-from-v1)
  - [Migrating from v1](#migrating-from-v1)
  - [Getting Started](#getting-started)
    - [Using this repository directly (URL)](#using-this-repository-directly-url)
    - [Using local files (after cloning)](#using-local-files-after-cloning)
    - [Via plantuml-stdlib (if/when included)](#via-plantuml-stdlib-ifwhen-included)
  - [Examples](#examples)
    - [Hello World](#hello-world)
    - [Basic Usage](#basic-usage)
    - [Serverless API](#serverless-api)
    - [Data Pipeline](#data-pipeline)
    - [Raw Sprite Usage](#raw-sprite-usage)
    - [Simplified View](#simplified-view)
    - [Technical View](#technical-view)
  - [Sprite Modes: PNG and SVG](#sprite-modes-png-and-svg)
  - [Customised Builds](#customised-builds)
  - [Contributing](#contributing)
  - [License Summary](#license-summary)
  - [Acknowledgements](#acknowledgements)
  - [v1 Reference Archive](#v1-reference-archive)

---

## What Changed from v1

v1 (2020) organised icons into 13 hand-curated category folders:

```
dist/
  AIAndMachineLearning/CloudRun.puml
  Compute/AppEngine.puml
  DataAnalytics/BigQuery.puml
  ...
```

Google's icon set has since grown from ~80 to ~183 products, shipped as **one directory per product** with no grouping layer. The category mapping became a maintenance burden — new products had no obvious category home, and any category reorganisation would silently break existing diagrams.

**v2 removes the category layer entirely**, mirroring Google's own structure:

```
dist/
  cloud_run.puml
  app_engine.puml
  bigquery.puml
  ... (183 products)
```

| | v1 (2020) | v2 (2026) |
|---|---|---|
| Output structure | `dist/{Category}/{ProductName}.puml` | `dist/{product_name}.puml` |
| Naming convention | CamelCase (`CloudRun`, `BigQuery`) | snake_case (`cloud_run`, `bigquery`) |
| Categories | 13 hand-curated groups | None — flat list of products |
| `all.puml` per category | Yes | No |
| Number of icons | ~80 | ~183 |
| Icon source | GCP Architecture Icons 2020 | GCP Architecture Icons 2025/2026 |
| Config file | `scripts/config.yml` | `scripts/configv2.yml` |
| Builder | `scripts/icon-builder.py` | `scripts/icon-builderv2.py` |

---

## Migrating from v1

Replace each include path: old category + CamelCase name → new snake_case product name.

| v1 include | v2 include |
|---|---|
| `!include <gcp/Compute/CloudRun>` | `!include <gcp/cloud_run>` |
| `!include <gcp/Compute/AppEngine>` | `!include <gcp/app_engine>` |
| `!include <gcp/Compute/KubernetesEngine>` | `!include <gcp/google_kubernetes_engine>` |
| `!include <gcp/DataAnalytics/BigQuery>` | `!include <gcp/bigquery>` |
| `!include <gcp/DataAnalytics/CloudPubSub>` | `!include <gcp/pubsub>` |
| `!include <gcp/DataAnalytics/CloudDataflow>` | `!include <gcp/dataflow>` |
| `!include <gcp/Databases/CloudSQL>` | `!include <gcp/cloud_sql>` |
| `!include <gcp/Databases/CloudSpanner>` | `!include <gcp/cloud_spanner>` |
| `!include <gcp/Storage/CloudStorage>` | `!include <gcp/cloud_storage>` |
| `!include <gcp/Networking/CloudLoadBalancing>` | `!include <gcp/cloud_load_balancing>` |
| `!include <gcp/Security/CloudIAM>` | `!include <gcp/identity_and_access_management>` |
| `!include <gcp/DeveloperTools/CloudBuild>` | `!include <gcp/cloud_build>` |
| `!include <gcp/AIAndMachineLearning/AIPlatform>` | `!include <gcp/ai_platform>` |
| `!include <gcp/InternetOfThings/CloudIoTCore>` | `!include <gcp/iot_core>` |
| `!include <gcp/APIManagement/CloudEndpoints>` | `!include <gcp/cloud_endpoints>` |

Macro names change from CamelCase to snake_case to match:

| v1 macro | v2 macro |
|---|---|
| `CloudRun(alias, label, tech)` | `cloud_run(alias, label, tech)` |
| `BigQuery(alias, label, tech)` | `bigquery(alias, label, tech)` |
| `CloudStorage(alias, label, tech)` | `cloud_storage(alias, label, tech)` |
| `AppEngine(alias, label, tech)` | `app_engine(alias, label, tech)` |
| `CloudEndpoints(alias, label, tech)` | `cloud_endpoints(alias, label, tech)` |

The `!define GCPPuml` base URL also changes:

```plantuml
' v1 (old)
!define GCPPuml https://raw.githubusercontent.com/davidholsgrove/gcp-icons-for-plantuml/master/dist

' v2 (new)
!define GCPPuml https://raw.githubusercontent.com/npiper/gcp-icons-for-plantuml/refs/heads/feature/2026-update/dist
```

---

## Getting Started

Include `GCPCommon.puml` first, then any product files you need.

### Using this repository directly (URL)

```plantuml
!define GCPPuml https://raw.githubusercontent.com/npiper/gcp-icons-for-plantuml/refs/heads/feature/2026-update/dist
!includeurl GCPPuml/GCPCommon.puml
!includeurl GCPPuml/cloud_run.puml
!includeurl GCPPuml/cloud_storage.puml
```

> **Note:** PNG sprites are the default — no extra define is needed. They work with all PlantUML versions and remote `!includeurl`. To use full-colour SVG sprites instead, add `!pragma svgparser sax` and `!define GCP_USE_SVG` **before** any `!include`, and use local `!include` (not `!includeurl`). SVG mode requires PlantUML >= 1.2026.x.

### Using local files (after cloning)

```plantuml
!pragma svgparser sax
!define GCP_USE_SVG
!define GCPPuml path/to/dist
!include GCPPuml/GCPCommon.puml
!include GCPPuml/bigquery.puml
```

### Via plantuml-stdlib (if/when included)

```plantuml
!include <gcp/GCPCommon>
!include <gcp/cloud_run>
!include <gcp/bigquery>
```

---

## Examples

Generated example diagrams are available in [`docs/images/`](docs/images/).

### Hello World

```plantuml
@startuml Hello World
!define GCPPuml https://raw.githubusercontent.com/npiper/gcp-icons-for-plantuml/refs/heads/feature/2026-update/dist
!includeurl GCPPuml/GCPCommon.puml
!includeurl GCPPuml/cloud_code.puml
!includeurl GCPPuml/cloud_storage.puml

actor "Person" as personAlias
cloud_code(desktopAlias, "Label", "Technology", "Optional Description")
cloud_storage(storageAlias, "Label", "Technology", "Optional Description")

personAlias --> desktopAlias
desktopAlias --> storageAlias
@enduml
```

![Hello World](docs/images/Hello%20World.svg)

---

### Basic Usage

IoT message processing via an error rule, routing to Pub/Sub event and error queues.

```plantuml
@startuml Basic Usage - GCP IoT Rules Engine
!define GCPPuml https://raw.githubusercontent.com/npiper/gcp-icons-for-plantuml/refs/heads/feature/2026-update/dist
!includeurl GCPPuml/GCPCommon.puml
!includeurl GCPPuml/iot_core.puml
!includeurl GCPPuml/pubsub.puml

left to right direction
agent "Published Event" as event #fff
iot_core(iotRule, "Action Error Rule", "error if Kinesis fails")
pubsub(eventStream, "IoT Events", "2 shards")
pubsub(errorQueue, "Rule Error Queue", "failed Rule actions")

event --> iotRule : JSON message
iotRule --> eventStream : messages
iotRule --> errorQueue : Failed action message
@enduml
```

![Basic Usage](docs/images/Basic%20Usage%20-%20GCP%20IoT%20Rules%20Engine.svg)

---

### Serverless API

Cloud Endpoints fronting Cloud Run, backed by Firestore, Cloud Armor at the edge.

```plantuml
@startuml Serverless API - GCP v2
!define GCPPuml https://raw.githubusercontent.com/npiper/gcp-icons-for-plantuml/refs/heads/feature/2026-update/dist
!includeurl GCPPuml/GCPCommon.puml
!includeurl GCPPuml/cloud_armor.puml
!includeurl GCPPuml/cloud_endpoints.puml
!includeurl GCPPuml/cloud_run.puml
!includeurl GCPPuml/firestore.puml
!includeurl GCPPuml/secret_manager.puml

left to right direction
actor "Client" as client

cloud_armor(armor, "Cloud Armor", "DDoS / WAF")
cloud_endpoints(endpoints, "Cloud Endpoints", "OpenAPI Gateway")
cloud_run(service, "Orders API", "Cloud Run")
firestore(db, "Orders Store", "Firestore")
secret_manager(secrets, "API Keys", "Secret Manager")

client --> armor
armor --> endpoints
endpoints --> service
service --> db
service --> secrets : reads at startup
@enduml
```

![Serverless API](docs/images/Serverless%20API%20-%20GCP%20v2.svg)

---

### Data Pipeline

Streaming ingestion from IoT devices through to BigQuery and Looker.

```plantuml
@startuml Data Pipeline - GCP v2
!define GCPPuml https://raw.githubusercontent.com/npiper/gcp-icons-for-plantuml/refs/heads/feature/2026-update/dist
!includeurl GCPPuml/GCPCommon.puml
!includeurl GCPPuml/iot_core.puml
!includeurl GCPPuml/pubsub.puml
!includeurl GCPPuml/dataflow.puml
!includeurl GCPPuml/bigquery.puml
!includeurl GCPPuml/cloud_storage.puml
!includeurl GCPPuml/looker.puml

left to right direction
node "Edge Devices" as devices

iot_core(iot, "IoT Core", "Device Registry")
pubsub(topic, "Events Topic", "Pub/Sub")
dataflow(pipeline, "Transform & Enrich", "Dataflow (streaming)")
cloud_storage(raw, "Raw Events", "GCS (archive)")
bigquery(warehouse, "Analytics", "BigQuery")
looker(dashboard, "Operations Dashboard", "Looker")

devices --> iot : MQTT
iot --> topic : publish
topic --> pipeline : subscribe
pipeline --> raw : archive
pipeline --> warehouse : stream insert
warehouse --> dashboard : SQL
@enduml
```

![Data Pipeline](docs/images/Data%20Pipeline%20-%20GCP%20v2.svg)

---

### Raw Sprite Usage

Use sprites directly inside any PlantUML shape — no macro required.

```plantuml
@startuml Raw Sprite Usage
!define GCPPuml https://raw.githubusercontent.com/npiper/gcp-icons-for-plantuml/refs/heads/feature/2026-update/dist
!includeurl GCPPuml/GCPCommon.puml
!includeurl GCPPuml/vertexai.puml
!includeurl GCPPuml/iot_core.puml

component "<color:green><$vertexai_png></color>" as myMLModel
database "<color:#232F3E><$iot_core_png></color>" as myRoboticService
iot_core(mySecondFunction, "Reinforcement Learning", "Gazebo")
rectangle "<color:GCP_SYMBOL_COLOR><$vertexai_png></color>" as mySecondML

myMLModel --> myRoboticService
mySecondFunction --> mySecondML
@enduml
```

![Raw Sprite Usage](docs/images/Raw%20Sprite%20Usage.svg)

---

### Simplified View

The `GCPSimplified.puml` include filters technical detail for executive-level diagrams.

```plantuml
@startuml Two Modes - Simple View
!define GCPPuml https://raw.githubusercontent.com/npiper/gcp-icons-for-plantuml/refs/heads/feature/2026-update/dist
!includeurl GCPPuml/GCPCommon.puml
!includeurl GCPPuml/GCPSimplified.puml
!includeurl GCPPuml/cloud_endpoints.puml
!includeurl GCPPuml/app_engine.puml
!include <material/common>
!include <material/cellphone_android>

left to right direction
GCPEntityColoring(MA_CELLPHONE_ANDROID)
MA_CELLPHONE_ANDROID(#9E9E9E, 1, sources, rectangle, "Android")
cloud_endpoints(endpoints, "GCP Cloud Endpoints", "api")
app_engine(engine, "GCP App Engine", "API Backend Instances")

sources <--> endpoints
endpoints <--> engine
@enduml
```

![Simple View](docs/images/Two%20Modes%20-%20Simple%20View.svg)

---

### Technical View

The same diagram without `GCPSimplified.puml` — full technical detail.

![Technical View](docs/images/Two%20Modes%20-%20Technical%20View.svg)

---

## Sprite Modes: PNG and SVG

Each `.puml` file in `dist/` contains **both** a PNG sprite and an SVG sprite for every icon.

| Mode | How to activate | When to use |
|---|---|---|
| **PNG** (grayscale, 72×72) | Default — no define needed | Remote `!includeurl`, any PlantUML version |
| **SVG** (full colour, scalable) | `!pragma svgparser sax` + `!define GCP_USE_SVG` before any include | Local `!include` with PlantUML >= 1.2026.x |

When using PNG mode (default), sprite names are suffixed `_png` (e.g. `$cloud_run_png`).
When using SVG mode (`!define GCP_USE_SVG`), sprite names have no suffix (e.g. `$cloud_run`).

See [`examples/Sprite Mode - PNG.puml`](examples/Sprite%20Mode%20-%20PNG.puml) and [`examples/Sprite Mode - SVG.puml`](examples/Sprite%20Mode%20-%20SVG.puml) for working examples of both modes.

**PNG mode** (remote `!includeurl`, grayscale):

![Sprite Mode PNG](docs/images/Sprite%20Mode%20-%20PNG%20fallback%20(v2%20local).svg)

**SVG mode** (local `!include`, full colour):

![Sprite Mode SVG](docs/images/Sprite%20Mode%20-%20SVG%20(v2).svg)

---

## Customised Builds

To regenerate the `dist/` directory from your local `source/official/` icons:

```bash
cd scripts
pip3 install -r requirements.txt
JAVA_HOME=/path/to/jdk18 python3 icon-builderv2.py
```

The build requires Java 18+ (for the bundled `plantuml.jar`). It reads `configv2.yml` and writes one `.puml` file per product into `dist/` — no category subdirectories.

To create a config template from whatever is currently in `source/official/`:

```bash
python3 icon-builderv2.py --create-config-template
```

This produces `config-template.yml` as a starting point for new GCP icon set releases.

---

## Contributing

When Google releases a new icon set:

1. Download and unzip to `source/official/`, replacing existing contents.
2. Run `python3 icon-builderv2.py --create-config-template` to see what is new or removed.
3. For **new directories**: add a matching entry to `configv2.yml` (copy any existing entry as a template).
4. For **renamed directories**: update the `SourceDir` in `configv2.yml`, keep or update the `Target`.
5. Run `python3 icon-builderv2.py` to regenerate `dist/`.
6. Open a PR against this fork.

---

## License Summary

The icons provided in this package are made available under the terms of the CC-BY-ND 2.0 license, available in the `LICENSE` file. Code is made available under the MIT license in `LICENSE-CODE`.

---

## Acknowledgements

- [davidholsgrove/gcp-icons-for-plantuml](https://github.com/davidholsgrove/gcp-icons-for-plantuml) — original v1 library (2020), the direct upstream of this fork.
- [aws-icons-for-plantuml](https://github.com/awslabs/aws-icons-for-plantuml) — the original structural pattern this library was based upon.
- [plantuml-stdlib](https://github.com/plantuml/plantuml-stdlib) — the flat sprite library pattern that informed the v2 design.

---

## v1 Reference Archive

The original v1 files are preserved in [`archive/v1/`](archive/v1/) for reference when upgrading existing diagrams:

| File | Description |
|---|---|
| [`archive/v1/README.md`](archive/v1/README.md) | Original v1 README with v1 include syntax and examples |
| [`archive/v1/config.yml`](archive/v1/config.yml) | v1 category mapping configuration used by the original `icon-builder.py` |
| [`archive/v1/scripts-README.md`](archive/v1/scripts-README.md) | v1 build instructions (category-based folder layout) |

The original builder (`scripts/icon-builder.py`) remains in place for reference but is superseded by `scripts/icon-builderv2.py`.
