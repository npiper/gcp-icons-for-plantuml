<!--
Copyright (c) 2026 Neil Piper (fork maintainer)
Original copyright (c) 2020 David Holsgrove
SPDX-License-Identifier: MIT (For details, see LICENSE-CODE)
-->

# GCP Icons for PlantUML — v2

PlantUML sprites, macros, and includes for Google Cloud Platform (GCP) services. Used to create PlantUML diagrams with GCP components. All elements are generated from the official [GCP Architecture Icons](https://cloud.google.com/icons).

> **This is a maintained fork of [davidholsgrove/gcp-icons-for-plantuml](https://github.com/davidholsgrove/gcp-icons-for-plantuml),
> updated for the current (2025/2026) GCP icon set and restructured as a breaking v2 release.**

---

## Table of Contents

- [Why v2 is a Breaking Change](#why-v2-is-a-breaking-change)
- [What Changed](#what-changed)
- [Migration from v1](#migration-from-v1)
- [Getting Started](#getting-started)
- [Examples](#examples)
  - [Hello World](#hello-world)
  - [Serverless API](#serverless-api)
  - [Data Pipeline](#data-pipeline)
  - [Security Perimeter](#security-perimeter)
  - [Raw Sprite Usage](#raw-sprite-usage)
- [Assets Needing Refresh](#assets-needing-refresh)
- [Customised Builds](#customised-builds)
- [Contributing](#contributing)
- [License Summary](#license-summary)

---

## Why v2 is a Breaking Change

### The original structure

The v1 library, published in 2020, mapped every GCP icon into one of 13 hand-curated categories:

```
dist/
  AIAndMachineLearning/
  APIManagement/
  Compute/
  DataAnalytics/
  Databases/
  DeveloperTools/
  HybridAndMultiCloud/
  InternetOfThings/
  ManagementTools/
  Migration/
  Networking/
  Security/
  Storage/
```

The include syntax reflected this:

```plantuml
!include <gcp/Compute/CloudRun>
!include <gcp/DataAnalytics/BigQuery>
!include <gcp/AIAndMachineLearning/VertexAI>
```

This was reasonable at the time. The official GCP icon set itself was organised into similar broad categories, and the mapping was stable enough to maintain.

### What Google did

Over the years since 2020, Google significantly reorganised their icon releases. Rather than broad service categories, the current icon set ships as **one directory per product**, named after the product itself, with no grouping layer:

```
source/official/
  vertexai/
  bigquery/
  cloud_run/
  cloud_sql/
  artifact_registry/
  ... (183 products)
```

There are now approximately **183 product directories**, compared to the 13 category folders in v1. Many products that existed in 2020 have been renamed, split, or removed. New products — `vertexai`, `dataplex`, `eventarc`, `cloud_deploy`, `workload_identity_pool` — have no natural home in the v1 taxonomy at all.

### The maintenance problem

Keeping a curated category mapping alive requires a human decision every time Google releases a new icon set:

- Where does `dataplex` go? Data Analytics? Databases? Management?
- Is `eventarc` a Developer Tool or a Networking service?
- `vertexai` supersedes `ai_platform_unified` — do both get entries? In which categories?

Every new GCP release risked the category layer becoming wrong, opinionated, or incomplete. Anyone who had built diagrams using `<gcp/Compute/CloudRun>` would find their include paths broken if icons moved between categories, even if the icons themselves were identical.

### The v2 decision

v2 removes the category layer entirely. The library now mirrors Google's own structure: **one file per product, named after the product directory**. This means:

- **Zero ongoing mapping work.** When Google adds a new icon directory, a new entry appears automatically. When they rename one, a single line in `configv2.yml` changes.
- **Predictable names.** The include name is always the product directory name, which is what you would look up on cloud.google.com.
- **No taxonomy disagreements.** We do not decide whether BigQuery is "Data Analytics" or "Databases".
- **Parity with other flat sprite libraries.** The [gilbarbara sprites stdlib](https://github.com/plantuml-stdlib/gilbarbara-plantuml-sprites) uses the same flat approach and it works well at scale.

This approach was also used as the basis for proposing this library's inclusion in the official [plantuml-stdlib](https://github.com/plantuml/plantuml-stdlib), where the flat structure fits naturally alongside `awslib` and `azure`.

---

## What Changed

| | v1 (2020) | v2 (2026) |
|---|---|---|
| Output structure | `dist/{Category}/{ProductName}.puml` | `dist/{product_name}.puml` |
| Include syntax | `!include <gcp/Compute/CloudRun>` | `!include <gcp/cloud_run>` |
| Naming convention | CamelCase (`CloudRun`, `BigQuery`) | snake_case (`cloud_run`, `bigquery`) |
| Categories | 13 hand-curated groups | None — flat list of products |
| `all.puml` per category | Yes | No (all icons at root level) |
| Number of icons | ~80 products | ~183 products |
| Icon source | GCP Architecture Icons 2020 | GCP Architecture Icons 2025/2026 |
| Config file | `scripts/config.yml` | `scripts/configv2.yml` |
| Builder | `icon-builder.py` (original) | `icon-builder.py` (v2 flat mode) |

---

## Migration from v1

Replace each include path, mapping from the old category + CamelCase name to the new snake_case product name.

Common examples:

| v1 | v2 |
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

Macro names also change from CamelCase to snake_case, matching the include name:

| v1 macro | v2 macro |
|---|---|
| `CloudRun(alias, label, tech)` | `cloud_run(alias, label, tech)` |
| `BigQuery(alias, label, tech)` | `bigquery(alias, label, tech)` |
| `CloudStorage(alias, label, tech)` | `cloud_storage(alias, label, tech)` |

---

## Getting Started

Include `GCPCommon.puml` first, then any product files you need.

### Using this repository directly (URL)

```plantuml
!define GCPPuml https://raw.githubusercontent.com/npiper/gcp-icons-for-plantuml/master/dist
!include GCPPuml/GCPCommon.puml
!include GCPPuml/cloud_run.puml
!include GCPPuml/cloud_sql.puml
!include GCPPuml/cloud_storage.puml
```

### Using local files

```plantuml
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

### Hello World

The simplest possible diagram: a user calling a Cloud Run service that reads from Cloud Storage.

```plantuml
@startuml Hello World - GCP v2

!define GCPPuml https://raw.githubusercontent.com/npiper/gcp-icons-for-plantuml/master/dist
!include GCPPuml/GCPCommon.puml
!include GCPPuml/cloud_run.puml
!include GCPPuml/cloud_storage.puml

actor "User" as user

cloud_run(api, "API Service", "Cloud Run")
cloud_storage(bucket, "Assets", "Cloud Storage")

user --> api : HTTPS
api --> bucket : read/write

@enduml
```

---

### Serverless API

A modern serverless API pattern: Cloud Endpoints fronting Cloud Run, backed by Firestore, with Cloud Armor protecting the edge and Secret Manager holding credentials.

```plantuml
@startuml Serverless API - GCP v2

!define GCPPuml https://raw.githubusercontent.com/npiper/gcp-icons-for-plantuml/master/dist
!include GCPPuml/GCPCommon.puml
!include GCPPuml/cloud_armor.puml
!include GCPPuml/cloud_endpoints.puml
!include GCPPuml/cloud_run.puml
!include GCPPuml/firestore.puml
!include GCPPuml/secret_manager.puml
!include GCPPuml/identity_and_access_management.puml

left to right direction

actor "Client" as client

cloud_armor(armor, "Cloud Armor", "DDoS / WAF")
cloud_endpoints(endpoints, "Cloud Endpoints", "OpenAPI Gateway")
cloud_run(service, "Orders API", "Cloud Run (us-central1)")
firestore(db, "Orders Store", "Firestore")
secret_manager(secrets, "API Keys", "Secret Manager")
identity_and_access_management(iam, "Service Account", "IAM")

client --> armor
armor --> endpoints
endpoints --> service
service --> db
service --> secrets : reads at startup
service --> iam : bound SA

@enduml
```

---

### Data Pipeline

A streaming data ingestion and analytics pipeline from IoT devices through to BigQuery.

```plantuml
@startuml Data Pipeline - GCP v2

!define GCPPuml https://raw.githubusercontent.com/npiper/gcp-icons-for-plantuml/master/dist
!include GCPPuml/GCPCommon.puml
!include GCPPuml/iot_core.puml
!include GCPPuml/pubsub.puml
!include GCPPuml/dataflow.puml
!include GCPPuml/bigquery.puml
!include GCPPuml/cloud_storage.puml
!include GCPPuml/looker.puml

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

---

### Security Perimeter

Illustrating a defence-in-depth architecture using GCP security services.

```plantuml
@startuml Security Perimeter - GCP v2

!define GCPPuml https://raw.githubusercontent.com/npiper/gcp-icons-for-plantuml/master/dist
!include GCPPuml/GCPCommon.puml
!include GCPPuml/cloud_armor.puml
!include GCPPuml/identity_and_access_management.puml
!include GCPPuml/binary_authorization.puml
!include GCPPuml/security_command_center.puml
!include GCPPuml/cloud_audit_logs.puml
!include GCPPuml/key_management_service.puml
!include GCPPuml/access_context_manager.puml
!include GCPPuml/google_kubernetes_engine.puml

rectangle "Security Controls" {
  cloud_armor(armor, "Cloud Armor", "Edge Protection")
  identity_and_access_management(iam, "IAM", "Identity & Access")
  binary_authorization(binauthz, "Binary Authorization", "Supply Chain")
  access_context_manager(acm, "Access Context Manager", "VPC-SC")
  key_management_service(kms, "Cloud KMS", "Encryption Keys")
}

google_kubernetes_engine(gke, "Workload Cluster", "GKE Autopilot")
security_command_center(scc, "Security Command Center", "Threat Detection")
cloud_audit_logs(logs, "Audit Logs", "All admin activity")

armor --> gke
iam --> gke
binauthz --> gke : admit only signed images
acm --> gke : VPC-SC boundary
kms --> gke : CMEK
gke --> scc : findings
gke --> logs : admin/data events

@enduml
```

---

### Raw Sprite Usage

Use the sprite directly inside any PlantUML shape — no macro required.

```plantuml
@startuml Raw Sprites - GCP v2

!define GCPPuml https://raw.githubusercontent.com/npiper/gcp-icons-for-plantuml/master/dist
!include GCPPuml/GCPCommon.puml
!include GCPPuml/vertexai.puml
!include GCPPuml/cloud_storage.puml

component "<color:GoogleBlue><$vertexai></color>\nVertex AI Model" as model
database "<color:GoogleBlue><$cloud_storage></color>\nTraining Data" as store

model --> store : reads features

@enduml
```

---

## Assets Needing Refresh

The following files in this repository were written against v1 (2020 icon set and category structure) and need to be updated for v2:

### Examples (all need rewriting for v2 include paths and macro names)

| File | v1 dependency | v2 action |
|---|---|---|
| `examples/HelloWorld.puml` | `!includeurl`, category paths, `CloudToolsforVisualStudio`, `CloudStorage` | Rewrite using v2 includes and macros |
| `examples/Basic Usage.puml` | `InternetOfThings/CloudIoTCore`, `DataAnalytics/CloudPubSub` | Rewrite using `iot_core`, `pubsub` |
| `examples/Raw Sprite Usage.puml` | `AIAndMachineLearning/AIPlatform`, `InternetOfThings/CloudIoTCore` | Rewrite using `ai_platform`, `iot_core` |
| `examples/Two Modes - Simple View.puml` | `APIManagement/CloudEndpoints`, `Compute/AppEngine` | Rewrite using `cloud_endpoints`, `app_engine`; reassess `GCPSimplified.puml` |
| `examples/Two Modes - Technical View.puml` | Same as Simple View | Same as above |

### Root documentation

| File | Issue |
|---|---|
| `README.md` | All include paths, macro names, and category references are v1. Replace with this file (`README-v2.md`) once generation is verified. |
| `GCPSymbols.md` | Auto-generated from build; will be regenerated by `icon-builder.py` v2 run. Contains v1 category table. |

### Source / scripts

| File | Issue |
|---|---|
| `scripts/config.yml` | v1 category config — kept for reference but no longer the active config. |
| `scripts/README.md` | Build instructions reference old category folder layout and old config.yml. Update once v2 builder is confirmed working. |
| `scripts/icon-builder.py` | Needs flat-output change (one-line path change + remove category `mkdir` loop). |
| `source/GCPCommon.puml` | Macro definitions use CamelCase names aligned to v1. Review whether macro names need updating for v2 snake_case targets. |

### GitHub / metadata

| File | Issue |
|---|---|
| `.github/` workflows (if any) | May reference v1 build steps or config.yml. |
| `CITATION.cff` (if present) | Version and date. |

---

## Customised Builds

To regenerate the `dist/` directory from your local `source/official/` icons:

```bash
cd scripts
pip3 install -r requirements.txt
./icon-builder.py --check-env     # verify prerequisites
./icon-builder.py                 # generate dist/
```

The build uses `configv2.yml` and writes one `.puml` file per product directly into `dist/` — no category subdirectories.

To generate a template from whatever is currently in `source/official/`:

```bash
./icon-builder.py --create-config-template
```

This produces `config-template.yml` which can be used as a starting point for future releases.

---

## Contributing

If Google releases a new icon set:

1. Download and unzip to `source/official/`, replacing existing contents.
2. Run `./icon-builder.py --create-config-template` to see what is new or removed.
3. For **new directories**: add a matching entry to `configv2.yml` (copy any existing entry as a template — one line changes).
4. For **renamed directories**: update the `SourceDir` in `configv2.yml` and keep or update the `Target`.
5. Run `./icon-builder.py` to regenerate `dist/`.
6. Open a PR against this fork. If targeting upstream `davidholsgrove/gcp-icons-for-plantuml` or the plantuml-stdlib, note this is a v2 breaking change.

---

## License Summary

Code is made available under the MIT license. See `LICENSE-CODE`.

GCP icons are owned by Google LLC and subject to Google's [Brand Resource Center terms](https://about.google/brand-resource-center/). They are redistributed here under the terms of the [GCP Architecture Icons license](https://cloud.google.com/icons).

---

## Acknowledgements

- [David Holsgrove](https://github.com/davidholsgrove) — original author of `gcp-icons-for-plantuml` (v1, 2020).
- [AWS Icons for PlantUML](https://github.com/awslabs/aws-icons-for-plantuml) — the structural inspiration for v1.
- [gilbarbara sprites](https://github.com/plantuml-stdlib/gilbarbara-plantuml-sprites) — inspiration for the flat v2 approach.
- [PlantUML stdlib](https://github.com/plantuml/plantuml-stdlib) — target for inclusion.
