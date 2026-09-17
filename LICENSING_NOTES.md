# Licensing Notes

StructDet-Bench uses a mixed-license repository structure so that software can be reused under a conventional open-source license while specifications and benchmark documentation can be reused with attribution.

## Asset classes

| Asset class | License |
|---|---|
| Python source code, test code, tooling, package/configuration files | Apache License 2.0 |
| Root specifications and benchmark documentation | Creative Commons Attribution 4.0 International (CC BY 4.0) |
| Repository-created example/fixture data and generated reference reports, unless marked otherwise | CC BY 4.0 |
| Theory publications | Retain the license stated in each publication |
| Third-party material | Retains its original license |

The root `LICENSE` contains the Apache License 2.0 and governs the software asset class. It does not relicense specification documents, theory publications, or third-party material.

## Specifications and documentation

The following project-authored specification files are released under CC BY 4.0 unless a file explicitly states otherwise:

- `PHASE_0_PLAN.md`
- `PROJECT_SCOPE.md`
- `DEFINITIONS_AND_UNITS.md`
- `STRUCTURAL_CLASS_CONTRACT.md`
- `METRICS_SPEC.md`
- `EVALUATION_INTEGRITY.md`
- `HERO_BENCHMARK_SPEC.md`
- `THEORY_TO_CODE_TRACEABILITY.md`
- `VALIDATION_AND_FALSIFICATION.md`
- `UNRESOLVED_DECISIONS.md`
- `PHASE_0_APPROVAL.md`
- `PHASE_1_PLAN.md`
- general explanatory documentation derived from those specifications

CC BY 4.0 reuse should provide attribution, identify the source, link or name the license where practical, and indicate modifications.

## Software

The following are Apache-2.0 software assets unless explicitly marked otherwise:

- `structdet_bench/**/*.py`
- `tests/**/*.py`
- `tools/**/*.py`
- `pyproject.toml`
- `.gitignore`
- future CI/workflow configuration

## Test and benchmark material

Code-like tests are Apache-2.0. Repository-created data fixtures, benchmark examples, and reference outputs are CC BY 4.0 unless a fixture explicitly declares another license.

## Theory publications

The two theory sources used by the current baseline are citation/reference works rather than software assets:

- *The Structural Determinacy of LLM Generation: Active Structure, Convergence Frontiers, and the Misreading of Randomness*
- *Structural Inbreeding in Synthetic Data: How Linguistic Abundance Conceals the Collapse of Generative Support*

The source PDFs state Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0). They are not included in this repository. Their absence prevents the public software repository from accidentally presenting the publications as Apache-2.0 assets or modified derivatives.

## Contributions

A contribution is distributed under the license applicable to the target asset class. Contributors should submit only material they have the right to contribute and should not include private, restricted, or uncleared datasets.

## No legal-advice claim

This file documents the project's intended license boundaries. It is not legal advice.
