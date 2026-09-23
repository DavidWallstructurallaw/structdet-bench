# Sorting reference and external-validation specifications

Phase 4 Step 3 materializes the adopted HERO design. These files are specifications and trusted integer test descriptions. All 32 actual core artifacts, independent human first passes, descriptor-pair reviews, witness observations, counterfactual executions, containment reviews and oracle reviews remain missing. No candidate program is supplied, constructed, imported or executed here.

The authoritative meanings remain HERO §§4–6 and the five pins: `bounded_integer_sort/0.1`, `sorting_mechanism_family/0.1`, `sorting_mechanism_partition/0.1`, `sorting_reference_eight/0.1`, `bounded_integer_sort_validity_v1`.

| File | Contents |
|---|---|
| `core_catalog.json` | Exactly 32 missing role specifications: two positive variants and one identifiable-defect proposal per family, plus eight boundary/negative roles. |
| `descriptor_reviews.json` | The complete eight constitutive rules, permitted variations and discriminating evidence from HERO §4.2; all 28 unordered descriptor pairs; outstanding same-class and mechanism-changing counterfactual requirements. |
| `witnesses.json` | Exact W-01 through W-04 inputs and intended discrimination. |
| `preservation_quotas.json` | Two positive variants plus a reviewed defect/boundary record per family, version-history protection, and explicit COUNT/RADIX W-03 and whole-key/digit-boundary protection. |
| `sorting_inputs.json` | Ordered canonical array of 8,995 test rows; repeated equal input values remain distinct identities. |
| `sorting_manifest.json` | Fixed suite identity, segment counts, exact input-file identity and path. |
| `readiness_gaps.json` | Missing material, external conduct, review and environment prerequisites. |
| `VALIDATION_RECEIPTS.md` | Strict passive full-log packet format, associations, bounded coverage and outcome rules. |

The A/B implementation contrasts are suggested permitted variations, not prescribed implementations or accepted empirical labels. A catalog role is not an artifact; an artifact is not a validated reference. Every actual artifact requires two distinct human initial records, at least 64 item-level initial records for all 32 artifacts. That does not require 64 different people. Initial disagreement remains separate from adjudicated results, and legitimate unresolved outcomes are retained.

The eight boundary roles follow HERO §6.1 in order: adjacent-swap insertion versus sweep; fresh selection versus maintained heap; positional merge versus pivot partition; whole-key counting advertised as one-pass radix; unregistered general hybrid; eligible gap-scheduled unregistered mechanism; opaque built-in ordering; misleading or unused fragment with an incomplete decisive path. Their titles are not ground-truth assignments.

Reproduce the two deterministic input files from the repository root:

```sh
python3.13 -B -S tools/materialize_sorting_inputs.py --output-dir /absolute/new/output-directory
```

The parent directory must exist. Existing files, directories and symlinks at the output path are rejected. The tool walks parent directories without following symlinks, stages exactly two regular files, and atomically publishes the fresh directory with Linux `renameat2(RENAME_NOREPLACE)`. Missing required primitives fail closed. It does not inspect other output directories, load candidate source, invoke a shell, expand archives or fetch remote content. Temporary naming uses operating-system entropy only to avoid staging collisions; generated integers, file contents and their order use no RNG.

`sorting_inputs.json` has 555,455 bytes. Its SHA-256 is `4b8dce8c2523bc953286bf853a0e17764e8fbaa6c71cc024b4e60d39feb17c11`. The digest is SHA-256 of ASCII-escaped, key-sorted compact JSON of the tests array plus exactly one LF. Counts are 781 V-SMALL, 18 V-SHAPE, 8,192 V-KEY and four V-STAGE. Test IDs and values exactly retain the existing `INPUT_FORMAT.md` §13.1 encoding.

`reference_specifications()` returns fresh copies of the five static JSON specification objects. `inspect_reference_specifications(mapping)` checks that exact specification set. Filling actual reference roles belongs in versioned operational study records under the later applicable authorization, without rewriting these planned specifications to imply completed work.
