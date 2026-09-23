# StructDet-Bench offline measurement report

**Scope: supplied records only. Independent scientific validation is not performed by this tool.**

| Field | Value |
|---|---|
| <code>&quot;bundle_id&quot;</code> | <code>&quot;CATEGORICAL-NULL-01&quot;</code> |
| <code>&quot;capabilities&quot;</code> | <code>{&quot;empirical_validation&quot;:&quot;not_performed&quot;,&quot;longitudinal&quot;:&quot;implemented_optional&quot;}</code> |
| <code>&quot;implementation_sha256&quot;</code> | <code>&quot;2ff499326eb52f694063f2558d9fb5f69214d7d55e09dfbe70d8de5d96e123eb&quot;</code> |
| <code>&quot;input_context_sha256&quot;</code> | <code>&quot;674a99e7fea293439936c1475dc73054e338775a14fc76c5d601cab27b7aa68b&quot;</code> |
| <code>&quot;input_fingerprint&quot;</code> | <code>&quot;000cef7a0439cc1e604a980afc62a783adbd946d40e67c69c9672f8e20ce9780&quot;</code> |
| <code>&quot;input_schema_version&quot;</code> | <code>&quot;0.1&quot;</code> |
| <code>&quot;report_profile&quot;</code> | <code>&quot;structdet_longitudinal_v1&quot;</code> |
| <code>&quot;report_schema_version&quot;</code> | <code>&quot;0.3&quot;</code> |
| <code>&quot;run_id&quot;</code> | <code>&quot;run-d17d8e2116fc8d95a3a67e6eff06f5570d7ecbf0&quot;</code> |
| <code>&quot;software_version&quot;</code> | <code>&quot;0.1.0.dev0&quot;</code> |
| <code>&quot;study_id&quot;</code> | <code>&quot;categorical-null-math-only&quot;</code> |

## 1. Scope, source/method identities, requested quantities and evidence limitations

### scope

| Field | Value |
|---|---|
| <code>&quot;data_role&quot;</code> | <code>&quot;fixture&quot;</code> |
| <code>&quot;evidence_status&quot;</code> | <code>&quot;supplied_record_checks_only&quot;</code> |
| <code>&quot;independent_validation_performed&quot;</code> | <code>false</code> |
| <code>&quot;permitted_claim_scope&quot;</code> | <code>&quot;fixture_only&quot;</code> |
| <code>&quot;phase3_complete&quot;</code> | <code>false</code> |
| <code>&quot;ud_006&quot;</code> | <code>&quot;actual_independent_evidence_outstanding&quot;</code> |

### ec 001 sha256

<code>&quot;31d2387ff2867e67e07adf60bca723b6783d0c3155b905d5477d2f844e1d9ce8&quot;</code>

### effective limits

| Field | Value |
|---|---|
| <code>&quot;max_categorical_classes&quot;</code> | <code>128</code> |
| <code>&quot;max_exact_bits&quot;</code> | <code>262144</code> |
| <code>&quot;max_forecast_steps&quot;</code> | <code>10000</code> |
| <code>&quot;max_interventions_per_assay&quot;</code> | <code>16</code> |
| <code>&quot;max_link_objects&quot;</code> | <code>100000</code> |
| <code>&quot;max_measurements&quot;</code> | <code>16384</code> |
| <code>&quot;max_panels_per_trajectory&quot;</code> | <code>64</code> |
| <code>&quot;max_states&quot;</code> | <code>256</code> |
| <code>&quot;max_tail_summands&quot;</code> | <code>2000000</code> |
| <code>&quot;max_trajectories&quot;</code> | <code>64</code> |
| <code>&quot;max_transitions&quot;</code> | <code>1024</code> |
| <code>&quot;max_trials_per_cell&quot;</code> | <code>2048</code> |
| <code>&quot;sensitivity_replicates&quot;</code> | <code>2000</code> |

### frozen baseline

| Field | Value |
|---|---|
| <code>&quot;approved_phase3_plan_sha256&quot;</code> | <code>&quot;1ca74fbba06bea44f2b656b3f4e6b46b0c6747cf13640c3f1ea29c69ef3d6352&quot;</code> |
| <code>&quot;archive_sha256&quot;</code> | <code>&quot;b25d9f63f81bc70b265d2e82182f1e4800a0ae500abe29d1e36d642c6f1e5ab0&quot;</code> |
| <code>&quot;commit_sha&quot;</code> | <code>&quot;e56d83d0a47fdfea7e1d4707c7d20e3acdfa25ea&quot;</code> |
| <code>&quot;file_count&quot;</code> | <code>153</code> |
| <code>&quot;git_tree_sha&quot;</code> | <code>&quot;6e7a371b10ce7e9922485482bcf88b3c8b031416&quot;</code> |
| <code>&quot;phase&quot;</code> | <code>3</code> |
| <code>&quot;scope&quot;</code> | <code>&quot;historical_frozen_delivery_not_current_repository_assertion&quot;</code> |
| <code>&quot;step&quot;</code> | <code>7</code> |

### input refs

| <code>&quot;input_id&quot;</code> | <code>&quot;locator_sha256&quot;</code> | <code>&quot;sha256&quot;</code> | <code>&quot;size_bytes&quot;</code> |
| --- | --- | --- | --- |
| <code>&quot;input-0001&quot;</code> | <code>&quot;95ccd009073a7b7414196129d5a54770d71b8dbf31cdba7c943c83fbdfd10a6e&quot;</code> | <code>&quot;ea91b1aea4332654ad9812fc014d033b77fd212583300a77b902482201f01c7f&quot;</code> | <code>7895</code> |

### methods

| Field | Value |
|---|---|
| <code>&quot;categorical_null&quot;</code> | <code>&quot;categorical_null_v1&quot;</code> |
| <code>&quot;half_life&quot;</code> | <code>&quot;anchored_log_decay_v1&quot;</code> |
| <code>&quot;local_half_life&quot;</code> | <code>&quot;endpoint_log_decay_v1&quot;</code> |
| <code>&quot;observed&quot;</code> | <code>&quot;observed_longitudinal_v1&quot;</code> |
| <code>&quot;pipeline&quot;</code> | <code>&quot;longitudinal_pipeline_v1&quot;</code> |
| <code>&quot;records&quot;</code> | <code>&quot;longitudinal_records_v1&quot;</code> |
| <code>&quot;recovery&quot;</code> | <code>&quot;finite_family_evidence_qualified_recovery_v1&quot;</code> |
| <code>&quot;sensitivity&quot;</code> | <code>&quot;longitudinal_trajectory_sensitivity_v1&quot;</code> |
| <code>&quot;support_assay&quot;</code> | <code>&quot;finite_family_binomial_threshold_v1&quot;</code> |

### processing

| Field | Value |
|---|---|
| <code>&quot;contract_failures&quot;</code> | <code>[]</code> |
| <code>&quot;exit_code&quot;</code> | <code>0</code> |
| <code>&quot;input_acquisition_complete&quot;</code> | <code>true</code> |

### quantities not activated

<code>[&quot;latent_support&quot;,&quot;complete_arbitrary_family_expressibility&quot;,&quot;causal_transmission&quot;,&quot;aggregate_inbreeding_score&quot;]</code>

### read limits

| Field | Value |
|---|---|
| <code>&quot;max_bundle_bytes&quot;</code> | <code>67108864</code> |
| <code>&quot;max_depth&quot;</code> | <code>64</code> |
| <code>&quot;max_file_bytes&quot;</code> | <code>16777216</code> |
| <code>&quot;max_line_bytes&quot;</code> | <code>1048576</code> |
| <code>&quot;max_number_chars&quot;</code> | <code>1024</code> |
| <code>&quot;max_records&quot;</code> | <code>100000</code> |

### requested capabilities

<code>[&quot;categorical_null&quot;]</code>

### source pins

| Field | Value |
|---|---|
| <code>&quot;EC&quot;</code> | <code>&quot;002d2393d05cb2c8b1db0a70e844e3d775e2be2155db7b2ffaadaa8080c8b950&quot;</code> |
| <code>&quot;SD&quot;</code> | <code>&quot;357c0c3994e34fc1831ce91bf1c7e579925d64827579f80eb0a8708e85c93f32&quot;</code> |
| <code>&quot;SI&quot;</code> | <code>&quot;80c193231af343d383544cee924a11fbb063a5c4ccee02d996ea4f904979565a&quot;</code> |


## 2. States, stages, lineage/path, clocks, probe/trial inventories, budgets and gaps

### binding review

| Field | Value |
|---|---|
| <code>&quot;bound_cell_ids&quot;</code> | <code>[]</code> |
| <code>&quot;configuration_sha256&quot;</code> | <code>&quot;fbcd80701a9fda5389e393c5b41f560928b81fc0b653135e18ab83d50fe5250a&quot;</code> |
| <code>&quot;input_context_sha256&quot;</code> | <code>&quot;674a99e7fea293439936c1475dc73054e338775a14fc76c5d601cab27b7aa68b&quot;</code> |
| <code>&quot;issues&quot;</code> | <code>[{&quot;code&quot;:&quot;registered_design_unresolved&quot;,&quot;locator_sha256&quot;:&quot;166e4abb580bc4681c0f007a5d3f6d2c3d00276f82a72433def04d65d1f038f2&quot;,&quot;severity&quot;:&quot;unresolved&quot;}]</code> |
| <code>&quot;limits&quot;</code> | <code>{&quot;max_categorical_classes&quot;:128,&quot;max_exact_bits&quot;:262144,&quot;max_forecast_steps&quot;:10000,&quot;max_interventions_per_assay&quot;:16,&quot;max_link_objects&quot;:100000,&quot;max_measurements&quot;:16384,&quot;max_panels_per_trajectory&quot;:64,&quot;max_states&quot;:256,&quot;max_tail_summands&quot;:2000000,&quot;max_trajectories&quot;:64,&quot;max_transitions&quot;:1024,&quot;max_trials_per_cell&quot;:2048,&quot;sensitivity_replicates&quot;:2000}</code> |
| <code>&quot;objects&quot;</code> | <code>[{&quot;declaration&quot;:{&quot;assumptions&quot;:{&quot;closed&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;empirical_reconstruction&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;exogenous_schedule&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;finite_multinomial&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;fixed_classes&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true}},&quot;child_counts&quot;:[[1,1],[2,0],[2,0]],&quot;classes&quot;:[&quot;abstract-a&quot;,&quot;abstract-b&quot;],&quot;evidence&quot;:{&quot;correction&quot;:[],&quot;independence&quot;:[],&quot;origin&quot;:[],&quot;process&quot;:[],&quot;review&quot;:[],&quot;validation&quot;:[]},&quot;n&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:2},&quot;object_id&quot;:&quot;balanced-two&quot;,&quot;object_kind&quot;:&quot;null_scenario&quot;,&quot;object_version&quot;:&quot;0.1&quot;,&quot;p&quot;:[&quot;0.5&quot;,&quot;0.5&quot;],&quot;q&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:[&quot;0.5&quot;,&quot;0.5&quot;]},&quot;schedule&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:null},&quot;steps&quot;:3},&quot;issues&quot;:[],&quot;locator_sha256&quot;:&quot;f52820599197e31a2e8ad8d067b99781c862d3f8e5b61006b8c4f065e0292d97&quot;,&quot;mock_evidence&quot;:false,&quot;ref&quot;:{&quot;object_id&quot;:&quot;balanced-two&quot;,&quot;object_kind&quot;:&quot;null_scenario&quot;,&quot;object_version&quot;:&quot;0.1&quot;},&quot;status&quot;:&quot;record_consistent&quot;,&quot;substantive_validation_performed&quot;:false},{&quot;declaration&quot;:{&quot;assumptions&quot;:{&quot;closed&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:false},&quot;empirical_reconstruction&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;exogenous_schedule&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;finite_multinomial&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;fixed_classes&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true}},&quot;child_counts&quot;:[],&quot;classes&quot;:[&quot;abstract-a&quot;,&quot;abstract-b&quot;],&quot;evidence&quot;:{&quot;correction&quot;:[],&quot;independence&quot;:[],&quot;origin&quot;:[],&quot;process&quot;:[],&quot;review&quot;:[],&quot;validation&quot;:[]},&quot;n&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:2},&quot;object_id&quot;:&quot;open-refusal&quot;,&quot;object_kind&quot;:&quot;null_scenario&quot;,&quot;object_version&quot;:&quot;0.1&quot;,&quot;p&quot;:[&quot;0.5&quot;,&quot;0.5&quot;],&quot;q&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:[&quot;0.5&quot;,&quot;0.5&quot;]},&quot;schedule&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:null},&quot;steps&quot;:3},&quot;issues&quot;:[],&quot;locator_sha256&quot;:&quot;4dd8c57639f01ed66051343575d4bc99900962e312127c4bc591dd8efc505e85&quot;,&quot;mock_evidence&quot;:false,&quot;ref&quot;:{&quot;object_id&quot;:&quot;open-refusal&quot;,&quot;object_kind&quot;:&quot;null_scenario&quot;,&quot;object_version&quot;:&quot;0.1&quot;},&quot;status&quot;:&quot;record_consistent&quot;,&quot;substantive_validation_performed&quot;:false},{&quot;declaration&quot;:{&quot;assumptions&quot;:{&quot;closed&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;empirical_reconstruction&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;exogenous_schedule&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;finite_multinomial&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;fixed_classes&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true}},&quot;child_counts&quot;:[],&quot;classes&quot;:[&quot;abstract-a&quot;,&quot;abstract-b&quot;],&quot;evidence&quot;:{&quot;correction&quot;:[],&quot;independence&quot;:[],&quot;origin&quot;:[],&quot;process&quot;:[],&quot;review&quot;:[],&quot;validation&quot;:[]},&quot;n&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;unknown&quot;},&quot;object_id&quot;:&quot;unknown-n&quot;,&quot;object_kind&quot;:&quot;null_scenario&quot;,&quot;object_version&quot;:&quot;0.1&quot;,&quot;p&quot;:[&quot;0.5&quot;,&quot;0.5&quot;],&quot;q&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:[&quot;0.5&quot;,&quot;0.5&quot;]},&quot;schedule&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:null},&quot;steps&quot;:3},&quot;issues&quot;:[],&quot;locator_sha256&quot;:&quot;72ea96ccdb64b65ca537d559c74e873e6f0be2930cb4ada6edd7c649f61cf62b&quot;,&quot;mock_evidence&quot;:false,&quot;ref&quot;:{&quot;object_id&quot;:&quot;unknown-n&quot;,&quot;object_kind&quot;:&quot;null_scenario&quot;,&quot;object_version&quot;:&quot;0.1&quot;},&quot;status&quot;:&quot;record_consistent&quot;,&quot;substantive_validation_performed&quot;:false}]</code> |
| <code>&quot;requested&quot;</code> | <code>true</code> |
| <code>&quot;statistics_computed&quot;</code> | <code>false</code> |
| <code>&quot;status&quot;</code> | <code>&quot;record_limited&quot;</code> |
| <code>&quot;substantive_validation_performed&quot;</code> | <code>false</code> |
| <code>&quot;work&quot;</code> | <code>{&quot;configuration_nodes&quot;:202,&quot;evidence_dependency_visits&quot;:0,&quot;objects&quot;:3,&quot;registered_states&quot;:0,&quot;registered_transitions&quot;:0}</code> |

### diagnostics

<code>[]</code>

### inventories

<code>[]</code>

### measurements

<code>[]</code>

### panels

<code>[]</code>

### roots

<code>[]</code>

### states

<code>[]</code>

### trajectories

<code>[]</code>

### transitions

<code>[]</code>


## 3. Per-state structural distributions, both views, coverage and protected-tail records

### curves

<code>[]</code>

### measurements

<code>[]</code>

### population unit

<code>&quot;classified_realizations&quot;</code>

### status

<code>&quot;not_requested&quot;</code>

### views

<code>[&quot;classified_all&quot;,&quot;classified_valid&quot;]</code>


## 4. Observed retention/recurrence, stage accounting and separately labeled categorical scenarios

### categorical scenarios

| <code>&quot;binding&quot;</code> | <code>&quot;evidence_status&quot;</code> | <code>&quot;reasons&quot;</code> | <code>&quot;result&quot;</code> | <code>&quot;status&quot;</code> |
| --- | --- | --- | --- | --- |
| <code>{&quot;declaration&quot;:{&quot;assumptions&quot;:{&quot;closed&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;empirical_reconstruction&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;exogenous_schedule&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;finite_multinomial&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;fixed_classes&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true}},&quot;child_counts&quot;:[[1,1],[2,0],[2,0]],&quot;classes&quot;:[&quot;abstract-a&quot;,&quot;abstract-b&quot;],&quot;evidence&quot;:{&quot;correction&quot;:[],&quot;independence&quot;:[],&quot;origin&quot;:[],&quot;process&quot;:[],&quot;review&quot;:[],&quot;validation&quot;:[]},&quot;n&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:2},&quot;object_id&quot;:&quot;balanced-two&quot;,&quot;object_kind&quot;:&quot;null_scenario&quot;,&quot;object_version&quot;:&quot;0.1&quot;,&quot;p&quot;:[&quot;0.5&quot;,&quot;0.5&quot;],&quot;q&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:[&quot;0.5&quot;,&quot;0.5&quot;]},&quot;schedule&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:null},&quot;steps&quot;:3},&quot;issues&quot;:[],&quot;locator_sha256&quot;:&quot;f52820599197e31a2e8ad8d067b99781c862d3f8e5b61006b8c4f065e0292d97&quot;,&quot;mock_evidence&quot;:false,&quot;ref&quot;:{&quot;object_id&quot;:&quot;balanced-two&quot;,&quot;object_kind&quot;:&quot;null_scenario&quot;,&quot;object_version&quot;:&quot;0.1&quot;},&quot;status&quot;:&quot;record_consistent&quot;,&quot;substantive_validation_performed&quot;:false}</code> | <code>&quot;fixture_only&quot;</code> | <code>[]</code> | <code>{&quot;assumption_status&quot;:&quot;satisfied_for_declared_model&quot;,&quot;assumptions&quot;:{&quot;closed&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;empirical_reconstruction&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;exogenous_schedule&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;finite_multinomial&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;fixed_classes&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true}},&quot;child_transitions&quot;:[{&quot;child&quot;:[{&quot;denominator&quot;:2,&quot;numerator&quot;:1},{&quot;denominator&quot;:2,&quot;numerator&quot;:1}],&quot;child_diversity&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;child_diversity&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:2,&quot;numerator&quot;:1}},&quot;child_support&quot;:[&quot;abstract-a&quot;,&quot;abstract-b&quot;],&quot;child_target_error&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;child_target_error&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:1,&quot;numerator&quot;:0}},&quot;expected_child_diversity&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;conditional_expected_child_diversity&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:4,&quot;numerator&quot;:1}},&quot;expected_child_target_error&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;conditional_expected_child_target_error&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:4,&quot;numerator&quot;:1}},&quot;index&quot;:1,&quot;n&quot;:2,&quot;omission_probabilities&quot;:{&quot;abstract-a&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;next_step_omission_probability&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:4,&quot;numerator&quot;:1}},&quot;abstract-b&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;next_step_omission_probability&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:4,&quot;numerator&quot;:1}}},&quot;parent&quot;:[{&quot;denominator&quot;:2,&quot;numerator&quot;:1},{&quot;denominator&quot;:2,&quot;numerator&quot;:1}],&quot;parent_support&quot;:[&quot;abstract-a&quot;,&quot;abstract-b&quot;],&quot;realized_diversity_increased&quot;:false,&quot;reasons&quot;:[],&quot;status&quot;:&quot;consistent_with_null&quot;,&quot;supplied_counts&quot;:[1,1],&quot;support_nonexpanding&quot;:true,&quot;violates_absorption&quot;:[]},{&quot;child&quot;:[{&quot;denominator&quot;:1,&quot;numerator&quot;:1},{&quot;denominator&quot;:1,&quot;numerator&quot;:0}],&quot;child_diversity&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;child_diversity&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:1,&quot;numerator&quot;:0}},&quot;child_support&quot;:[&quot;abstract-a&quot;],&quot;child_target_error&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;child_target_error&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:2,&quot;numerator&quot;:1}},&quot;expected_child_diversity&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;conditional_expected_child_diversity&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:4,&quot;numerator&quot;:1}},&quot;expected_child_target_error&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;conditional_expected_child_target_error&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:4,&quot;numerator&quot;:1}},&quot;index&quot;:2,&quot;n&quot;:2,&quot;omission_probabilities&quot;:{&quot;abstract-a&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;next_step_omission_probability&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:4,&quot;numerator&quot;:1}},&quot;abstract-b&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;next_step_omission_probability&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:4,&quot;numerator&quot;:1}}},&quot;parent&quot;:[{&quot;denominator&quot;:2,&quot;numerator&quot;:1},{&quot;denominator&quot;:2,&quot;numerator&quot;:1}],&quot;parent_support&quot;:[&quot;abstract-a&quot;,&quot;abstract-b&quot;],&quot;realized_diversity_increased&quot;:false,&quot;reasons&quot;:[],&quot;status&quot;:&quot;consistent_with_null&quot;,&quot;supplied_counts&quot;:[2,0],&quot;support_nonexpanding&quot;:true,&quot;violates_absorption&quot;:[]},{&quot;child&quot;:[{&quot;denominator&quot;:1,&quot;numerator&quot;:1},{&quot;denominator&quot;:1,&quot;numerator&quot;:0}],&quot;child_diversity&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;child_diversity&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:1,&quot;numerator&quot;:0}},&quot;child_support&quot;:[&quot;abstract-a&quot;],&quot;child_target_error&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;child_target_error&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:2,&quot;numerator&quot;:1}},&quot;expected_child_diversity&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;conditional_expected_child_diversity&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:1,&quot;numerator&quot;:0}},&quot;expected_child_target_error&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;conditional_expected_child_target_error&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:2,&quot;numerator&quot;:1}},&quot;index&quot;:3,&quot;n&quot;:2,&quot;omission_probabilities&quot;:{&quot;abstract-a&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;next_step_omission_probability&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:1,&quot;numerator&quot;:0}},&quot;abstract-b&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;next_step_omission_probability&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:1,&quot;numerator&quot;:1}}},&quot;parent&quot;:[{&quot;denominator&quot;:1,&quot;numerator&quot;:1},{&quot;denominator&quot;:1,&quot;numerator&quot;:0}],&quot;parent_support&quot;:[&quot;abstract-a&quot;],&quot;realized_diversity_increased&quot;:false,&quot;reasons&quot;:[],&quot;status&quot;:&quot;consistent_with_null&quot;,&quot;supplied_counts&quot;:[2,0],&quot;support_nonexpanding&quot;:true,&quot;violates_absorption&quot;:[]}],&quot;classes&quot;:[&quot;abstract-a&quot;,&quot;abstract-b&quot;],&quot;distribution_scope&quot;:&quot;explicit_finite_categorical_scenario&quot;,&quot;empirical_pipeline_matches_null&quot;:false,&quot;expected_next_diversity&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;conditional_expected_next_diversity&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:4,&quot;numerator&quot;:1}},&quot;expected_next_target_error&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;conditional_expected_next_target_error&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:4,&quot;numerator&quot;:1}},&quot;forecast&quot;:[{&quot;expected_concentration&quot;:{&quot;denominator&quot;:2,&quot;numerator&quot;:1},&quot;expected_diversity&quot;:{&quot;denominator&quot;:2,&quot;numerator&quot;:1},&quot;expected_target_error&quot;:{&quot;denominator&quot;:1,&quot;numerator&quot;:0},&quot;retained_multiplier&quot;:{&quot;denominator&quot;:1,&quot;numerator&quot;:1},&quot;round_index&quot;:0,&quot;transition_n&quot;:null},{&quot;expected_concentration&quot;:{&quot;denominator&quot;:4,&quot;numerator&quot;:3},&quot;expected_diversity&quot;:{&quot;denominator&quot;:4,&quot;numerator&quot;:1},&quot;expected_target_error&quot;:{&quot;denominator&quot;:4,&quot;numerator&quot;:1},&quot;retained_multiplier&quot;:{&quot;denominator&quot;:2,&quot;numerator&quot;:1},&quot;round_index&quot;:1,&quot;transition_n&quot;:2},{&quot;expected_concentration&quot;:{&quot;denominator&quot;:8,&quot;numerator&quot;:7},&quot;expected_diversity&quot;:{&quot;denominator&quot;:8,&quot;numerator&quot;:1},&quot;expected_target_error&quot;:{&quot;denominator&quot;:8,&quot;numerator&quot;:3},&quot;retained_multiplier&quot;:{&quot;denominator&quot;:4,&quot;numerator&quot;:1},&quot;round_index&quot;:2,&quot;transition_n&quot;:2},{&quot;expected_concentration&quot;:{&quot;denominator&quot;:16,&quot;numerator&quot;:15},&quot;expected_diversity&quot;:{&quot;denominator&quot;:16,&quot;numerator&quot;:1},&quot;expected_target_error&quot;:{&quot;denominator&quot;:16,&quot;numerator&quot;:7},&quot;retained_multiplier&quot;:{&quot;denominator&quot;:8,&quot;numerator&quot;:1},&quot;round_index&quot;:3,&quot;transition_n&quot;:2}],&quot;forecast_reasons&quot;:[],&quot;forecast_status&quot;:&quot;available&quot;,&quot;halving_applicability&quot;:&quot;positive_initial_diversity&quot;,&quot;limits&quot;:{&quot;max_categorical_classes&quot;:128,&quot;max_exact_bits&quot;:262144,&quot;max_forecast_steps&quot;:10000,&quot;max_interventions_per_assay&quot;:16,&quot;max_link_objects&quot;:100000,&quot;max_measurements&quot;:16384,&quot;max_panels_per_trajectory&quot;:64,&quot;max_states&quot;:256,&quot;max_tail_summands&quot;:2000000,&quot;max_trajectories&quot;:64,&quot;max_transitions&quot;:1024,&quot;max_trials_per_cell&quot;:2048,&quot;sensitivity_replicates&quot;:2000},&quot;method&quot;:&quot;categorical_null_v1&quot;,&quot;mode&quot;:&quot;fixed_n&quot;,&quot;n&quot;:2,&quot;null_first_expected_half_crossing&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;null_first_expected_half_crossing&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;categorical_recursive_rounds&quot;,&quot;value&quot;:1},&quot;omission_probabilities&quot;:{&quot;abstract-a&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;next_step_omission_probability&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:4,&quot;numerator&quot;:1}},&quot;abstract-b&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;next_step_omission_probability&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:4,&quot;numerator&quot;:1}}},&quot;parent&quot;:[{&quot;denominator&quot;:2,&quot;numerator&quot;:1},{&quot;denominator&quot;:2,&quot;numerator&quot;:1}],&quot;parent_concentration&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;structural_concentration_index&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:2,&quot;numerator&quot;:1}},&quot;parent_diversity&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;gini_simpson_diversity&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:2,&quot;numerator&quot;:1}},&quot;positive_support&quot;:[&quot;abstract-a&quot;,&quot;abstract-b&quot;],&quot;reasons&quot;:[],&quot;requested_steps&quot;:3,&quot;scenario_id&quot;:&quot;balanced-two&quot;,&quot;schedule&quot;:null,&quot;simulated_draws&quot;:0,&quot;source_pins&quot;:{&quot;EC&quot;:&quot;002d2393d05cb2c8b1db0a70e844e3d775e2be2155db7b2ffaadaa8080c8b950&quot;,&quot;SD&quot;:&quot;357c0c3994e34fc1831ce91bf1c7e579925d64827579f80eb0a8708e85c93f32&quot;,&quot;SI&quot;:&quot;80c193231af343d383544cee924a11fbb063a5c4ccee02d996ea4f904979565a&quot;},&quot;status&quot;:&quot;available&quot;,&quot;structural_half_life_null&quot;:{&quot;evaluation&quot;:&quot;binary64_log1p&quot;,&quot;name&quot;:&quot;structural_half_life_null&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;categorical_recursive_rounds&quot;,&quot;value&quot;:1.0},&quot;substantive_validation_performed&quot;:false,&quot;target&quot;:[{&quot;denominator&quot;:2,&quot;numerator&quot;:1},{&quot;denominator&quot;:2,&quot;numerator&quot;:1}],&quot;target_error&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;squared_target_error&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:1,&quot;numerator&quot;:0}},&quot;target_status&quot;:&quot;available&quot;}</code> | <code>&quot;available&quot;</code> |
| <code>{&quot;declaration&quot;:{&quot;assumptions&quot;:{&quot;closed&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:false},&quot;empirical_reconstruction&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;exogenous_schedule&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;finite_multinomial&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;fixed_classes&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true}},&quot;child_counts&quot;:[],&quot;classes&quot;:[&quot;abstract-a&quot;,&quot;abstract-b&quot;],&quot;evidence&quot;:{&quot;correction&quot;:[],&quot;independence&quot;:[],&quot;origin&quot;:[],&quot;process&quot;:[],&quot;review&quot;:[],&quot;validation&quot;:[]},&quot;n&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:2},&quot;object_id&quot;:&quot;open-refusal&quot;,&quot;object_kind&quot;:&quot;null_scenario&quot;,&quot;object_version&quot;:&quot;0.1&quot;,&quot;p&quot;:[&quot;0.5&quot;,&quot;0.5&quot;],&quot;q&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:[&quot;0.5&quot;,&quot;0.5&quot;]},&quot;schedule&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:null},&quot;steps&quot;:3},&quot;issues&quot;:[],&quot;locator_sha256&quot;:&quot;4dd8c57639f01ed66051343575d4bc99900962e312127c4bc591dd8efc505e85&quot;,&quot;mock_evidence&quot;:false,&quot;ref&quot;:{&quot;object_id&quot;:&quot;open-refusal&quot;,&quot;object_kind&quot;:&quot;null_scenario&quot;,&quot;object_version&quot;:&quot;0.1&quot;},&quot;status&quot;:&quot;record_consistent&quot;,&quot;substantive_validation_performed&quot;:false}</code> | <code>&quot;fixture_only&quot;</code> | <code>[]</code> | <code>{&quot;assumption_status&quot;:&quot;unavailable&quot;,&quot;assumptions&quot;:{&quot;closed&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:false},&quot;empirical_reconstruction&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;exogenous_schedule&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;finite_multinomial&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;fixed_classes&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true}},&quot;child_transitions&quot;:[],&quot;classes&quot;:[&quot;abstract-a&quot;,&quot;abstract-b&quot;],&quot;distribution_scope&quot;:&quot;explicit_finite_categorical_scenario&quot;,&quot;empirical_pipeline_matches_null&quot;:false,&quot;expected_next_diversity&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;conditional_expected_next_diversity&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[&quot;null_conditions_or_first_n_unavailable&quot;],&quot;status&quot;:&quot;unavailable&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:null},&quot;expected_next_target_error&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;conditional_expected_next_target_error&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[&quot;null_conditions_or_target_unavailable&quot;],&quot;status&quot;:&quot;unavailable&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:null},&quot;forecast&quot;:[],&quot;forecast_reasons&quot;:[&quot;closed_not_satisfied&quot;],&quot;forecast_status&quot;:&quot;unavailable&quot;,&quot;halving_applicability&quot;:&quot;unavailable&quot;,&quot;limits&quot;:{&quot;max_categorical_classes&quot;:128,&quot;max_exact_bits&quot;:262144,&quot;max_forecast_steps&quot;:10000,&quot;max_interventions_per_assay&quot;:16,&quot;max_link_objects&quot;:100000,&quot;max_measurements&quot;:16384,&quot;max_panels_per_trajectory&quot;:64,&quot;max_states&quot;:256,&quot;max_tail_summands&quot;:2000000,&quot;max_trajectories&quot;:64,&quot;max_transitions&quot;:1024,&quot;max_trials_per_cell&quot;:2048,&quot;sensitivity_replicates&quot;:2000},&quot;method&quot;:&quot;categorical_null_v1&quot;,&quot;mode&quot;:&quot;fixed_n&quot;,&quot;n&quot;:2,&quot;null_first_expected_half_crossing&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;null_first_expected_half_crossing&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[&quot;null_assumptions_unresolved&quot;],&quot;status&quot;:&quot;unavailable&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;categorical_recursive_rounds&quot;,&quot;value&quot;:null},&quot;omission_probabilities&quot;:{&quot;abstract-a&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;next_step_omission_probability&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[&quot;null_conditions_or_first_n_unavailable&quot;],&quot;status&quot;:&quot;unavailable&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:null},&quot;abstract-b&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;next_step_omission_probability&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[&quot;null_conditions_or_first_n_unavailable&quot;],&quot;status&quot;:&quot;unavailable&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:null}},&quot;parent&quot;:[{&quot;denominator&quot;:2,&quot;numerator&quot;:1},{&quot;denominator&quot;:2,&quot;numerator&quot;:1}],&quot;parent_concentration&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;structural_concentration_index&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:2,&quot;numerator&quot;:1}},&quot;parent_diversity&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;gini_simpson_diversity&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:2,&quot;numerator&quot;:1}},&quot;positive_support&quot;:[&quot;abstract-a&quot;,&quot;abstract-b&quot;],&quot;reasons&quot;:[&quot;closed_not_satisfied&quot;,&quot;null_assumptions_unresolved&quot;,&quot;null_conditions_or_first_n_unavailable&quot;,&quot;null_conditions_or_target_unavailable&quot;],&quot;requested_steps&quot;:3,&quot;scenario_id&quot;:&quot;open-refusal&quot;,&quot;schedule&quot;:null,&quot;simulated_draws&quot;:0,&quot;source_pins&quot;:{&quot;EC&quot;:&quot;002d2393d05cb2c8b1db0a70e844e3d775e2be2155db7b2ffaadaa8080c8b950&quot;,&quot;SD&quot;:&quot;357c0c3994e34fc1831ce91bf1c7e579925d64827579f80eb0a8708e85c93f32&quot;,&quot;SI&quot;:&quot;80c193231af343d383544cee924a11fbb063a5c4ccee02d996ea4f904979565a&quot;},&quot;status&quot;:&quot;available_with_limitations&quot;,&quot;structural_half_life_null&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;structural_half_life_null&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[&quot;null_assumptions_unresolved&quot;],&quot;status&quot;:&quot;unavailable&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;categorical_recursive_rounds&quot;,&quot;value&quot;:null},&quot;substantive_validation_performed&quot;:false,&quot;target&quot;:[{&quot;denominator&quot;:2,&quot;numerator&quot;:1},{&quot;denominator&quot;:2,&quot;numerator&quot;:1}],&quot;target_error&quot;:{&quot;evaluation&quot;:&quot;exact_rational&quot;,&quot;name&quot;:&quot;squared_target_error&quot;,&quot;qualifiers&quot;:[],&quot;reasons&quot;:[],&quot;status&quot;:&quot;available&quot;,&quot;uncertainty_status&quot;:&quot;not_estimated&quot;,&quot;unit&quot;:&quot;dimensionless&quot;,&quot;value&quot;:{&quot;denominator&quot;:1,&quot;numerator&quot;:0}},&quot;target_status&quot;:&quot;available&quot;}</code> | <code>&quot;available_with_limitations&quot;</code> |
| <code>{&quot;declaration&quot;:{&quot;assumptions&quot;:{&quot;closed&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;empirical_reconstruction&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;exogenous_schedule&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;finite_multinomial&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true},&quot;fixed_classes&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:true}},&quot;child_counts&quot;:[],&quot;classes&quot;:[&quot;abstract-a&quot;,&quot;abstract-b&quot;],&quot;evidence&quot;:{&quot;correction&quot;:[],&quot;independence&quot;:[],&quot;origin&quot;:[],&quot;process&quot;:[],&quot;review&quot;:[],&quot;validation&quot;:[]},&quot;n&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;unknown&quot;},&quot;object_id&quot;:&quot;unknown-n&quot;,&quot;object_kind&quot;:&quot;null_scenario&quot;,&quot;object_version&quot;:&quot;0.1&quot;,&quot;p&quot;:[&quot;0.5&quot;,&quot;0.5&quot;],&quot;q&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:[&quot;0.5&quot;,&quot;0.5&quot;]},&quot;schedule&quot;:{&quot;evidence_refs&quot;:[],&quot;state&quot;:&quot;known&quot;,&quot;value&quot;:null},&quot;steps&quot;:3},&quot;issues&quot;:[],&quot;locator_sha256&quot;:&quot;72ea96ccdb64b65ca537d559c74e873e6f0be2930cb4ada6edd7c649f61cf62b&quot;,&quot;mock_evidence&quot;:false,&quot;ref&quot;:{&quot;object_id&quot;:&quot;unknown-n&quot;,&quot;object_kind&quot;:&quot;null_scenario&quot;,&quot;object_version&quot;:&quot;0.1&quot;},&quot;status&quot;:&quot;record_consistent&quot;,&quot;substantive_validation_performed&quot;:false}</code> | <code>&quot;declared_only&quot;</code> | <code>[&quot;categorical_sample_size_unknown&quot;]</code> | <code>null</code> | <code>&quot;unavailable&quot;</code> |

### categorical status

<code>&quot;available_with_limitations&quot;</code>

### observed requests

<code>[]</code>

### scenario scope

<code>&quot;explicit_finite_categorical_arithmetic_no_neural_rate_inference&quot;</code>

### stage transitions

<code>[]</code>


## 5. Empirical/local SHL, geometric-fit diagnostics, sensitivity, non-applicability and crossing brackets

### sensitivity

<code>[]</code>

### half life

<code>[]</code>

### half life status

<code>&quot;not_requested&quot;</code>

### sensitivity status

<code>&quot;not_requested&quot;</code>

### uncertainty limit

<code>&quot;Resampling sensitivity is conditional on registered complete units; no population confidence or model training variability is inferred.&quot;</code>


## 6. Finite-family assays, pre/post missing sets, recovery gates, ERR and partial-information states

### scope

<code>&quot;finite_registered_family_and_reference_registry_only&quot;</code>

### assay status

<code>&quot;not_requested&quot;</code>

### assays

<code>[]</code>

### recovery

<code>[]</code>

### recovery status

<code>&quot;not_requested&quot;</code>


## 7. Anomalies, distributional/structural reopening, corrections and affected-result dependencies

### correction impacts

<code>[]</code>

### dependencies

<code>[]</code>

### new recursive rounds created by reclassification

<code>0</code>

### new samples created by reclassification

<code>0</code>

### original anomalies retained

<code>true</code>

### prior results overwritten

<code>false</code>

### revisions

<code>[]</code>


## 8. Five-condition integrity, ten EC disclosures, omitted conditions, currentness and release restrictions

### currentness

| Field | Value |
|---|---|
| <code>&quot;declared_expiry_is_certification&quot;</code> | <code>false</code> |
| <code>&quot;future_evidence_status&quot;</code> | <code>&quot;unknown&quot;</code> |
| <code>&quot;input_context_sha256&quot;</code> | <code>&quot;674a99e7fea293439936c1475dc73054e338775a14fc76c5d601cab27b7aa68b&quot;</code> |

### declared claim records

<code>[]</code>

### ec reporting disclosures

| Field | Value |
|---|---|
| <code>&quot;capability_and_scope&quot;</code> | <code>&quot;section_1&quot;</code> |
| <code>&quot;class_and_tail_outcomes&quot;</code> | <code>&quot;sections_3_4_6&quot;</code> |
| <code>&quot;correction_path&quot;</code> | <code>&quot;new_pinned_input_new_output_directory_prior_results_preserved&quot;</code> |
| <code>&quot;current_until&quot;</code> | <code>{&quot;scoped_declarations&quot;:[],&quot;state&quot;:&quot;unknown&quot;}</code> |
| <code>&quot;evaluator_identity&quot;</code> | <code>&quot;record_ids_only_private_mappings_omitted&quot;</code> |
| <code>&quot;exposure_and_bias_controls&quot;</code> | <code>&quot;sections_6_8_declared_records_only&quot;</code> |
| <code>&quot;horizon_recovery_override&quot;</code> | <code>&quot;declared_horizon_and_qualified_finite_family_recovery_only&quot;</code> |
| <code>&quot;live_field_evidence&quot;</code> | <code>&quot;not_established_by_toolkit&quot;</code> |
| <code>&quot;source_and_transformation_lineage&quot;</code> | <code>&quot;sections_2_7_and_pinned_input&quot;</code> |
| <code>&quot;structural_cut_and_known_omissions&quot;</code> | <code>&quot;sections_1_3_7&quot;</code> |

### five conditions

| <code>&quot;condition&quot;</code> | <code>&quot;declared_assessments&quot;</code> | <code>&quot;outcome&quot;</code> | <code>&quot;reason&quot;</code> |
| --- | --- | --- | --- |
| <code>&quot;structural_validity&quot;</code> | <code>[]</code> | <code>&quot;unresolved&quot;</code> | <code>&quot;no_substantive_independent_validation_performed_by_toolkit&quot;</code> |
| <code>&quot;external_presence&quot;</code> | <code>[]</code> | <code>&quot;unresolved&quot;</code> | <code>&quot;no_substantive_independent_validation_performed_by_toolkit&quot;</code> |
| <code>&quot;source_integrity&quot;</code> | <code>[]</code> | <code>&quot;unresolved&quot;</code> | <code>&quot;no_substantive_independent_validation_performed_by_toolkit&quot;</code> |
| <code>&quot;tail_retention&quot;</code> | <code>[]</code> | <code>&quot;unresolved&quot;</code> | <code>&quot;no_substantive_independent_validation_performed_by_toolkit&quot;</code> |
| <code>&quot;corrective_capacity&quot;</code> | <code>[]</code> | <code>&quot;unresolved&quot;</code> | <code>&quot;no_substantive_independent_validation_performed_by_toolkit&quot;</code> |

### omitted conditions

<code>[&quot;deployment_representativeness&quot;,&quot;all_input_program_correctness&quot;,&quot;long_horizon_behavior&quot;,&quot;causal_attribution_to_recursive_training&quot;,&quot;complete_expressible_or_latent_repertoire&quot;]</code>

### redaction

| Field | Value |
|---|---|
| <code>&quot;limitation&quot;</code> | <code>&quot;Full reproduction requires the retained local evidence; a public report cannot reconstruct withheld material.&quot;</code> |
| <code>&quot;private_identity_mappings&quot;</code> | <code>&quot;omitted&quot;</code> |
| <code>&quot;private_paths&quot;</code> | <code>&quot;hashed&quot;</code> |
| <code>&quot;raw_bodies&quot;</code> | <code>&quot;omitted&quot;</code> |
| <code>&quot;source_bytes_modified&quot;</code> | <code>false</code> |
| <code>&quot;unrestricted_evidence_prose&quot;</code> | <code>&quot;hashed&quot;</code> |

### release restrictions

<code>[&quot;No empirical or deployment certification.&quot;,&quot;No model calls, training or candidate execution.&quot;,&quot;Local software processing and repository publication are separate outcomes.&quot;,&quot;Phase 3 Step 9 final conformance is outside this command.&quot;]</code>

### support checks

<code>[]</code>

### support records

<code>[]</code>

### workflow status

| Field | Value |
|---|---|
| <code>&quot;local_processing_exit_code&quot;</code> | <code>0</code> |
| <code>&quot;local_software_processing&quot;</code> | <code>&quot;success&quot;</code> |
| <code>&quot;owner_acceptance&quot;</code> | <code>&quot;not_assessed_by_command&quot;</code> |
| <code>&quot;repository_delivery&quot;</code> | <code>&quot;not_assessed_by_command&quot;</code> |
