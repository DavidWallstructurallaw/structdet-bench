# Passive sorting validation receipts, version 0.1

This contract supplements the unchanged `STUDY_FORMAT.md` validation-receipt family and `INPUT_FORMAT.md` §§13.1–13.3. It introduces no candidate runner, conformance scanner, model judge, expert identity or empirical execution. All content is parsed passively from already acquired immutable local snapshots. The Phase 4 Step 3 API reports which bounded judgments the supplied records support. It cannot authenticate an external run or prove independent human conduct.

## Public API

- `sorting_inputs()` returns fresh ordered test rows; `sorting_manifest()` returns the legacy `{version, tests, sha256}` object.
- `validate_sorting_manifest(raw_or_bytes, limits=None)` accepts that object or the tests array, checks every exact identity, construction, position and digest, and returns `ManifestInspection` with `diagnostics`, `has_errors`, `exit_code`, `test_count`, `sha256`.
- `parse_validation_packet_bytes(data, limits=None)` returns `ValidationPacket` with immutable `data`, `diagnostics`, `has_errors` and `exit_code`.
- `inspect_validation_receipt(loaded_study, receipt_id, limits=None)` consumes a `LoadedStudy` produced by the unchanged `load_study`. It returns `ValidationAssessment` with the supported `validity_status`, actual `coverage_status`, `observed_count`, `expected_count`, `missing_ids`, `duplicate_ids`, `mechanism_status`, preserved `mechanism_observations`, `evidence_policy`, `material_role`, `qualification_status`, diagnostics and exit status.

Diagnostic errors yield exit code 2; missing evidence is inspectable uncertainty with warning diagnostics and can retain exit code 0. `substantive_validation_performed` is always false. `qualification_status` is `fixture_only` for a fixture study and `external_authentication_required` otherwise. A computed `valid` or `invalid` describes the supported state of supplied records under this bounded rubric; it is not independent execution by this API.

## Exact full-log packet

A full-log attachment uses inventory `format: json`, a known local location, known expected hash and size, and a declared packet ID. The existing study loader must acquire its bytes and report `snapshot_verified`. Declaring `locally_verified_content` or `verified_external_receipt` is insufficient. External locations are not fetched. The full-log JSON object has exactly these fields:

| Field | Required type or value |
|---|---|
| `validation_packet_version` | String `0.1` |
| `packet_id` | Registered study packet ID |
| `study_id`, `study_version` | Exact receipt study identity and version |
| `receipt_ref` | Exact three-key study reference to this `validation_receipt` |
| `artifact_ref`, `artifact_sha256` | Exact receipt artifact reference and lowercase SHA-256 |
| `suite_sha256` | `4b8dce8c2523bc953286bf853a0e17764e8fbaa6c71cc024b4e60d39feb17c11` |
| `scope` | Exact `{claim_id, task_id: bounded_integer_sort, task_version: 0.1}` receipt scope |
| `rubric_id` | `bounded_integer_sort_validity_v1` |
| `environment_configuration_sha256`, `environment_image_sha256` | Exact known receipt configuration and image hashes |
| `environment_id`, `oracle_id` | Exact known receipt environment and oracle identities |
| `oracle_source_sha256` | Exact known receipt oracle implementation hash |
| `environment_check` | Exact object described below |
| `observations` | Ordered array of observation rows |

`environment_check` has exactly `containment_status` (`passed`, `failed`, `not_assessed`), `accommodated_class_ids` (unique registered class IDs), `isolation_review_ref` and `oracle_review_ref` (typed human-review references). The review references must equal the corresponding known receipt references. A complete validity judgment requires passed containment and all eight families. Missing configuration, image, oracle identity, source identity or review association withholds validity. A conflicting known association is an error. These are supplied review associations, not proof that the environment actually behaved as described.

Every observation row has exactly `test_id`, `runtime_status`, `property_checks` and `violation`. Runtime states retain the existing vocabulary: `completed`, `timeout`, `memory_limit`, `exception`, `prohibited_capability`, `output_protocol_failure`, `harness_error`, `containment_failure`, `oracle_error`.

`property_checks` has exactly six fields: `fresh_plain_list`, `plain_integers`, `length_preserved`, `nondecreasing`, `multiplicity_preserved`, `input_unchanged`. Each is a strict knowledge wrapper: `{state: known, value: true|false}`, or `{state: unknown|unavailable|not_applicable, reason: nonblank text}`. No native float, integer stand-in for boolean, unknown-to-false conversion or omitted property is allowed.

`violation` is a knowledge wrapper. A known value has exactly:

- `property`: one of the six functional properties, or `syntax`, `prohibited_capability`, `exception`, `output_protocol`;
- `observed_violation`: the literal boolean true;
- `evidence_refs`: a nonempty array of exact study references for a decisive judgment.

An unknown, unavailable or not-applicable violation uses the same strict nonknown wrapper. A complete passing row requires runtime completed, all six known true properties, and violation explicitly not applicable. Unknown violation knowledge does not become known absence.

## Coverage and association

The receipt suite is exactly `sorting_functional_suite/0.1`, expected count 8,995 and the fixed canonical tests-array hash. Its coverage contains the four segments in the registered order with exact counts. Each segment lists its ordered `observed_ids` and `full_log_packets`. A packet may cover multiple segments and be named by those segments; it is read and counted once. Multiple packets retain the first-declared packet order. Actual rows must retain the global registered test order; repeated equal input values under different IDs remain separate tests.

A verified local tests-array attachment is required, with that exact canonical byte hash and all 8,995 checked rows. The artifact's actual snapshot must match the receipt artifact hash. Unknown artifact declarations cannot bypass the acquired-byte comparison. Every log header must bind the exact receipt, artifact, study, version, claim scope, rubric, suite, environment and oracle. A different record ID remains a different artifact even if bytes happen to match.

Actual observations come only from verified parsed log packets. The actual per-segment IDs must equal the receipt's declared IDs. Duplicate or unknown test IDs, reordered rows, wrong packet associations, inconsistent segment inventories and false complete-coverage claims are errors. Missing or incomplete genuine material remains inspectable limited evidence; declared summaries do not fill its gaps.

`trusted_observations` is an optional summary, not a second observation source. If supplied, every test must exist in actual logs, a known packet reference must match the actual row's packet, and pass/violation/harness/resource/undetermined assertions must agree with that row. A contradictory summary or nonexistent summarized identity is an error. Summary prose is preserved without being treated as execution.

The conformance receipt must say `satisfied_for_scope`, with meaningful known basis, evidence references and a resolvable human review of the same artifact/hash/scope. Conformance, oracle and isolation review references must resolve to nondraft human records with declared qualifications, independence and meaningful rationale/evidence. These checks inspect supplied review records only. One supplied review may cover more than one role when explicitly referenced; this does not certify that those roles were independently performed. Later human-admission and authenticity work remains necessary.

## Outcome rules

A supported `valid` state requires exact complete actual coverage, six known passing properties on every row, completed termination, functioning harness, the verified artifact and input manifest, conformance review and environment/oracle association. Passing these inputs is bounded tested evidence, not exhaustive proof over every legal list.

A supported `invalid` state can use a decisive counterexample before the suite completes. Its receipt entry identifies the exact local input packet, actual observation packet, tested ID and violation property. A functional violation must have completed runtime and that exact property known false. An exception, prohibited capability or output-protocol violation must match its corresponding observed runtime state. A syntax observation uses the exception runtime. Supporting references must resolve in the same study/version/scope. A supporting human review, validation receipt or adjudication must also identify this exact artifact reference and hash; a record about another artifact cannot supply the counterexample. The source, input and environment/oracle associations must be supported. Unsupported allegations or mismatched counterexamples are rejected.

Harness failure, oracle failure, containment failure, cancellation, resource exhaustion, incomplete coverage and missing evidence yield `undetermined` unless independently decisive associated evidence establishes the scoped violation. A timeout never proves nontermination. Empty, explicitly unassessed evidence can retain `not_assessed`.

Functional evidence never certifies mechanism membership. `mechanism_observations` remains separate and `mechanism_status` remains `unresolved` in this Step 3 importer. Names, matching outputs, trace prose or complete functional coverage cannot select a structural family. The supplied mechanism evidence must undergo the later appropriate review and admission.

## Bounded import and serialization

The unchanged ceilings remain: 16 MiB per file, 64 MiB per bundle, 1 MiB per JSON line, 100,000 logical records, depth 64 and 1,024 characters per number token. Caller limits may only tighten them. Duplicate JSON keys, unsupported versions, unknown fields, nonfinite values, invalid UTF-8 and unsafe local paths are rejected. Direct manifest mappings undergo the equivalent canonical-byte bounds.

Inspection rechecks acquired-byte identities and counts every acquired file, including the study envelope and otherwise unused attachments, against stricter caller byte ceilings. Existing JSON/JSONL packet counts are retained; each functional test row and each full-log observation is additionally counted as a logical record instead of hiding a large array behind one JSON object. Multiple artifacts' logs must be partitioned into finite declared packets within the same ceilings. No automatic remote retrieval, archive expansion, candidate import or execution occurs.

`sorting_inputs.json` and the materializer's sidecar have deterministic ASCII-escaped, sorted-key compact JSON plus LF. Full-log packets may use any strict valid bounded UTF-8 JSON layout; their expected SHA-256 identifies the exact acquired bytes. No hash is reconstructed from summaries or repaired after tampering. Diagnostic paths contain schema-owned names rather than arbitrary candidate text.
