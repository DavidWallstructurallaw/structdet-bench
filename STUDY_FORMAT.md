# StructDet-Bench Study Format

**Operational schema version:** `0.1`  
**Operational grammar:** Phase 4 Step 2, P4-W04 through P4-W07; additive offline CLI and disclosures available at Step 8, P4-W31 through P4-W34  
**Authority:** the adopted `PHASE_4_PLAN.md`, especially §§3, 5, 6 and 9, and the unchanged inherited scientific and physical contracts.

This format describes a passive study workspace. Successful parsing establishes field shape, declared identity consistency and bounded acquisition. It establishes no actual execution, independent human review, prospective registration, evidence qualification, operational readiness, or empirical finding. Every supplied status remains a recorded assertion until the corresponding later qualification procedure evaluates its actual evidence. Both public result objects expose `substantive_validation_performed: false`.

The software fixtures contain stipulated examples of all twelve record families. “Complete” in their filename means a complete structural example. Their material role is `fixture`, their evidence policy is `fixture_only`, and their unresolved scientific prerequisites remain unresolved. Fixture provenance must survive every later export.

## 1. Component API and outcomes

The record module is `structdet_bench.study_records`. Step 8 adds the opt-in `study inspect`, `study export-review` and `study prepare` commands through `structdet_bench.study_cli`, with readiness/disclosure companions in `structdet_bench.study_reporting`. The original `validate` and `analyze` commands remain available for compatible M/V/L bundles. See `README.md` and `EMPIRICAL_PROTOCOL.md` for complete CLI examples, explicit selection flags, fresh-directory publication and evidence limits.

| Function | Result and failure behavior |
|---|---|
| `parse_study_bytes(data, limits=None)` | A `StudyPacket` for strict UTF-8 JSON. Malformed bytes produce diagnostics, without an exception-based fallback reader. |
| `parse_study(mapping, limits=None)` | The same grammar for direct Python values. Binary floats, recursive containers and unsupported values fail. Tuples and frozen mappings are accepted as JSON arrays/objects. |
| `load_study(path, limits=None)` | A `LoadedStudy` with the parsed packet, immutable actual byte snapshots, one attachment observation per inventoried item, and diagnostics. Reads no undeclared attachment. |
| `canonical_study_bytes(packet_or_mapping)` | Validates the packet and returns deterministic UTF-8 JSON. Invalid input raises `InputError("invalid_study_for_serialization")`. |

`StudyPacket` has `data`, `records`, `diagnostics`, `has_errors`, `exit_code`, and `substantive_validation_performed`. `StudyRecord` exposes `record_type`, `record_id`, `record_version`, `study_version`, and immutable `data`. `LoadedStudy` has `packet`, `snapshots`, `attachments`, `diagnostics`, `total_read_bytes`, `acquisition_complete`, `has_errors`, `exit_code`, and `substantive_validation_performed`. Missing acquisition does not erase the well-formed supplied record.

The component exit convention is **0 for structurally well-formed input, including unresolved or restricted studies; 2 for malformed or contradictory input**. A later compiler reports an unrepresentable requested conversion as a mapping error and withholds the bundle. Readiness-only inspection remains possible on a well-formed input with known missing evidence. A status flag cannot override a malformed record.

## 2. Physical grammar and canonical bytes

The envelope is one JSON object. Input uses strict UTF-8 without a BOM, comments, duplicate keys, trailing documents, nonfinite numbers, or unpaired Unicode surrogates. Escaped and literal spellings of the same key count as duplicate keys. Unknown keys fail at every structured level. All fields listed below are required, including explicit empty arrays or tagged uncertainty. No extensions, arbitrary payload object, implicit defaults, executable expression, imported module or automatic schema expansion exists.

The inherited hard ceilings are **16 MiB per file, 64 MiB per import, 1 MiB per JSON/JSONL physical line, 100,000 records per import, nesting depth 64, and numeric-token length 1,024**. JSONL counts each nonblank object line as one record and rejects blank or nonobject lines. A `json` attachment counts as one record; a `bytes` attachment counts as zero and has no text-line requirement. Raw bytes retain arbitrary exact content, including invalid UTF-8. They remain passive.

`ReadLimits` may only lower those ceilings. An expanded limit fails with `unsupported_read_limit`; no permissive reader is substituted. Direct-value parsing additionally checks the canonical physical representation. Byte parsing checks both the original representation and its canonical representation, so every accepted envelope can be serialized and reparsed within the default hard ceilings. Numeric lexemes are retained as `ExactNumber`; a decimal JSON token is never coerced to a binary float. Decimal-string control values remain strings. Exact numeric control values have a finite exponent with absolute value at most 10,000 and at most 1,024 characters. This bound concerns operational numeric fields and does not change an inherited metric.

Canonical bytes use lexicographically sorted object keys, two-space indentation, unchanged array order, UTF-8 without ASCII-only escaping, and one trailing LF. No Unicode normalization, stripping of original text, reordering of coverage IDs or semantic number rounding occurs. Fractional/exponent JSON numbers retain their original token. `known false`, `known 0`, known null where explicitly permitted, unknown, unavailable, and not applicable remain distinct. Canonicalization is not a scientific comparison or evidence qualification operation.

## 3. Type notation

The formal grammar in §§4–6 uses the following small schema notation. It is descriptive data, not a user-supplied validator language.

| Notation | Exact meaning |
|---|---|
| `text` | A nonempty string containing a non-whitespace character. |
| `id` | Existing bounded identifier `[A-Za-z0-9][A-Za-z0-9_.:-]{0,255}`. |
| `hash` | Exactly 64 lowercase hexadecimal SHA-256 characters. |
| `positive`, `nonnegative` | Plain Python/JSON integer greater than zero or at least zero; booleans fail. |
| `bool` | A JSON Boolean. |
| `integer_or_null` | A plain integer or explicit JSON null. This permits an explicitly known no-fixed-seed value. |
| `exact`, `exact_nonnegative`, `probability` | Exact JSON integer/decimal token or decimal string; respectively finite signed, nonnegative, or greater than zero and at most one. Binary floats fail direct parsing. |
| `timestamp` | ISO timestamp with a `T` separator and explicit UTC offset or `Z`. Its existence alone does not establish event chronology. |
| `path` | A safe relative local path under §7. |
| `class_id` | One of the original eight `SORT-*` family IDs. |
| `core_role` | `CORE-<family>-A`, `-B`, `-D` for the eight families, or `CORE-X01` through `CORE-X08`. |
| `{"literal": value}` | The exact listed value. |
| `{"enum": [...]}` | Exactly one listed string. |
| `{"array": T}` | An ordered array of T; empty unless a stated semantic invariant requires entries. |
| `{"object": {...}}` | Exactly these named fields, all required, with the shown types. |
| `{"knowledge": T}` | `{"state":"known","value":T}` or `{"state":"unknown"/"unavailable"/"not_applicable","reason":text}`. Every nonknown state requires a reason. No `value`, including null, is allowed in a nonknown wrapper. |
| `{"reference": [...]}` | Exactly `record_type`, `record_id`, `record_version`, with type in the listed families and version `0.1`. The target must resolve uniquely. |
| `{"choice": [...]}` | One exact alternative object, selected by its literal `kind`. |
| `record` | One common record envelope plus exactly the fields for its `record_type`. |

Knowledge wrappers are deliberately separate from reference arrays. Their reasons record the absence or inapplicability basis without pretending to provide evidence. Field-specific semantics still apply: a mandatory prerequisite cannot be relabeled not applicable, and accepted assignment shape requires a known class identifier. Parsing a declared assignment does not admit it into an analysis population.

## 4. Envelope grammar

The finite `packet_inventory` is declared before attachment reading. `import_budget` caps total packets, total bytes and total records. Byte accounting includes the original envelope bytes and each acquired snapshot. Known declared sizes and counts are checked before acquisition, and actual acquired sizes/counts are checked independently. The same packet cannot appear under duplicate IDs or duplicate local paths. A packet cannot refer to the envelope file itself.

The current study version and `prior_study_versions` are disjoint and unique. Exactly one registration is required for each declared version. Every record belongs to the one envelope study ID and a declared version. Historical records preserve their original bytes and identities; they are not silently rewritten to the current version.

```json
{
  "object": {
    "study_schema_version": {
      "literal": "0.1"
    },
    "study_id": "id",
    "study_version": "id",
    "prior_study_versions": {
      "array": "id"
    },
    "evidence_policy": {
      "enum": [
        "fixture_only",
        "adjudicated_import"
      ]
    },
    "material_role": {
      "enum": [
        "fixture",
        "pilot",
        "confirmatory",
        "descriptive"
      ]
    },
    "packet_inventory": {
      "array": {
        "object": {
          "packet_id": "id",
          "purpose": {
            "enum": [
              "artifact",
              "evidence",
              "review",
              "original_response",
              "compiled_output",
              "registration"
            ]
          },
          "location": {
            "knowledge": {
              "choice": [
                {
                  "object": {
                    "kind": {
                      "literal": "local"
                    },
                    "path": "path"
                  }
                },
                {
                  "object": {
                    "kind": {
                      "literal": "external"
                    },
                    "locator": "text"
                  }
                }
              ]
            }
          },
          "sha256": {
            "knowledge": "hash"
          },
          "size_bytes": {
            "knowledge": "nonnegative"
          },
          "record_count": {
            "knowledge": "nonnegative"
          },
          "format": {
            "enum": [
              "bytes",
              "json",
              "jsonl"
            ]
          },
          "verification": {
            "enum": [
              "unchecked",
              "locally_verified_content",
              "verified_external_receipt",
              "unavailable_attachment"
            ]
          },
          "verification_ref": {
            "knowledge": {
              "reference": [
                "study_registration",
                "activity_readiness",
                "core_catalog",
                "artifact",
                "validation_receipt",
                "human_review",
                "adjudication",
                "collection_ledger",
                "extraction",
                "audit_selection",
                "correction_incident",
                "compilation_receipt"
              ]
            }
          }
        }
      }
    },
    "import_budget": {
      "object": {
        "max_packets": "nonnegative",
        "max_total_bytes": "positive",
        "max_total_records": "positive"
      }
    },
    "records": {
      "array": "record"
    }
  }
}
```

## 5. Common record fields and graph relations

Record IDs are globally unique within an envelope, even across families or study versions. `record_version` names the physical grammar, while `study_version` names the study instance and `revision` is an explicit positive record revision number. A revised record receives a new ID. `scope` fixes a claim ID and task/version; every record for a version agrees with that version's registration and pinned task.

An ordinary typed reference resolves to the same study version and scope. `depends_on` is an explicit acyclic dependency graph. `supersedes` has one typed predecessor or a reasoned nonknown state, requires the same record family and a strictly lower predecessor revision, and is acyclic. It may cross a declared historical version. No semantic version ordering is guessed from arbitrary version strings.

`lineage_refs` may cross declared historical versions and may contain reciprocal/cyclic source associations. These relationships are not merged into the dependency graph. A correction's `affected_refs` can also identify historical records. The claim/task scope remains equal across these edges. Other correction references, review evidence and compilation mappings obey the ordinary same-version rule; old inputs are carried explicitly in `input_snapshots` or historical records rather than borrowed as new evidence.

Typed artifact references additionally enforce their role where the relation requires one: prompt links name `prompt` artifacts; original response links name `raw_response`; extracted selections name `candidate` or generic `source`; core links name core material or generic `source`; a supplied legacy profile names `source` or `longitudinal_input`. A generic source role makes no claim that the bytes are validated code.

```json
{
  "object": {
    "record_type": {
      "enum": [
        "study_registration",
        "activity_readiness",
        "core_catalog",
        "artifact",
        "validation_receipt",
        "human_review",
        "adjudication",
        "collection_ledger",
        "extraction",
        "audit_selection",
        "correction_incident",
        "compilation_receipt"
      ]
    },
    "record_version": {
      "literal": "0.1"
    },
    "record_id": "id",
    "study_id": "id",
    "study_version": "id",
    "revision": "positive",
    "scope": {
      "object": {
        "claim_id": "id",
        "task_id": "id",
        "task_version": "id"
      }
    },
    "depends_on": {
      "array": {
        "reference": [
          "study_registration",
          "activity_readiness",
          "core_catalog",
          "artifact",
          "validation_receipt",
          "human_review",
          "adjudication",
          "collection_ledger",
          "extraction",
          "audit_selection",
          "correction_incident",
          "compilation_receipt"
        ]
      }
    },
    "lineage_refs": {
      "array": {
        "reference": [
          "study_registration",
          "activity_readiness",
          "core_catalog",
          "artifact",
          "validation_receipt",
          "human_review",
          "adjudication",
          "collection_ledger",
          "extraction",
          "audit_selection",
          "correction_incident",
          "compilation_receipt"
        ]
      }
    },
    "supersedes": {
      "knowledge": {
        "reference": [
          "study_registration",
          "activity_readiness",
          "core_catalog",
          "artifact",
          "validation_receipt",
          "human_review",
          "adjudication",
          "collection_ledger",
          "extraction",
          "audit_selection",
          "correction_incident",
          "compilation_receipt"
        ]
      }
    }
  }
}
```

## 6. Complete family-specific field grammar

Each block below is added to the common fields. Every nested key is explicit. There are no future catch-all fields.

### 6.1. `study_registration`

```json
{
  "object": {
    "claim_scope": "text",
    "source_pins": {
      "object": {
        "SD": {
          "literal": "357c0c3994e34fc1831ce91bf1c7e579925d64827579f80eb0a8708e85c93f32"
        },
        "SI": {
          "literal": "80c193231af343d383544cee924a11fbb063a5c4ccee02d996ea4f904979565a"
        },
        "EC": {
          "literal": "002d2393d05cb2c8b1db0a70e844e3d775e2be2155db7b2ffaadaa8080c8b950"
        }
      }
    },
    "pins": {
      "object": {
        "task_id": {
          "literal": "bounded_integer_sort"
        },
        "task_version": {
          "literal": "0.1"
        },
        "analytic_resolution_id": {
          "literal": "sorting_mechanism_family"
        },
        "analytic_resolution_version": {
          "literal": "0.1"
        },
        "structural_schema_id": {
          "literal": "sorting_mechanism_partition"
        },
        "structural_schema_version": {
          "literal": "0.1"
        },
        "reference_registry_id": {
          "literal": "sorting_reference_eight"
        },
        "reference_registry_version": {
          "literal": "0.1"
        },
        "validity_rubric_ref": {
          "literal": "bounded_integer_sort_validity_v1"
        }
      }
    },
    "requested_profile": {
      "enum": [
        "m_only",
        "hero_sort_abc_v1",
        "structdet_longitudinal_v1"
      ]
    },
    "frame_definition": {
      "object": {
        "task_context": {
          "knowledge": "text"
        },
        "consequence_horizon": {
          "knowledge": "text"
        },
        "load_bearing_invariants": {
          "array": "text"
        },
        "consequence_signature_spec": {
          "knowledge": "text"
        },
        "equivalence_rule_ref": {
          "knowledge": "text"
        },
        "admissible_substitutions": {
          "knowledge": "text"
        },
        "evidence_requirement": {
          "knowledge": "text"
        },
        "exceptional_case_rules": {
          "knowledge": "text"
        }
      }
    },
    "protocol": {
      "object": {
        "protocol_id": "id",
        "protocol_version": "id",
        "design": {
          "enum": [
            "sorting_abc",
            "supplied_longitudinal",
            "descriptive"
          ]
        },
        "prompt_refs": {
          "array": {
            "reference": [
              "artifact"
            ]
          }
        },
        "controls": {
          "object": {
            "temperature": {
              "knowledge": "exact_nonnegative"
            },
            "top_p": {
              "knowledge": "probability"
            },
            "presence_penalty": {
              "knowledge": "exact"
            },
            "frequency_penalty": {
              "knowledge": "exact"
            },
            "seed": {
              "knowledge": "integer_or_null"
            },
            "output_allowance": {
              "knowledge": "nonnegative"
            },
            "cap_semantics": {
              "knowledge": "text"
            },
            "fresh_context": {
              "knowledge": "bool"
            },
            "tools_requested": {
              "knowledge": "bool"
            },
            "hidden_controls": {
              "knowledge": "text"
            },
            "wrapper_knowledge": {
              "knowledge": "text"
            }
          }
        },
        "budget": {
          "object": {
            "max_calls": {
              "knowledge": "nonnegative"
            },
            "max_positions": {
              "knowledge": "nonnegative"
            },
            "max_output_tokens": {
              "knowledge": "nonnegative"
            },
            "monetary_ceiling": {
              "knowledge": "exact_nonnegative"
            },
            "currency": {
              "knowledge": "text"
            }
          }
        },
        "longitudinal_input": {
          "knowledge": {
            "reference": [
              "artifact"
            ]
          }
        },
        "legacy_profile_input": {
          "knowledge": {
            "object": {
              "artifact_ref": {
                "reference": [
                  "artifact"
                ]
              },
              "input_schema_version": {
                "literal": "0.1"
              },
              "profile": {
                "enum": [
                  "m_only",
                  "hero_sort_abc_v1",
                  "structdet_longitudinal_v1"
                ]
              }
            }
          }
        }
      }
    },
    "preregistration": {
      "object": {
        "status": {
          "enum": [
            "prospectively_registered",
            "retrospective",
            "not_registered",
            "unknown"
          ]
        },
        "registered_at": {
          "knowledge": "timestamp"
        },
        "evidence_refs": {
          "array": {
            "reference": [
              "study_registration",
              "activity_readiness",
              "core_catalog",
              "artifact",
              "validation_receipt",
              "human_review",
              "adjudication",
              "collection_ledger",
              "extraction",
              "audit_selection",
              "correction_incident",
              "compilation_receipt"
            ]
          }
        },
        "exposure_at_registration": {
          "knowledge": "text"
        }
      }
    },
    "exposure": {
      "knowledge": "text"
    },
    "currentness": {
      "object": {
        "state": {
          "enum": [
            "current",
            "expired",
            "unresolved"
          ]
        },
        "assessed_at": {
          "knowledge": "timestamp"
        },
        "expires_at": {
          "knowledge": "timestamp"
        },
        "basis": {
          "knowledge": "text"
        }
      }
    }
  }
}
```

### 6.2. `activity_readiness`

```json
{
  "object": {
    "activity": {
      "enum": [
        "core_construction",
        "external_validation",
        "human_review",
        "pilot_collection",
        "main_collection",
        "analysis",
        "scientific_release"
      ]
    },
    "state": {
      "enum": [
        "ready",
        "restricted",
        "blocked",
        "not_assessed"
      ]
    },
    "prerequisites": {
      "array": {
        "object": {
          "requirement_id": "id",
          "mandatory": "bool",
          "outcome": {
            "enum": [
              "satisfied_for_scope",
              "unsatisfied",
              "unresolved",
              "not_applicable"
            ]
          },
          "evidence_refs": {
            "array": {
              "reference": [
                "study_registration",
                "activity_readiness",
                "core_catalog",
                "artifact",
                "validation_receipt",
                "human_review",
                "adjudication",
                "collection_ledger",
                "extraction",
                "audit_selection",
                "correction_incident",
                "compilation_receipt"
              ]
            }
          },
          "basis": {
            "knowledge": "text"
          }
        }
      }
    },
    "outstanding_requirements": {
      "array": "id"
    },
    "responsible_operator": {
      "knowledge": "id"
    },
    "authorization_ref": {
      "knowledge": {
        "reference": [
          "study_registration",
          "activity_readiness",
          "core_catalog",
          "artifact",
          "validation_receipt",
          "human_review",
          "adjudication",
          "collection_ledger",
          "extraction",
          "audit_selection",
          "correction_incident",
          "compilation_receipt"
        ]
      }
    }
  }
}
```

### 6.3. `core_catalog`

```json
{
  "object": {
    "role_id": "core_role",
    "proposed_family": {
      "knowledge": "class_id"
    },
    "desired_contrast": "text",
    "artifact_ref": {
      "knowledge": {
        "reference": [
          "artifact"
        ]
      }
    },
    "source": {
      "knowledge": "text"
    },
    "ai_assistance": {
      "knowledge": "text"
    },
    "exposure": {
      "knowledge": "text"
    },
    "role_status": {
      "enum": [
        "missing",
        "draft",
        "supplied",
        "reviewed"
      ]
    },
    "evidence_refs": {
      "array": {
        "reference": [
          "study_registration",
          "activity_readiness",
          "core_catalog",
          "artifact",
          "validation_receipt",
          "human_review",
          "adjudication",
          "collection_ledger",
          "extraction",
          "audit_selection",
          "correction_incident",
          "compilation_receipt"
        ]
      }
    }
  }
}
```

### 6.4. `artifact`

```json
{
  "object": {
    "content": {
      "knowledge": {
        "object": {
          "packet_id": "id"
        }
      }
    },
    "sha256": {
      "knowledge": "hash"
    },
    "size_bytes": {
      "knowledge": "nonnegative"
    },
    "artifact_role": {
      "enum": [
        "core_positive",
        "core_defect",
        "core_boundary",
        "candidate",
        "raw_response",
        "prompt",
        "source",
        "evidence",
        "review",
        "longitudinal_input",
        "compiled_output"
      ]
    },
    "original_source": {
      "knowledge": "text"
    },
    "transformations": {
      "array": {
        "object": {
          "transformation_id": "id",
          "source_refs": {
            "array": {
              "reference": [
                "artifact"
              ]
            }
          },
          "operation": "text",
          "performed_at": {
            "knowledge": "timestamp"
          },
          "operator": {
            "knowledge": "id"
          },
          "output_sha256": "hash"
        }
      }
    },
    "ai_assistance": {
      "knowledge": "text"
    },
    "exposure": {
      "knowledge": "text"
    },
    "evidence_refs": {
      "array": {
        "reference": [
          "study_registration",
          "activity_readiness",
          "core_catalog",
          "artifact",
          "validation_receipt",
          "human_review",
          "adjudication",
          "collection_ledger",
          "extraction",
          "audit_selection",
          "correction_incident",
          "compilation_receipt"
        ]
      }
    }
  }
}
```

### 6.5. `validation_receipt`

```json
{
  "object": {
    "artifact_ref": {
      "reference": [
        "artifact"
      ]
    },
    "artifact_sha256": "hash",
    "suite": {
      "object": {
        "suite_id": "id",
        "suite_version": "id",
        "manifest_sha256": "hash",
        "expected_test_count": "nonnegative"
      }
    },
    "coverage": {
      "object": {
        "representation": {
          "literal": "ordered_test_ids_v1"
        },
        "segments": {
          "array": {
            "object": {
              "segment_id": "id",
              "expected_count": "nonnegative",
              "observed_ids": {
                "array": "id"
              },
              "full_log_packets": {
                "array": "id"
              }
            }
          }
        },
        "declared_status": {
          "enum": [
            "complete",
            "partial",
            "not_performed"
          ]
        },
        "log_provenance": {
          "enum": [
            "locally_verified_content",
            "verified_external_receipt",
            "unavailable_attachment",
            "unchecked"
          ]
        }
      }
    },
    "trusted_observations": {
      "array": {
        "object": {
          "test_id": "id",
          "outcome": {
            "enum": [
              "pass",
              "violation",
              "undetermined",
              "harness_failure",
              "resource_exhausted"
            ]
          },
          "observation": "text",
          "evidence_packet_id": {
            "knowledge": "id"
          }
        }
      }
    },
    "counterexamples": {
      "array": {
        "object": {
          "test_id": "id",
          "input_packet_id": "id",
          "observation_packet_id": "id",
          "violation": "text"
        }
      }
    },
    "conformance_review": {
      "object": {
        "outcome": {
          "enum": [
            "satisfied_for_scope",
            "unsatisfied",
            "unresolved",
            "not_applicable"
          ]
        },
        "reviewer_ref": {
          "knowledge": {
            "reference": [
              "human_review"
            ]
          }
        },
        "evidence_refs": {
          "array": {
            "reference": [
              "study_registration",
              "activity_readiness",
              "core_catalog",
              "artifact",
              "validation_receipt",
              "human_review",
              "adjudication",
              "collection_ledger",
              "extraction",
              "audit_selection",
              "correction_incident",
              "compilation_receipt"
            ]
          }
        },
        "basis": {
          "knowledge": "text"
        }
      }
    },
    "environment": {
      "object": {
        "environment_id": {
          "knowledge": "id"
        },
        "image_sha256": {
          "knowledge": "hash"
        },
        "configuration_sha256": {
          "knowledge": "hash"
        },
        "isolation_review_ref": {
          "knowledge": {
            "reference": [
              "human_review"
            ]
          }
        }
      }
    },
    "oracle": {
      "object": {
        "oracle_id": {
          "knowledge": "id"
        },
        "source_sha256": {
          "knowledge": "hash"
        },
        "review_ref": {
          "knowledge": {
            "reference": [
              "human_review"
            ]
          }
        }
      }
    },
    "limits": {
      "object": {
        "cpu_seconds": {
          "knowledge": "exact_nonnegative"
        },
        "elapsed_seconds": {
          "knowledge": "exact_nonnegative"
        },
        "memory_bytes": {
          "knowledge": "nonnegative"
        },
        "output_bytes": {
          "knowledge": "nonnegative"
        }
      }
    },
    "termination": {
      "enum": [
        "completed",
        "counterexample",
        "resource_exhausted",
        "cancelled",
        "not_started",
        "unknown"
      ]
    },
    "harness_status": {
      "enum": [
        "ok",
        "failed",
        "not_assessed"
      ]
    },
    "validity_status": {
      "enum": [
        "valid",
        "invalid",
        "undetermined",
        "not_assessed"
      ]
    },
    "mechanism_observations": {
      "array": {
        "object": {
          "witness_id": "id",
          "relation": "text",
          "evidence_packet_id": {
            "knowledge": "id"
          }
        }
      }
    },
    "provenance": {
      "object": {
        "operator": {
          "knowledge": "id"
        },
        "performed_at": {
          "knowledge": "timestamp"
        },
        "original_receipt_packet": {
          "knowledge": "id"
        },
        "authenticity": {
          "enum": [
            "stipulated_fixture",
            "unverified",
            "externally_attested"
          ]
        },
        "attestation_ref": {
          "knowledge": {
            "reference": [
              "study_registration",
              "activity_readiness",
              "core_catalog",
              "artifact",
              "validation_receipt",
              "human_review",
              "adjudication",
              "collection_ledger",
              "extraction",
              "audit_selection",
              "correction_incident",
              "compilation_receipt"
            ]
          }
        }
      }
    }
  }
}
```

### 6.6. `human_review`

```json
{
  "object": {
    "artifact_ref": {
      "reference": [
        "artifact"
      ]
    },
    "artifact_sha256": "hash",
    "reviewer": {
      "object": {
        "reviewer_id": "id",
        "roster_packet_id": {
          "knowledge": "id"
        },
        "entity_kind": {
          "enum": [
            "human",
            "machine",
            "unknown"
          ]
        },
        "qualifications": {
          "knowledge": "text"
        },
        "relationships": {
          "knowledge": "text"
        },
        "exposure": {
          "knowledge": "text"
        },
        "machine_assistance": {
          "knowledge": "text"
        }
      }
    },
    "submission_stage": {
      "enum": [
        "draft",
        "initial",
        "revision"
      ]
    },
    "submitted_at": {
      "knowledge": "timestamp"
    },
    "initial_submission_ref": {
      "knowledge": {
        "reference": [
          "human_review"
        ]
      }
    },
    "independence": {
      "object": {
        "declared_independent": {
          "knowledge": "bool"
        },
        "evidence_refs": {
          "array": {
            "reference": [
              "study_registration",
              "activity_readiness",
              "core_catalog",
              "artifact",
              "validation_receipt",
              "human_review",
              "adjudication",
              "collection_ledger",
              "extraction",
              "audit_selection",
              "correction_incident",
              "compilation_receipt"
            ]
          }
        },
        "limitations": {
          "array": "text"
        }
      }
    },
    "blinding": {
      "object": {
        "pack_id": {
          "knowledge": "id"
        },
        "withheld_fields": {
          "array": {
            "enum": [
              "model",
              "condition",
              "proposed_role",
              "other_judgments"
            ]
          }
        },
        "limitations": {
          "array": "text"
        }
      }
    },
    "judgment": {
      "object": {
        "assignment_status": {
          "enum": [
            "assigned",
            "unresolved",
            "unclassified"
          ]
        },
        "structural_class_id": {
          "knowledge": "class_id"
        },
        "validity_status": {
          "enum": [
            "valid",
            "invalid",
            "undetermined",
            "not_assessed"
          ]
        },
        "rationale": {
          "knowledge": "text"
        },
        "evidence_refs": {
          "array": {
            "reference": [
              "study_registration",
              "activity_readiness",
              "core_catalog",
              "artifact",
              "validation_receipt",
              "human_review",
              "adjudication",
              "collection_ledger",
              "extraction",
              "audit_selection",
              "correction_incident",
              "compilation_receipt"
            ]
          }
        }
      }
    },
    "original_submission_packet": {
      "knowledge": "id"
    }
  }
}
```

### 6.7. `adjudication`

```json
{
  "object": {
    "artifact_ref": {
      "reference": [
        "artifact"
      ]
    },
    "artifact_sha256": "hash",
    "initial_review_refs": {
      "array": {
        "reference": [
          "human_review"
        ]
      }
    },
    "adjudicator": {
      "object": {
        "reviewer_id": "id",
        "roster_packet_id": {
          "knowledge": "id"
        },
        "entity_kind": {
          "enum": [
            "human",
            "machine",
            "unknown"
          ]
        },
        "qualifications": {
          "knowledge": "text"
        },
        "relationships": {
          "knowledge": "text"
        },
        "exposure": {
          "knowledge": "text"
        },
        "machine_assistance": {
          "knowledge": "text"
        }
      }
    },
    "independence": {
      "object": {
        "declared_independent": {
          "knowledge": "bool"
        },
        "evidence_refs": {
          "array": {
            "reference": [
              "study_registration",
              "activity_readiness",
              "core_catalog",
              "artifact",
              "validation_receipt",
              "human_review",
              "adjudication",
              "collection_ledger",
              "extraction",
              "audit_selection",
              "correction_incident",
              "compilation_receipt"
            ]
          }
        },
        "limitations": {
          "array": "text"
        }
      }
    },
    "disagreement": "text",
    "basis": {
      "knowledge": "text"
    },
    "judgment": {
      "object": {
        "assignment_status": {
          "enum": [
            "assigned",
            "unresolved",
            "unclassified"
          ]
        },
        "structural_class_id": {
          "knowledge": "class_id"
        },
        "validity_status": {
          "enum": [
            "valid",
            "invalid",
            "undetermined",
            "not_assessed"
          ]
        },
        "rationale": {
          "knowledge": "text"
        },
        "evidence_refs": {
          "array": {
            "reference": [
              "study_registration",
              "activity_readiness",
              "core_catalog",
              "artifact",
              "validation_receipt",
              "human_review",
              "adjudication",
              "collection_ledger",
              "extraction",
              "audit_selection",
              "correction_incident",
              "compilation_receipt"
            ]
          }
        }
      }
    },
    "unresolved_issues": {
      "array": "text"
    },
    "submitted_at": {
      "knowledge": "timestamp"
    },
    "original_submission_packet": {
      "knowledge": "id"
    }
  }
}
```

### 6.8. `collection_ledger`

```json
{
  "object": {
    "phase": {
      "enum": [
        "pilot",
        "main"
      ]
    },
    "block_id": {
      "enum": [
        "P00",
        "P01",
        "P02",
        "P03",
        "P04",
        "P05",
        "P06"
      ]
    },
    "condition": {
      "enum": [
        "A",
        "B",
        "C"
      ]
    },
    "group_index": "positive",
    "registered_call_order": "positive",
    "planned_positions": {
      "array": "positive"
    },
    "controls": {
      "object": {
        "temperature": {
          "knowledge": "exact_nonnegative"
        },
        "top_p": {
          "knowledge": "probability"
        },
        "presence_penalty": {
          "knowledge": "exact"
        },
        "frequency_penalty": {
          "knowledge": "exact"
        },
        "seed": {
          "knowledge": "integer_or_null"
        },
        "output_allowance": {
          "knowledge": "nonnegative"
        },
        "cap_semantics": {
          "knowledge": "text"
        },
        "fresh_context": {
          "knowledge": "bool"
        },
        "tools_requested": {
          "knowledge": "bool"
        },
        "hidden_controls": {
          "knowledge": "text"
        },
        "wrapper_knowledge": {
          "knowledge": "text"
        }
      }
    },
    "prompt_ref": {
      "knowledge": {
        "reference": [
          "artifact"
        ]
      }
    },
    "sent_prompt_sha256": {
      "knowledge": "hash"
    },
    "deployment": {
      "object": {
        "model_identifier": {
          "knowledge": "text"
        },
        "model_family": {
          "knowledge": "text"
        },
        "checkpoint_identifier": {
          "knowledge": "text"
        },
        "deployment_identifier": {
          "knowledge": "text"
        },
        "drift": {
          "knowledge": "text"
        }
      }
    },
    "attempt_status": {
      "enum": [
        "succeeded",
        "failed",
        "cancelled",
        "not_attempted",
        "unknown"
      ]
    },
    "attempt_id": {
      "knowledge": "id"
    },
    "request_id": {
      "knowledge": "text"
    },
    "attempted_at": {
      "knowledge": "timestamp"
    },
    "raw_response_ref": {
      "knowledge": {
        "reference": [
          "artifact"
        ]
      }
    },
    "termination_reason": {
      "knowledge": "text"
    },
    "retry_of": {
      "knowledge": {
        "reference": [
          "collection_ledger"
        ]
      }
    },
    "retry_evidence_refs": {
      "array": {
        "reference": [
          "study_registration",
          "activity_readiness",
          "core_catalog",
          "artifact",
          "validation_receipt",
          "human_review",
          "adjudication",
          "collection_ledger",
          "extraction",
          "audit_selection",
          "correction_incident",
          "compilation_receipt"
        ]
      }
    },
    "usage": {
      "object": {
        "input_tokens": {
          "knowledge": "nonnegative"
        },
        "output_tokens": {
          "knowledge": "nonnegative"
        },
        "hidden_reasoning_tokens": {
          "knowledge": "nonnegative"
        },
        "compute": {
          "knowledge": "text"
        },
        "monetary_cost": {
          "knowledge": "exact_nonnegative"
        },
        "currency": {
          "knowledge": "text"
        }
      }
    },
    "authorization_ref": {
      "knowledge": {
        "reference": [
          "study_registration",
          "activity_readiness",
          "core_catalog",
          "artifact",
          "validation_receipt",
          "human_review",
          "adjudication",
          "collection_ledger",
          "extraction",
          "audit_selection",
          "correction_incident",
          "compilation_receipt"
        ]
      }
    }
  }
}
```

### 6.9. `extraction`

```json
{
  "object": {
    "collection_ref": {
      "reference": [
        "collection_ledger"
      ]
    },
    "raw_response_ref": {
      "knowledge": {
        "reference": [
          "artifact"
        ]
      }
    },
    "raw_response_sha256": {
      "knowledge": "hash"
    },
    "rule_version": {
      "literal": "hero_candidates_v1"
    },
    "positions": {
      "array": {
        "object": {
          "within_group_index": "positive",
          "selection": {
            "enum": [
              "selected",
              "missing",
              "withheld"
            ]
          },
          "artifact_ref": {
            "knowledge": {
              "reference": [
                "artifact"
              ]
            }
          },
          "heading": {
            "knowledge": "text"
          },
          "fence": {
            "knowledge": "text"
          },
          "byte_range": {
            "knowledge": {
              "object": {
                "start": "nonnegative",
                "end": "nonnegative"
              }
            }
          },
          "completion_status": {
            "enum": [
              "complete",
              "truncated",
              "refused",
              "failed",
              "unknown"
            ]
          },
          "limitations": {
            "array": "text"
          }
        }
      }
    },
    "extras": {
      "array": {
        "object": {
          "heading": {
            "knowledge": "text"
          },
          "byte_range": {
            "object": {
              "start": "nonnegative",
              "end": "nonnegative"
            }
          },
          "reason": "text"
        }
      }
    },
    "limitations": {
      "array": "text"
    }
  }
}
```

### 6.10. `audit_selection`

```json
{
  "object": {
    "formula_id": {
      "literal": "hero_systematic_positions_v1"
    },
    "position": {
      "object": {
        "block_id": {
          "enum": [
            "P00",
            "P01",
            "P02",
            "P03",
            "P04",
            "P05",
            "P06"
          ]
        },
        "condition": {
          "enum": [
            "A",
            "B",
            "C"
          ]
        },
        "group_index": "positive",
        "within_group_index": "positive"
      }
    },
    "reasons": {
      "array": {
        "enum": [
          "systematic",
          "disagreement",
          "unresolved",
          "new_class",
          "rare_class",
          "invalid",
          "boundary",
          "other_registered"
        ]
      }
    },
    "artifact_ref": {
      "knowledge": {
        "reference": [
          "artifact"
        ]
      }
    },
    "opportunity": {
      "enum": [
        "present",
        "missing",
        "not_assessed"
      ]
    },
    "review_refs": {
      "array": {
        "reference": [
          "human_review"
        ]
      }
    },
    "distinct_artifact_count": "nonnegative",
    "basis": {
      "knowledge": "text"
    }
  }
}
```

### 6.11. `correction_incident`

```json
{
  "object": {
    "kind": {
      "enum": [
        "challenge",
        "correction",
        "incident",
        "retraction"
      ]
    },
    "challenge": "text",
    "provenance": {
      "knowledge": "text"
    },
    "affected_refs": {
      "array": {
        "reference": [
          "study_registration",
          "activity_readiness",
          "core_catalog",
          "artifact",
          "validation_receipt",
          "human_review",
          "adjudication",
          "collection_ledger",
          "extraction",
          "audit_selection",
          "correction_incident",
          "compilation_receipt"
        ]
      }
    },
    "reviewer_authority": {
      "knowledge": "text"
    },
    "action_status": {
      "enum": [
        "proposed",
        "performed",
        "rejected",
        "unresolved"
      ]
    },
    "action": {
      "knowledge": "text"
    },
    "replacement_refs": {
      "array": {
        "reference": [
          "study_registration",
          "activity_readiness",
          "core_catalog",
          "artifact",
          "validation_receipt",
          "human_review",
          "adjudication",
          "collection_ledger",
          "extraction",
          "audit_selection",
          "correction_incident",
          "compilation_receipt"
        ]
      }
    },
    "rollback_refs": {
      "array": {
        "reference": [
          "study_registration",
          "activity_readiness",
          "core_catalog",
          "artifact",
          "validation_receipt",
          "human_review",
          "adjudication",
          "collection_ledger",
          "extraction",
          "audit_selection",
          "correction_incident",
          "compilation_receipt"
        ]
      }
    },
    "reanalysis_refs": {
      "array": {
        "reference": [
          "compilation_receipt"
        ]
      }
    },
    "performed_at": {
      "knowledge": "timestamp"
    },
    "evidence_refs": {
      "array": {
        "reference": [
          "study_registration",
          "activity_readiness",
          "core_catalog",
          "artifact",
          "validation_receipt",
          "human_review",
          "adjudication",
          "collection_ledger",
          "extraction",
          "audit_selection",
          "correction_incident",
          "compilation_receipt"
        ]
      }
    }
  }
}
```

### 6.12. `compilation_receipt`

```json
{
  "object": {
    "input_snapshots": {
      "array": {
        "object": {
          "packet_id": "id",
          "sha256": "hash",
          "study_version": "id"
        }
      }
    },
    "target_profile": {
      "enum": [
        "m_only",
        "hero_sort_abc_v1",
        "structdet_longitudinal_v1"
      ]
    },
    "target_input_schema_version": {
      "literal": "0.1"
    },
    "disposition": {
      "enum": [
        "eligible",
        "withheld",
        "readiness_only"
      ]
    },
    "claim_disposition": {
      "enum": [
        "supported_for_scope",
        "restricted",
        "withheld"
      ]
    },
    "analysis_bundle_created": "bool",
    "id_map": {
      "array": {
        "object": {
          "source_ref": {
            "reference": [
              "study_registration",
              "activity_readiness",
              "core_catalog",
              "artifact",
              "validation_receipt",
              "human_review",
              "adjudication",
              "collection_ledger",
              "extraction",
              "audit_selection",
              "correction_incident",
              "compilation_receipt"
            ]
          },
          "target_record_type": {
            "enum": [
              "frame",
              "protocol",
              "cell",
              "attempt",
              "realization",
              "assignment",
              "validity",
              "artifact",
              "raw_artifact",
              "reference_registry",
              "evidence",
              "role",
              "lineage",
              "independence_assessment",
              "annotation",
              "adjudication",
              "domain_suite",
              "domain_result",
              "audit",
              "exposure",
              "integrity_assessment",
              "intake",
              "tail",
              "correction",
              "preregistration",
              "budget",
              "sampling_plan",
              "source"
            ]
          },
          "target_record_id": "id"
        }
      }
    },
    "outputs": {
      "array": {
        "object": {
          "path": "path",
          "sha256": "hash",
          "size_bytes": "nonnegative",
          "role": {
            "enum": [
              "bundle",
              "payload",
              "readiness",
              "provenance",
              "manifest",
              "report"
            ]
          }
        }
      }
    },
    "unresolved_restrictions": {
      "array": "text"
    },
    "mapping_errors": {
      "array": {
        "object": {
          "source_ref": {
            "reference": [
              "study_registration",
              "activity_readiness",
              "core_catalog",
              "artifact",
              "validation_receipt",
              "human_review",
              "adjudication",
              "collection_ledger",
              "extraction",
              "audit_selection",
              "correction_incident",
              "compilation_receipt"
            ]
          },
          "field": "id",
          "reason": "text"
        }
      }
    },
    "evidence_refs": {
      "array": {
        "reference": [
          "study_registration",
          "activity_readiness",
          "core_catalog",
          "artifact",
          "validation_receipt",
          "human_review",
          "adjudication",
          "collection_ledger",
          "extraction",
          "audit_selection",
          "correction_incident",
          "compilation_receipt"
        ]
      }
    }
  }
}
```

### 6.13. Semantic relationships across fields

- Study registration retains exact SD/SI/EC hashes and all task/resolution/schema/registry/rubric pins. Profile values are `m_only` (an operational selector for no legacy optional extension), `hero_sort_abc_v1`, or `structdet_longitudinal_v1`. The longitudinal selector requires the `supplied_longitudinal` design; comparison requires `sorting_abc`. A supplied profile carrier must declare the same profile. A/B/C records never manufacture training states or transitions.
- Readiness prerequisites have unique IDs. The outstanding list is exactly the mandatory requirements not declared satisfied. Mandatory not-applicable is contradictory. An optional not-applicable outcome requires a known justification in its basis field; a nonknown basis cannot supply that justification. `ready` with mandatory gaps is contradictory. The parser checks consistency of a claim of readiness; genuine activity readiness is qualified later.
- Core catalog rows represent stable desired roles independently of actual material. `missing` has no known artifact; `supplied` and `reviewed` have a known reference. One catalog row does not imply that all 32 slots or actual programs exist. Step 3 enforces the complete catalog design.
- Artifact identity is independent of its label. All known hashes and sizes along artifact, inventory and acquired bytes must agree. Multiple known hash claims for one artifact ID must agree even when its artifact/packet metadata and physical bytes are unavailable; different artifact IDs remain distinct even when their hashes match. A receipt, human review or adjudication's artifact hash must agree with a known artifact hash or known backing packet hash. After acquisition, every known referring receipt, review, prompt and response hash is also compared directly with actual target bytes, even when both artifact and packet expectations were unknown. Changing bytes therefore cannot silently reuse an old known receipt association.
- Validation coverage is lossless `ordered_test_ids_v1`. Segment order and test-ID order remain supplied order. IDs are unique across segments, and complete coverage has exactly each declared segment count; segment counts sum to the suite count. Excess coverage and a populated not-performed coverage fail. Repeated equal test inputs remain distinct identities. Step 3 verifies the actual 8,995 identities and suite manifest; this parser only verifies structural/count consistency and never treats a summary as full-log evidence.
- Each full-log packet must be declared. `coverage.log_provenance` and `packet_inventory.verification` remain supplied assertions, separately reported from actual acquisition. Generic attached bytes or an arbitrary reference cannot become an externally verified receipt. Full-log review, authentic execution, oracle quality, containment and mechanism evidence have their distinct later requirements.
- A declared `valid` validation receipt has complete coverage, completed termination, an OK harness and satisfied conformance shape. A declared `invalid` receipt supplies counterexample entries. Resource exhaustion alone cannot become invalidity. Those consistency rules do not establish the truth of the declared observations or source conformance.
- A review revision points to an initial submission for the same artifact bytes and claimed reviewer identity. An initial or draft submission has no known initial-submission predecessor. Adjudication links preserve initial submissions for the same artifact/hash. A validation receipt's conformance reviewer refers to a human review of that exact artifact and hash; generic evidence references retain their broader roles. No first pass is overwritten. Distinct JSON identities do not establish two real independent people; human independence and expert qualification remain Step 4/6 and E03/E04 obligations.
- Mechanism judgments preserve `assigned`, `unresolved`, and `unclassified`. Only assigned has a known registered class. Validity separately preserves `valid`, `invalid`, `undetermined`, and `not_assessed`. A label-conditioned calculation may later be representable while a stronger claim remains restricted.
- A collection row retains all five planned indices `[1,2,3,4,5]`. Pilot rows use P00 and groups 1–2; main rows use P01–P06 and groups 1–4. Conditions remain A/B/C. A not-attempted row cannot carry a known actual attempt, response or attempt time. Whole-ledger enumeration and exact registered order first occur at Step 5.
- Extraction retains five ordered position rows, including missing positions. Selected rows need a source response, artifact and nonreversed byte span; missing rows have neither artifact nor byte span. Known source sizes bound selected spans. Extras retain their own source spans and limitations. Step 5 checks actual heading/fence rules and exact source-byte reconstruction; Step 2 does not extract or repair code.
- Audit selection retains systematic/targeted reasons and missing opportunities. One present position names one artifact; a missing opportunity has no known artifact and count zero. A present audit cannot contradict a known missing extraction at the same position, substitute a different known extracted artifact, or link a human review of another artifact. A missing audit opportunity cannot contradict a known selected extraction. Step 6 materializes the fixed 72 positions and deduplicated targeted selection.
- A proposed correction has no performed timestamp. A declared performed action has a known action and timestamp, without any inference that it really happened. Explicit affected/replacement/rollback/reanalysis relationships remain separate. Step 7 propagates dependency invalidation and requires new byte-bound evidence where applicable.
- A compilation receipt's profile agrees with registration. A claimed created bundle requires an eligible disposition, exactly one bundle output and no mapping errors. Readiness-only/withheld outputs cannot contain a bundle. Output paths are unique, safe, and hash/size pinned. This passive receipt does not create or validate an output file.

## 7. Passive acquisition and evidence packets

`load_study` reuses the unchanged `local_io.LocalReader` and `parse_json_bytes`. Each local path is relative to the envelope's directory. Absolute paths, drive/URL syntax, tilde or environment expansion, backslashes, control characters, empty/dot/parent components, and colons are rejected. The reader anchors the root with held descriptor-relative no-follow directory opens; symlinks and nonregular files are rejected. Before/after file identity and size must agree. There is no archive extraction, directory discovery, network fetch, subprocess, dynamic import, code evaluation or model call.

A location can deliberately be unknown, unavailable, or not applicable with its reason. A known external locator is retained verbatim as passive metadata and is never fetched. An absent declared local file is a warning, with its missing opportunity retained. Unsafe/unreadable files other than a genuinely absent path, changed files, mismatched known hashes/sizes/counts and over-budget imports are errors. Excess content requires an explicitly partitioned new import; it is never truncated, sampled or omitted to obtain a pass.

`LoadedStudy.snapshots` is an immutable mapping from acquired relative path to the inherited `ByteSnapshot(path, size_bytes, sha256, content)`. Original bytes are preserved exactly. Each `AttachmentInspection` includes `packet_id`, `declared_verification`, `status`, expected/actual hash, expected/actual size, and `checked_record_count`.

| Observed attachment status | Meaning |
|---|---|
| `snapshot_verified` | Local bytes acquired, with both declared hash and size known and matching. This is byte verification only. |
| `snapshot_read_unverified` | Local bytes acquired but one or both expected identity quantities remain unknown. |
| `unavailable_attachment` | Location absent or supplied local file missing; no invented empty content. |
| `external_not_fetched` | External locator retained; no network action or qualified external attestation. |
| `hash_mismatch`, `size_mismatch`, `record_count_mismatch` | A supplied identity/count conflicts with actual bytes; input error. |
| `rejected` | Other safe-reading, packet grammar, or budget error. |

`locally_verified_content`, `verified_external_receipt`, `unavailable_attachment`, and `unchecked` in the input inventory are declared provenance categories. A nonunchecked category produces an `unverified_attachment` warning during structural parsing. The loader's observed status is reported independently. The Step 2 implementation never emits a substantively qualified external receipt merely from `verification_ref`, a hash, a declared flag, or attached JSON. Later packet qualification must bind the exact packet identity and actual checked observations/attestation before a downstream claim can rely on it.

Multiple bounded packets can preserve full-log associations without placing millions of observations inside one legacy analysis bundle. Every operation still supplies a finite inventory and its own byte/record limits. No recursively fetched packet list, automatic inventory expansion or unbounded partition iterator exists. Downstream receipts must identify exactly the checked packet contents and distinguish unavailable logs from a genuinely checked external attestation. The compiled legacy bundle independently satisfies its original limits.

## 8. Explicit legacy field crosswalk

The existing formats and modules remain unchanged. This table fixes representational sources; it does not implement compilation at Step 2. Later compilation must use the original parsers/evidence functions and reject contradictory or lossy mappings. References below to a supplied legacy profile mean `study_registration.protocol.legacy_profile_input`.

### 8.1. Exact passive legacy-profile carrier

`legacy_profile_input` is either explicit uncertainty or exactly `{artifact_ref, input_schema_version:"0.1", profile}` under a known wrapper. Its artifact has exact supplied local-byte identity under the normal packet rules. The referenced bytes are an entire existing input-format JSON bundle declaration, not arbitrary new operational extension fields. Every file it names must also be explicitly inventoried for the compilation operation. No filename, role text or declared profile selects an alternative parser.

At Step 7 the compiler must parse the carrier using the unchanged `INPUT_FORMAT.md`, and the selected `COMPARISON_FORMAT.md` or `LONGITUDINAL_FORMAT.md`, including all existing support-record grammars. It must check the carrier study ID, material role, frame/task pins, evidence policy, exact versions, artifact hashes, call/group/position associations and every known overlapping operational fact. Unknown operational metadata cannot overwrite a known legacy fact, and the carrier cannot override a contradictory known operational fact. A contradiction is a mapping error. A missing carrier is well-formed input, with any dependent conversion withheld until its required fields are independently representable.

This carrier resolves detailed representation beyond the operational summary fields while retaining existing accepted meanings. It is never promoted to a validated analysis bundle merely by `load_study`. An actual longitudinal record graph must come from the declared carrier or explicitly supplied `protocol.longitudinal_input` and satisfy the unchanged fourteen-family longitudinal grammar. If both are supplied they must identify compatible exact input; the compiler cannot blend incompatible versions.

### 8.2. Core bundle and records

| Compiled legacy field(s) | Exact operational source or required validated carrier content |
|---|---|
| `input_schema_version` | Existing literal `0.1`, checked against carrier/compilation receipt. |
| `bundle_id`, `study_id`, `data_role` | Explicit output identity in compilation provenance; envelope study ID and `material_role`; carrier identity must agree. No generated output ID is a registration claim. |
| `source_pins` | Registration's exact SD/SI/EC object transformed to the existing source-ID/hash array. No original source PDF is copied or fetched. |
| Frame `frame_id`, task/version, resolution/version, structural schema/version, registry/version, `validity_rubric_ref` | Explicit compilation `id_map` and registration pins. Output frame identity is recorded, never guessed from a mechanism label. |
| Frame `task_context`, `consequence_horizon`, `load_bearing_invariants`, `consequence_signature_spec`, `equivalence_rule_ref`, `admissible_substitutions`, `evidence_requirement`, `exceptional_case_rules` | Corresponding `frame_definition` fields when fully known; otherwise exact validated carrier frame. Mandatory legacy plain text cannot be filled with an unknown placeholder. |
| Frame `registration_ref`, optional `registry_ref`; registry `classes`, `validation_status`, `provenance`, `source_fragments` | Qualified translated preregistration/core evidence or the exact validated carrier registry/support records. A 32-role catalog does not synthesize validated descriptors or registry provenance. |
| Protocol `generation_protocol_id`, `generation_protocol_version` | Registration `protocol_id`, `protocol_version` with explicit output ID mapping. |
| Protocol `conditioning_context_ref`, `decoding_settings`, `seed`, optional shared-context/sampling/intervention refs | Exact prompt association and controls when representable; full validated carrier protocol for detailed conditioning/control evidence. Known no-fixed-seed null remains distinct from unknown. |
| Cell `analysis_cell_id`, `frame_id`, protocol ID/version, `prompt_block_id`, `prompt_id`, `condition_id` | Explicit mapped cell identity and collection block/condition/protocol; distinct call groups remain within their declared cell. Prompt identity must be supplied or recorded in the mapping. |
| Cell `model_identifier`, `model_family`, `checkpoint_identifier`, `collection_window`, optional budget/recursive/parent/transition refs | Collection deployment/attempt chronology and qualified supporting carrier records. A/B/C labels never become recursive rounds or transitions. |
| Attempt `attempt_id`, `analysis_cell_id`, `attempt_status`, `retry_of`, `raw_response_ref`, `generation_group_id`, `planned_candidate_count`, `registered_call_order`, termination/budget refs | Collection row plus explicit output mapping. Preserve all five planned positions, registered call order, actual retry evidence and failed/not-attempted status. Group identity is explicit, not compressed after missing outputs. |
| Realization `sample_id`, cell/attempt/raw-response/output refs, output hash, group/index/order, `extraction_rule_version`, `completion_status`, optional selection/termination/context/group fields | Collection/extraction positions and exact artifact bytes with a recorded ID map. Missing positions remain in planning/accounting; they cannot become fabricated realizations. Supplied extraction rule identity must match the existing rule before compilation. |
| Assignment identity/version, sample/frame, `assignment_status`, `structural_class_id`, method/rationale/evidence refs, evidence policy/version, supersession | Qualified human/adjudication judgment for exact artifact bytes, envelope evidence policy, recorded output identity and correction graph. The parser's declared judgment alone cannot create an accepted assignment. |
| Assignment `assignment_review_status`, optional `candidate_class_ids`, uncertainty/disagreement/role/correction/hash fields | Exact validated carrier assignment/support evidence or a later explicit qualified mapping. A draft/initial/revision stage does not imply `fixture`, `provisional`, or `adjudicated`; unresolved candidate classes cannot be discarded. |
| Validity identity/version, sample, `validity_status`, rubric/review state, evidence/rationale/supersession and optional observation/role/correction refs | Qualified separate validity evidence and explicit output mapping. Preserve invalid-but-classifiable, valid-but-unresolved, undetermined and not-assessed. Review status requires the exact carrier or qualified mapping; completion of a human form is insufficient. |
| Artifact/raw-artifact `artifact_id`, `content_ref`, `expected_sha256`, `knowledge_type`, transformation/external-locator/material-role fields | Explicit artifact and packet association; original response/code bytes unchanged. `knowledge_type` and detailed provenance come from supplied evidence or carrier, with unknown preserved where legacy grammar permits. |
| `analysis_config` order/selection, `requested_k`, registered positions/sample order, assignment/validity version pins, frequency threshold, evidence-policy identity/version, numeric settings and revision pins | Exact validated carrier `analysis_config`, crosschecked against operational design and output identities. No threshold, budget, favorable subset, estimator or ordering is silently defaulted. |
| `record_files` role/format/path/hash | Actual compilation payload inventory and exact output hashes. The compiler publishes only the complete validated set into a fresh directory. |
| Support records `evidence`, `role`, `lineage`, `independence_assessment`, `annotation`, `adjudication`, `domain_suite`, `domain_result`, `audit`, `exposure`, `integrity_assessment`, `intake`, `tail`, `correction`, `preregistration`, `budget`, `sampling_plan`, `source` | Typed operational evidence translated only where every existing payload field is representable; otherwise exact validated carrier records under the corresponding inherited evidence grammar. Common provenance, scope, authority, exposure and knowledge fields remain present. A new-family name does not authorize an arbitrary legacy payload. |

### 8.3. Comparison profile

| Existing comparison field family | Required source and preserved distinction |
|---|---|
| Version, comparison ID/version, exact `profile`, six blocks, condition cell/study-record references, pilot refs, P1/P5 questions, two classified views | Exact registered design plus validated carrier comparison object and explicit cell mapping. Pilot/main separation and all six original blocks remain fixed. |
| Per-cell `payload.extensions.study_binding`: `version`, comparison ID/version, block/condition IDs, `protocol_ref`, `sent_prompt.{artifact_ref,attestation_ref}`, `visible_system_instruction`, `platform_context`, `reasoning`, `controls`, `cap`, `budget_ref`, four ordered `attempts`, `automatic_retries`, `deployment`, `deviations` | Exact validated `study_binding_v1` comparison evidence records, crosschecked against registration, artifact bytes, controls and extraction positions. Preserve each deviation code/detail/evidence array and serving-identity/change-detected evidence. Unknown bindings or retries remain unknown. |
| Requested/actual/enforced controls and evidence refs | Validated carrier control records. The simple operational `controls` values summarize supplied knowledge and cannot create three separate requested/actual/enforcement facts. Preserve tools, retrieval, history, best-of, hidden/system/developer/reasoning controls, automatic/observable retries, and missing settings. |
| Cap amount/unit/tokenizer/convention, seed policy, output-selection controls, deployment identity/change detection/evidence and collection timing | Exact validated carrier fields, crosschecked against operational allowance/usage/deployment records. A provider's cap or hidden-control semantics are never assumed. |
| `evidence` groups, text method, extraction/replay identities, resampling generator/seed/quantile/index data, engineering limits, revision prior-comparison/run IDs and reason/change fields | Exact validated carrier comparison extension and its support records. Preserve the original seven evidence groups and all existing method, limit and revision fields without deriving scientific parameters from prose. |
| P1/P5 operands, primary/sensitivity populations, quality gates, estimates, ranges and report schema | Existing analysis implementation after validated compilation. They have no replacement estimator or numerical field in this operational parser. |

### 8.4. Longitudinal profile

The exact carrier extension is `analysis_config.extensions.longitudinal`, version `0.1`, profile `structdet_longitudinal_v1`, method `longitudinal_records_v1`. Preserve `study_id`, `study_version`, `data_role`, `registered_design_ref`, `source_pins`, the unique capability subset, and limits. All fourteen original collections remain required: `states`, `panels`, `measurements`, `roots`, `transitions`, `trajectories`, `observed_requests`, `null_scenarios`, `shl_requests`, `assays`, `interventions`, `recovery_episodes`, `revisions`, and `replays`.

Every nested object, object-version reference, evidence dictionary, actual state/transition/trial observation, input hash, replay identity and correction relation follows `LONGITUDINAL_FORMAT.md` and the existing modules. The declared carrier is the explicit source for these fields. An unknown longitudinal input remains a readiness gap. Sorting conditions, repeated generation groups or a prose intervention description cannot synthesize any of them. M-only, comparison and longitudinal requests remain separate profiles.

### 8.5. Sidecars and unrepresentable distinctions

Operational readiness per activity, original review chronology, restricted identity maps, requested-versus-actual control evidence not representable in a selected legacy field, packet acquisition state, claim currentness, EC disclosures, monetary knowledge, authorization, correction proposed/performed state and empirical qualification survive in the readiness/provenance/compilation sidecars even when the numerical bundle has no corresponding slot. They must not be collapsed into a legacy numeric zero, false flag, accepted label, generic review state or global integrity score.

A format-0.1 operational packet without the needed validated carrier or later qualified typed mapping cannot encode every existing assignment candidate-set/review-status nuance or every inherited correction category, descriptor split/merge/recut and revision state. That requested conversion is explicitly **unrepresentable** and must produce a field-level `mapping_errors` entry, withhold the affected bundle/claim, and retain the original information in the source association. The compiler must never infer those enum values from free text. The exact legacy carrier provides a representable route under the unchanged schema; it is not permission to enlarge an existing accepted meaning.

The compilation receipt retains accepted/withheld/readiness-only disposition separately from `supported_for_scope`, `restricted`, or `withheld` claim disposition. Numeric availability never proves independent evidence, operational openness, all-five EC satisfaction, software completion, remote delivery, or owner acceptance.

## 9. Diagnostics and provenance limits

Diagnostics use inherited `Diagnostic(code, scope, source, field, line, severity)`. This module uses `scope="study"`, `source="study"`, and schema-owned field paths with ordinal indexes. Untrusted record IDs, path text, reviewer identities, payloads, secrets and exception messages are not interpolated into errors. Multiple independent shape findings can be returned; reference semantics run only after successful shape validation.

Stable schema/semantic diagnostic codes:

`missing_field`, `unknown_field`, `invalid_type`, `invalid_value`, `unsupported_study_schema_version`, `unsupported_record_version`, `unsupported_record_type`, `invalid_reference`, `reference_type_mismatch`, `reference_version_mismatch`, `missing_reference`, `duplicate_record_id`, `duplicate_packet_id`, `duplicate_packet_path`, `duplicate_value`, `study_identity_mismatch`, `study_version_mismatch`, `scope_mismatch`, `registration_count`, `profile_contradiction`, `fixture_policy_mismatch`, `supersession_type_mismatch`, `supersession_revision_order`, `supersession_cycle`, `dependency_cycle`, `artifact_hash_mismatch`, `attachment_hash_mismatch`, `attachment_size_mismatch`, `attachment_record_count_mismatch`, `attachment_unavailable`, `external_attachment_not_fetched`, `unverified_attachment`, `packet_not_declared`, `invalid_knowledge`, `invalid_knowledge_state`, `missing_knowledge_reason`, `known_value_missing`, `value_in_unknown_state`, `coverage_count_mismatch`, `coverage_duplicate_test_id`, `coverage_overflow`, `position_contradiction`, `state_contradiction`, `budget_exceeded_partition_required`, `unsupported_read_limit`, `invalid_study_for_serialization`, `invalid_json_value`, `input_not_bytes`, `file_size_exceeded`, `bundle_size_exceeded`, `line_size_exceeded`, `record_count_exceeded`, `json_depth_exceeded`, `number_token_too_long`, `duplicate_json_key`, `nonfinite_number`, `invalid_json`, `invalid_utf8`, `utf8_bom_not_supported`, `unpaired_unicode_surrogate`, `unsafe_local_path`, `remote_or_drive_path`, `unsafe_or_unreadable_local_file`, `not_regular_file`, `file_changed_during_read`, `invalid_jsonl_record`.

Inherited local-reader capability/root failures can also be returned unchanged as bounded codes, including `safe_local_open_unavailable`, `unsafe_bundle_root`, `unsafe_or_unreadable_bundle_root`, and `closed_local_reader`. A budget failure identifies the need to partition the input; it never authorizes changing the hard ceilings.

Hash matching proves identity of acquired supplied bytes. It does not prove human identity, independence, original execution, chronology, suitability of containment, source rights, study readiness or scientific truth. Actual scientific qualification, compilation, publication and empirical activities retain their separate implementation steps and evidence requirements.

## 10. Fixture and revision inventory

The Step 2 software fixtures are `tests/fixtures/phase4/study_complete.json`, `study_partial.json`, `study_malformed.json`, `study_expected.json`, and `study_payload.txt`. Their independent tests are in `tests/test_study_records.py`. Complete and partial packets are well-formed with stipulated uncertainty; malformed input demonstrates a controlled rejection. No fixture contains real reviewer contact details, credentials, acquired model output or actual candidate execution evidence.

A later grammar change requires a recorded exact change, compatible version handling and independent regression. Historical records and frozen predecessor contracts remain intact. Subsequent modules consume this grammar and must not weaken the passive boundaries or promote structural declarations into empirical evidence.
