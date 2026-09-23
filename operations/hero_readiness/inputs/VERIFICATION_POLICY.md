# StructDet-Bench

## Verification Consolidation and Post-Phase-3 Engineering Policy

Status: Adopted by the owner's instruction on 2026-09-22, following the completed Phase 4 Step 3 delivery.

This policy governs subsequent engineering and verification decisions. Where the earlier Phase 4 plan requires permanent preservation of historical test identities, repeated historical gate inheritance, or additional administrative verification layers, this newer instruction takes precedence. Scientific contracts, evidence distinctions, and controls protecting distinct computational, security, or release failures remain binding.

### Purpose

StructDet-Bench has reached a stage where its core M, V, and L software behavior has extensive verification.

Future development should shift from cumulative historical verification growth toward a stable canonical regression architecture.

The main goal is:

> Preserve scientific and computational correctness while reducing permanent maintenance of development-history machinery.

Phase 3 historical evidence remains valuable and must remain auditable.

It does not need to remain part of every future execution path.

## 1. Preserve the Scientific Core

The following remain first-class verification targets.

### Measurement semantics

Preserve exact behavior for:

- structural classes;
- support;
- SCI and related diversity measures;
- comparison profiles;
- longitudinal profiles;
- observed versus expressible versus latent support distinctions;
- fixed denominator semantics;
- missing and unavailable states.

### Longitudinal behavior

Preserve:

- trajectory calculations;
- matched and descriptive comparisons;
- finite-family support assays;
- empirical/local structural half-life;
- conditional recovery;
- revision and recut invalidation;
- panel/root identity;
- clock/window semantics.

### Replay

Replay must continue to verify:

- input identity;
- method identity;
- software identity;
- registered unit order;
- stored draw/index identity;
- context compatibility.

Corrupt or absent replay information must not silently trigger a fresh run.

### Evidence limits

Software outputs must continue to distinguish:

- fixture correctness;
- software verification;
- empirical evidence;
- independent validation;
- unavailable scientific conclusions.

A passing fixture must never become an empirical claim.

## 2. Stop Cumulative Historical Expansion

Do not carry every Phase 1, Phase 2, and Phase 3 development mechanism into all future active suites.

Historical records should remain in:

- Git history;
- completion documents;
- archived verification packages;
- release notes;
- retained execution receipts.

Future tests should target current supported behavior.

If an old test protects a still-relevant behavior, migrate that behavior into the canonical suite.

Do not preserve old wrappers, historical runner architecture, or administrative identities solely because they existed in earlier phases.

## 3. Establish Three Permanent Verification Suites

### A. Canonical Regression Suite

Runs frequently.

Contains:

- current M behavior;
- current V behavior;
- current L behavior;
- schemas;
- numerical oracles;
- replay;
- report semantics;
- critical malformed-input cases.

This becomes the primary development suite.

### B. Release Qualification Suite

Runs for release candidates and high-impact changes.

Contains:

- clean source execution;
- clean extracted archive execution;
- package/build verification where applicable;
- canonical examples;
- reproducibility checks;
- environment identity;
- publication safety;
- no-overwrite output behavior;
- release artifact integrity.

### C. Historical Evidence Archive

Does not run as a normal regression suite.

Contains:

- old phase journals;
- exact historical test identities;
- superseded matrices;
- migration records;
- failed attempts;
- prior delivery receipts;
- original phase-completion evidence.

Historical auditability is preserved without forcing historical development machinery into every future run.

## 4. Risk-Based Test Selection

### Small implementation change

Run:

- directly affected tests;
- mathematical oracle tests for the affected method;
- relevant integration neighbors.

### Measurement-definition or numerical-kernel change

Run:

- all related numerical tests;
- relevant M/V/L integration;
- sensitivity/replay cases;
- canonical regression suite if semantics are shared.

### Schema or report change

Run:

- schema tests;
- JSON/Markdown parity where applicable;
- report-boundary tests;
- affected replay tests;
- relevant full regression.

### Packaging or release change

Run release qualification.

### Documentation-only change

Do not run the full scientific suite unless the document is executable authority.

## 5. Test Quality Over Test Count

Do not optimize for increasing the number of unique test methods.

Prefer tests that detect distinct failure modes.

Introduce bounded mutation testing around high-value logic such as:

- threshold inclusivity;
- denominator selection;
- diversity formulas;
- recovery qualification;
- missing/unavailable distinction;
- replay fallback prevention;
- revision invalidation;
- categorical support logic.

Examples of meaningful mutations:

- `<` to `<=`;
- incorrect zero handling;
- swapped numerator/denominator;
- dropped missing-state branch;
- accidental replay resampling;
- failure to invalidate dependent results after recut.

Use mutation results to identify redundant tests.

## 6. Phase 4 and Later Work

Future phases should add verification primarily for genuinely new capabilities.

Do not automatically recreate:

- a new phase-specific historical runner;
- a new layer of approval hashes;
- a new permanent identity-preservation mechanism;
- a new execution-evidence hierarchy;

unless a new failure mode specifically requires it.

Reuse the canonical regression and release architecture.

New capabilities should plug into the existing structure.

## 7. Practical Simplicity Requirement

The internal verification system may remain rigorous.

The external user experience must become simpler as the project matures.

A normal user should eventually be able to understand:

1. what input is required;
2. which command to run;
3. what output means;
4. what conclusions are supported;
5. what conclusions remain unsupported.

Internal auditability should remain available for experts without forcing ordinary users to understand development-phase governance.

## 8. Long-Term Target

StructDet-Bench should evolve from:

> highly verified development-phase research software

toward:

> stable reference research software with strong canonical tests and archived development evidence.

The desired long-term balance is:

- strong scientific correctness;
- strong reproducibility;
- strong replay;
- clear evidence boundaries;
- moderate release verification;
- minimal permanent meta-governance.

Do not remove a control merely because it is expensive.

First determine whether it protects a unique scientific, computational, security, or release failure.

If it does, preserve it.

If it only preserves historical development structure already recoverable elsewhere, consolidate or archive it.

## Step 3 Adoption Checkpoint

### Implementation status at adoption

At the Step 3 adoption checkpoint, policy adoption was complete and the three-suite migration was pending implementation. The delivered Step 3 runner discovered the existing full test tree and checks cumulative predecessor identities. Policy adoption alone created no new runner, changed no test or numerical oracle, and claimed no completed mutation campaign. The subsequent implemented architecture is documented in `VERIFICATION.md`; this checkpoint remains a historical description.

The completed Step 3 source and its accepted execution records remain the migration baseline. Its 2,073 methods and earlier 1,817, 1,866, and 1,992 method sets are historical facts, not minimum test-count targets for future releases. Existing delivery archives remain unchanged.

### Precedence over the earlier Phase 4 plan

| Existing obligation | Application under this policy |
|---|---|
| Sections 7, 8, 9.2, and 12.1 require every predecessor method identity to remain present and pass; P4-W02 enforces historical inheritance. | Preserve each distinct supported behavior with canonical tests. Historical method names and phase membership may be retired after coverage is migrated and the original evidence remains auditable. |
| The Phase 4 runner re-evaluates older phase gates and carries cumulative predecessor annotations. | Consolidate current behavioral checks into the canonical and release suites. Preserve historical gate outcomes in the archive. |
| Step 1 source reconciliation and successive phase-specific identity pins recur in later execution paths. | Retain the original reconciliation as historical evidence. Continue current input, method, software, replay, and release identity checks where they protect the actual operation. |
| Each step carries extensive source inventories, journals, and delivery proofs. | Select verification by the actual change and release risk. Retain useful results and failures without automatically adding another permanent layer. |
| Current/full software status, empirical qualification, and actual delivery are reported separately. | Preserve these distinctions. Simplifying the runner must not promote incomplete software, fixture evidence, or an unpublished artifact. |

### Bounded migration procedure

1. Identify the supported behavior or distinct failure protected by each affected control. Use one concise behavior-to-suite mapping in ordinary project documentation; do not create another recursive approval or evidence system.
2. Move or adapt meaningful scientific, schema, replay, report, and input-boundary tests into the canonical suite. Select controls by what they protect, including those currently housed in phase-named files.
3. Place release environment, extraction, build, publication, and artifact checks in release qualification. A control that also protects routine behavior may retain a small canonical test for that distinct risk.
4. Remove historical-only wrappers and identities from normal discovery after their still-relevant coverage has been preserved. Keep authentic prior journals, failures, matrices, and receipts in the historical archive.
5. Use bounded mutations to assess selected high-value logic. Record whether each mutation was detected; examine surviving mutations and coverage before treating tests as redundant. Do not alter authoritative scientific expected values to make a migration pass.
6. Verify the changed test-selection architecture and preserved behavioral coverage before making it the default. Run release qualification when the work produces a release candidate or changes release behavior. Subsequent small changes use the risk-based selection above.

A lower test count or fewer historical artifacts in an active execution path is acceptable when distinct supported behavior remains covered and historical evidence remains retrievable. Migration does not require a new numbered phase. Phase 4 Step 4 capability work and external publication have not started through this policy adoption.
