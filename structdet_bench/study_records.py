"""Strict passive operational study envelope, version 0.1.

Structural parsing never establishes empirical qualification. No candidate code,
attachment, reviewer text, URL or declared command is executed or imported.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping
from .contracts import (CLASS_IDS, Diagnostic, ExactNumber, InputError, freeze,
                        is_hash, is_id)
from .local_io import ByteSnapshot, LocalReader, ReadLimits, parse_json_bytes, relative_parts

STUDY_SCHEMA_VERSION = "0.1"
HARD_LIMITS = ReadLimits()

COMMON_FIELDS = {'depends_on': {'array': {'reference': ['study_registration',
                                        'activity_readiness',
                                        'core_catalog',
                                        'artifact',
                                        'validation_receipt',
                                        'human_review',
                                        'adjudication',
                                        'collection_ledger',
                                        'extraction',
                                        'audit_selection',
                                        'correction_incident',
                                        'compilation_receipt']}},
 'lineage_refs': {'array': {'reference': ['study_registration',
                                          'activity_readiness',
                                          'core_catalog',
                                          'artifact',
                                          'validation_receipt',
                                          'human_review',
                                          'adjudication',
                                          'collection_ledger',
                                          'extraction',
                                          'audit_selection',
                                          'correction_incident',
                                          'compilation_receipt']}},
 'record_id': 'id',
 'record_type': {'enum': ['study_registration',
                          'activity_readiness',
                          'core_catalog',
                          'artifact',
                          'validation_receipt',
                          'human_review',
                          'adjudication',
                          'collection_ledger',
                          'extraction',
                          'audit_selection',
                          'correction_incident',
                          'compilation_receipt']},
 'record_version': {'literal': '0.1'},
 'revision': 'positive',
 'scope': {'object': {'claim_id': 'id', 'task_id': 'id', 'task_version': 'id'}},
 'study_id': 'id',
 'study_version': 'id',
 'supersedes': {'knowledge': {'reference': ['study_registration',
                                            'activity_readiness',
                                            'core_catalog',
                                            'artifact',
                                            'validation_receipt',
                                            'human_review',
                                            'adjudication',
                                            'collection_ledger',
                                            'extraction',
                                            'audit_selection',
                                            'correction_incident',
                                            'compilation_receipt']}}}

FAMILY_SCHEMAS = {'activity_readiness': {'object': {'activity': {'enum': ['core_construction',
                                                         'external_validation',
                                                         'human_review',
                                                         'pilot_collection',
                                                         'main_collection',
                                                         'analysis',
                                                         'scientific_release']},
                                   'authorization_ref': {'knowledge': {'reference': ['study_registration',
                                                                                     'activity_readiness',
                                                                                     'core_catalog',
                                                                                     'artifact',
                                                                                     'validation_receipt',
                                                                                     'human_review',
                                                                                     'adjudication',
                                                                                     'collection_ledger',
                                                                                     'extraction',
                                                                                     'audit_selection',
                                                                                     'correction_incident',
                                                                                     'compilation_receipt']}},
                                   'outstanding_requirements': {'array': 'id'},
                                   'prerequisites': {'array': {'object': {'basis': {'knowledge': 'text'},
                                                                          'evidence_refs': {'array': {'reference': ['study_registration',
                                                                                                                    'activity_readiness',
                                                                                                                    'core_catalog',
                                                                                                                    'artifact',
                                                                                                                    'validation_receipt',
                                                                                                                    'human_review',
                                                                                                                    'adjudication',
                                                                                                                    'collection_ledger',
                                                                                                                    'extraction',
                                                                                                                    'audit_selection',
                                                                                                                    'correction_incident',
                                                                                                                    'compilation_receipt']}},
                                                                          'mandatory': 'bool',
                                                                          'outcome': {'enum': ['satisfied_for_scope',
                                                                                               'unsatisfied',
                                                                                               'unresolved',
                                                                                               'not_applicable']},
                                                                          'requirement_id': 'id'}}},
                                   'responsible_operator': {'knowledge': 'id'},
                                   'state': {'enum': ['ready',
                                                      'restricted',
                                                      'blocked',
                                                      'not_assessed']}}},
 'adjudication': {'object': {'adjudicator': {'object': {'entity_kind': {'enum': ['human',
                                                                                 'machine',
                                                                                 'unknown']},
                                                        'exposure': {'knowledge': 'text'},
                                                        'machine_assistance': {'knowledge': 'text'},
                                                        'qualifications': {'knowledge': 'text'},
                                                        'relationships': {'knowledge': 'text'},
                                                        'reviewer_id': 'id',
                                                        'roster_packet_id': {'knowledge': 'id'}}},
                             'artifact_ref': {'reference': ['artifact']},
                             'artifact_sha256': 'hash',
                             'basis': {'knowledge': 'text'},
                             'disagreement': 'text',
                             'independence': {'object': {'declared_independent': {'knowledge': 'bool'},
                                                         'evidence_refs': {'array': {'reference': ['study_registration',
                                                                                                   'activity_readiness',
                                                                                                   'core_catalog',
                                                                                                   'artifact',
                                                                                                   'validation_receipt',
                                                                                                   'human_review',
                                                                                                   'adjudication',
                                                                                                   'collection_ledger',
                                                                                                   'extraction',
                                                                                                   'audit_selection',
                                                                                                   'correction_incident',
                                                                                                   'compilation_receipt']}},
                                                         'limitations': {'array': 'text'}}},
                             'initial_review_refs': {'array': {'reference': ['human_review']}},
                             'judgment': {'object': {'assignment_status': {'enum': ['assigned',
                                                                                    'unresolved',
                                                                                    'unclassified']},
                                                     'evidence_refs': {'array': {'reference': ['study_registration',
                                                                                               'activity_readiness',
                                                                                               'core_catalog',
                                                                                               'artifact',
                                                                                               'validation_receipt',
                                                                                               'human_review',
                                                                                               'adjudication',
                                                                                               'collection_ledger',
                                                                                               'extraction',
                                                                                               'audit_selection',
                                                                                               'correction_incident',
                                                                                               'compilation_receipt']}},
                                                     'rationale': {'knowledge': 'text'},
                                                     'structural_class_id': {'knowledge': 'class_id'},
                                                     'validity_status': {'enum': ['valid',
                                                                                  'invalid',
                                                                                  'undetermined',
                                                                                  'not_assessed']}}},
                             'original_submission_packet': {'knowledge': 'id'},
                             'submitted_at': {'knowledge': 'timestamp'},
                             'unresolved_issues': {'array': 'text'}}},
 'artifact': {'object': {'ai_assistance': {'knowledge': 'text'},
                         'artifact_role': {'enum': ['core_positive',
                                                    'core_defect',
                                                    'core_boundary',
                                                    'candidate',
                                                    'raw_response',
                                                    'prompt',
                                                    'source',
                                                    'evidence',
                                                    'review',
                                                    'longitudinal_input',
                                                    'compiled_output']},
                         'content': {'knowledge': {'object': {'packet_id': 'id'}}},
                         'evidence_refs': {'array': {'reference': ['study_registration',
                                                                   'activity_readiness',
                                                                   'core_catalog',
                                                                   'artifact',
                                                                   'validation_receipt',
                                                                   'human_review',
                                                                   'adjudication',
                                                                   'collection_ledger',
                                                                   'extraction',
                                                                   'audit_selection',
                                                                   'correction_incident',
                                                                   'compilation_receipt']}},
                         'exposure': {'knowledge': 'text'},
                         'original_source': {'knowledge': 'text'},
                         'sha256': {'knowledge': 'hash'},
                         'size_bytes': {'knowledge': 'nonnegative'},
                         'transformations': {'array': {'object': {'operation': 'text',
                                                                  'operator': {'knowledge': 'id'},
                                                                  'output_sha256': 'hash',
                                                                  'performed_at': {'knowledge': 'timestamp'},
                                                                  'source_refs': {'array': {'reference': ['artifact']}},
                                                                  'transformation_id': 'id'}}}}},
 'audit_selection': {'object': {'artifact_ref': {'knowledge': {'reference': ['artifact']}},
                                'basis': {'knowledge': 'text'},
                                'distinct_artifact_count': 'nonnegative',
                                'formula_id': {'literal': 'hero_systematic_positions_v1'},
                                'opportunity': {'enum': ['present', 'missing', 'not_assessed']},
                                'position': {'object': {'block_id': {'enum': ['P00',
                                                                              'P01',
                                                                              'P02',
                                                                              'P03',
                                                                              'P04',
                                                                              'P05',
                                                                              'P06']},
                                                        'condition': {'enum': ['A', 'B', 'C']},
                                                        'group_index': 'positive',
                                                        'within_group_index': 'positive'}},
                                'reasons': {'array': {'enum': ['systematic',
                                                               'disagreement',
                                                               'unresolved',
                                                               'new_class',
                                                               'rare_class',
                                                               'invalid',
                                                               'boundary',
                                                               'other_registered']}},
                                'review_refs': {'array': {'reference': ['human_review']}}}},
 'collection_ledger': {'object': {'attempt_id': {'knowledge': 'id'},
                                  'attempt_status': {'enum': ['succeeded',
                                                              'failed',
                                                              'cancelled',
                                                              'not_attempted',
                                                              'unknown']},
                                  'attempted_at': {'knowledge': 'timestamp'},
                                  'authorization_ref': {'knowledge': {'reference': ['study_registration',
                                                                                    'activity_readiness',
                                                                                    'core_catalog',
                                                                                    'artifact',
                                                                                    'validation_receipt',
                                                                                    'human_review',
                                                                                    'adjudication',
                                                                                    'collection_ledger',
                                                                                    'extraction',
                                                                                    'audit_selection',
                                                                                    'correction_incident',
                                                                                    'compilation_receipt']}},
                                  'block_id': {'enum': ['P00',
                                                        'P01',
                                                        'P02',
                                                        'P03',
                                                        'P04',
                                                        'P05',
                                                        'P06']},
                                  'condition': {'enum': ['A', 'B', 'C']},
                                  'controls': {'object': {'cap_semantics': {'knowledge': 'text'},
                                                          'frequency_penalty': {'knowledge': 'exact'},
                                                          'fresh_context': {'knowledge': 'bool'},
                                                          'hidden_controls': {'knowledge': 'text'},
                                                          'output_allowance': {'knowledge': 'nonnegative'},
                                                          'presence_penalty': {'knowledge': 'exact'},
                                                          'seed': {'knowledge': 'integer_or_null'},
                                                          'temperature': {'knowledge': 'exact_nonnegative'},
                                                          'tools_requested': {'knowledge': 'bool'},
                                                          'top_p': {'knowledge': 'probability'},
                                                          'wrapper_knowledge': {'knowledge': 'text'}}},
                                  'deployment': {'object': {'checkpoint_identifier': {'knowledge': 'text'},
                                                            'deployment_identifier': {'knowledge': 'text'},
                                                            'drift': {'knowledge': 'text'},
                                                            'model_family': {'knowledge': 'text'},
                                                            'model_identifier': {'knowledge': 'text'}}},
                                  'group_index': 'positive',
                                  'phase': {'enum': ['pilot', 'main']},
                                  'planned_positions': {'array': 'positive'},
                                  'prompt_ref': {'knowledge': {'reference': ['artifact']}},
                                  'raw_response_ref': {'knowledge': {'reference': ['artifact']}},
                                  'registered_call_order': 'positive',
                                  'request_id': {'knowledge': 'text'},
                                  'retry_evidence_refs': {'array': {'reference': ['study_registration',
                                                                                  'activity_readiness',
                                                                                  'core_catalog',
                                                                                  'artifact',
                                                                                  'validation_receipt',
                                                                                  'human_review',
                                                                                  'adjudication',
                                                                                  'collection_ledger',
                                                                                  'extraction',
                                                                                  'audit_selection',
                                                                                  'correction_incident',
                                                                                  'compilation_receipt']}},
                                  'retry_of': {'knowledge': {'reference': ['collection_ledger']}},
                                  'sent_prompt_sha256': {'knowledge': 'hash'},
                                  'termination_reason': {'knowledge': 'text'},
                                  'usage': {'object': {'compute': {'knowledge': 'text'},
                                                       'currency': {'knowledge': 'text'},
                                                       'hidden_reasoning_tokens': {'knowledge': 'nonnegative'},
                                                       'input_tokens': {'knowledge': 'nonnegative'},
                                                       'monetary_cost': {'knowledge': 'exact_nonnegative'},
                                                       'output_tokens': {'knowledge': 'nonnegative'}}}}},
 'compilation_receipt': {'object': {'analysis_bundle_created': 'bool',
                                    'claim_disposition': {'enum': ['supported_for_scope',
                                                                   'restricted',
                                                                   'withheld']},
                                    'disposition': {'enum': ['eligible', 'withheld', 'readiness_only']},
                                    'evidence_refs': {'array': {'reference': ['study_registration',
                                                                              'activity_readiness',
                                                                              'core_catalog',
                                                                              'artifact',
                                                                              'validation_receipt',
                                                                              'human_review',
                                                                              'adjudication',
                                                                              'collection_ledger',
                                                                              'extraction',
                                                                              'audit_selection',
                                                                              'correction_incident',
                                                                              'compilation_receipt']}},
                                    'id_map': {'array': {'object': {'source_ref': {'reference': ['study_registration',
                                                                                                 'activity_readiness',
                                                                                                 'core_catalog',
                                                                                                 'artifact',
                                                                                                 'validation_receipt',
                                                                                                 'human_review',
                                                                                                 'adjudication',
                                                                                                 'collection_ledger',
                                                                                                 'extraction',
                                                                                                 'audit_selection',
                                                                                                 'correction_incident',
                                                                                                 'compilation_receipt']},
                                                                    'target_record_id': 'id',
                                                                    'target_record_type': {'enum': ['frame',
                                                                                                    'protocol',
                                                                                                    'cell',
                                                                                                    'attempt',
                                                                                                    'realization',
                                                                                                    'assignment',
                                                                                                    'validity',
                                                                                                    'artifact',
                                                                                                    'raw_artifact',
                                                                                                    'reference_registry',
                                                                                                    'evidence',
                                                                                                    'role',
                                                                                                    'lineage',
                                                                                                    'independence_assessment',
                                                                                                    'annotation',
                                                                                                    'adjudication',
                                                                                                    'domain_suite',
                                                                                                    'domain_result',
                                                                                                    'audit',
                                                                                                    'exposure',
                                                                                                    'integrity_assessment',
                                                                                                    'intake',
                                                                                                    'tail',
                                                                                                    'correction',
                                                                                                    'preregistration',
                                                                                                    'budget',
                                                                                                    'sampling_plan',
                                                                                                    'source']}}}},
                                    'input_snapshots': {'array': {'object': {'packet_id': 'id',
                                                                             'sha256': 'hash',
                                                                             'study_version': 'id'}}},
                                    'mapping_errors': {'array': {'object': {'field': 'id',
                                                                            'reason': 'text',
                                                                            'source_ref': {'reference': ['study_registration',
                                                                                                         'activity_readiness',
                                                                                                         'core_catalog',
                                                                                                         'artifact',
                                                                                                         'validation_receipt',
                                                                                                         'human_review',
                                                                                                         'adjudication',
                                                                                                         'collection_ledger',
                                                                                                         'extraction',
                                                                                                         'audit_selection',
                                                                                                         'correction_incident',
                                                                                                         'compilation_receipt']}}}},
                                    'outputs': {'array': {'object': {'path': 'path',
                                                                     'role': {'enum': ['bundle',
                                                                                       'payload',
                                                                                       'readiness',
                                                                                       'provenance',
                                                                                       'manifest',
                                                                                       'report']},
                                                                     'sha256': 'hash',
                                                                     'size_bytes': 'nonnegative'}}},
                                    'target_input_schema_version': {'literal': '0.1'},
                                    'target_profile': {'enum': ['m_only',
                                                                'hero_sort_abc_v1',
                                                                'structdet_longitudinal_v1']},
                                    'unresolved_restrictions': {'array': 'text'}}},
 'core_catalog': {'object': {'ai_assistance': {'knowledge': 'text'},
                             'artifact_ref': {'knowledge': {'reference': ['artifact']}},
                             'desired_contrast': 'text',
                             'evidence_refs': {'array': {'reference': ['study_registration',
                                                                       'activity_readiness',
                                                                       'core_catalog',
                                                                       'artifact',
                                                                       'validation_receipt',
                                                                       'human_review',
                                                                       'adjudication',
                                                                       'collection_ledger',
                                                                       'extraction',
                                                                       'audit_selection',
                                                                       'correction_incident',
                                                                       'compilation_receipt']}},
                             'exposure': {'knowledge': 'text'},
                             'proposed_family': {'knowledge': 'class_id'},
                             'role_id': 'core_role',
                             'role_status': {'enum': ['missing', 'draft', 'supplied', 'reviewed']},
                             'source': {'knowledge': 'text'}}},
 'correction_incident': {'object': {'action': {'knowledge': 'text'},
                                    'action_status': {'enum': ['proposed',
                                                               'performed',
                                                               'rejected',
                                                               'unresolved']},
                                    'affected_refs': {'array': {'reference': ['study_registration',
                                                                              'activity_readiness',
                                                                              'core_catalog',
                                                                              'artifact',
                                                                              'validation_receipt',
                                                                              'human_review',
                                                                              'adjudication',
                                                                              'collection_ledger',
                                                                              'extraction',
                                                                              'audit_selection',
                                                                              'correction_incident',
                                                                              'compilation_receipt']}},
                                    'challenge': 'text',
                                    'evidence_refs': {'array': {'reference': ['study_registration',
                                                                              'activity_readiness',
                                                                              'core_catalog',
                                                                              'artifact',
                                                                              'validation_receipt',
                                                                              'human_review',
                                                                              'adjudication',
                                                                              'collection_ledger',
                                                                              'extraction',
                                                                              'audit_selection',
                                                                              'correction_incident',
                                                                              'compilation_receipt']}},
                                    'kind': {'enum': ['challenge',
                                                      'correction',
                                                      'incident',
                                                      'retraction']},
                                    'performed_at': {'knowledge': 'timestamp'},
                                    'provenance': {'knowledge': 'text'},
                                    'reanalysis_refs': {'array': {'reference': ['compilation_receipt']}},
                                    'replacement_refs': {'array': {'reference': ['study_registration',
                                                                                 'activity_readiness',
                                                                                 'core_catalog',
                                                                                 'artifact',
                                                                                 'validation_receipt',
                                                                                 'human_review',
                                                                                 'adjudication',
                                                                                 'collection_ledger',
                                                                                 'extraction',
                                                                                 'audit_selection',
                                                                                 'correction_incident',
                                                                                 'compilation_receipt']}},
                                    'reviewer_authority': {'knowledge': 'text'},
                                    'rollback_refs': {'array': {'reference': ['study_registration',
                                                                              'activity_readiness',
                                                                              'core_catalog',
                                                                              'artifact',
                                                                              'validation_receipt',
                                                                              'human_review',
                                                                              'adjudication',
                                                                              'collection_ledger',
                                                                              'extraction',
                                                                              'audit_selection',
                                                                              'correction_incident',
                                                                              'compilation_receipt']}}}},
 'extraction': {'object': {'collection_ref': {'reference': ['collection_ledger']},
                           'extras': {'array': {'object': {'byte_range': {'object': {'end': 'nonnegative',
                                                                                     'start': 'nonnegative'}},
                                                           'heading': {'knowledge': 'text'},
                                                           'reason': 'text'}}},
                           'limitations': {'array': 'text'},
                           'positions': {'array': {'object': {'artifact_ref': {'knowledge': {'reference': ['artifact']}},
                                                              'byte_range': {'knowledge': {'object': {'end': 'nonnegative',
                                                                                                      'start': 'nonnegative'}}},
                                                              'completion_status': {'enum': ['complete',
                                                                                             'truncated',
                                                                                             'refused',
                                                                                             'failed',
                                                                                             'unknown']},
                                                              'fence': {'knowledge': 'text'},
                                                              'heading': {'knowledge': 'text'},
                                                              'limitations': {'array': 'text'},
                                                              'selection': {'enum': ['selected',
                                                                                     'missing',
                                                                                     'withheld']},
                                                              'within_group_index': 'positive'}}},
                           'raw_response_ref': {'knowledge': {'reference': ['artifact']}},
                           'raw_response_sha256': {'knowledge': 'hash'},
                           'rule_version': {'literal': 'hero_candidates_v1'}}},
 'human_review': {'object': {'artifact_ref': {'reference': ['artifact']},
                             'artifact_sha256': 'hash',
                             'blinding': {'object': {'limitations': {'array': 'text'},
                                                     'pack_id': {'knowledge': 'id'},
                                                     'withheld_fields': {'array': {'enum': ['model',
                                                                                            'condition',
                                                                                            'proposed_role',
                                                                                            'other_judgments']}}}},
                             'independence': {'object': {'declared_independent': {'knowledge': 'bool'},
                                                         'evidence_refs': {'array': {'reference': ['study_registration',
                                                                                                   'activity_readiness',
                                                                                                   'core_catalog',
                                                                                                   'artifact',
                                                                                                   'validation_receipt',
                                                                                                   'human_review',
                                                                                                   'adjudication',
                                                                                                   'collection_ledger',
                                                                                                   'extraction',
                                                                                                   'audit_selection',
                                                                                                   'correction_incident',
                                                                                                   'compilation_receipt']}},
                                                         'limitations': {'array': 'text'}}},
                             'initial_submission_ref': {'knowledge': {'reference': ['human_review']}},
                             'judgment': {'object': {'assignment_status': {'enum': ['assigned',
                                                                                    'unresolved',
                                                                                    'unclassified']},
                                                     'evidence_refs': {'array': {'reference': ['study_registration',
                                                                                               'activity_readiness',
                                                                                               'core_catalog',
                                                                                               'artifact',
                                                                                               'validation_receipt',
                                                                                               'human_review',
                                                                                               'adjudication',
                                                                                               'collection_ledger',
                                                                                               'extraction',
                                                                                               'audit_selection',
                                                                                               'correction_incident',
                                                                                               'compilation_receipt']}},
                                                     'rationale': {'knowledge': 'text'},
                                                     'structural_class_id': {'knowledge': 'class_id'},
                                                     'validity_status': {'enum': ['valid',
                                                                                  'invalid',
                                                                                  'undetermined',
                                                                                  'not_assessed']}}},
                             'original_submission_packet': {'knowledge': 'id'},
                             'reviewer': {'object': {'entity_kind': {'enum': ['human',
                                                                              'machine',
                                                                              'unknown']},
                                                     'exposure': {'knowledge': 'text'},
                                                     'machine_assistance': {'knowledge': 'text'},
                                                     'qualifications': {'knowledge': 'text'},
                                                     'relationships': {'knowledge': 'text'},
                                                     'reviewer_id': 'id',
                                                     'roster_packet_id': {'knowledge': 'id'}}},
                             'submission_stage': {'enum': ['draft', 'initial', 'revision']},
                             'submitted_at': {'knowledge': 'timestamp'}}},
 'study_registration': {'object': {'claim_scope': 'text',
                                   'currentness': {'object': {'assessed_at': {'knowledge': 'timestamp'},
                                                              'basis': {'knowledge': 'text'},
                                                              'expires_at': {'knowledge': 'timestamp'},
                                                              'state': {'enum': ['current',
                                                                                 'expired',
                                                                                 'unresolved']}}},
                                   'exposure': {'knowledge': 'text'},
                                   'frame_definition': {'object': {'admissible_substitutions': {'knowledge': 'text'},
                                                                   'consequence_horizon': {'knowledge': 'text'},
                                                                   'consequence_signature_spec': {'knowledge': 'text'},
                                                                   'equivalence_rule_ref': {'knowledge': 'text'},
                                                                   'evidence_requirement': {'knowledge': 'text'},
                                                                   'exceptional_case_rules': {'knowledge': 'text'},
                                                                   'load_bearing_invariants': {'array': 'text'},
                                                                   'task_context': {'knowledge': 'text'}}},
                                   'pins': {'object': {'analytic_resolution_id': {'literal': 'sorting_mechanism_family'},
                                                       'analytic_resolution_version': {'literal': '0.1'},
                                                       'reference_registry_id': {'literal': 'sorting_reference_eight'},
                                                       'reference_registry_version': {'literal': '0.1'},
                                                       'structural_schema_id': {'literal': 'sorting_mechanism_partition'},
                                                       'structural_schema_version': {'literal': '0.1'},
                                                       'task_id': {'literal': 'bounded_integer_sort'},
                                                       'task_version': {'literal': '0.1'},
                                                       'validity_rubric_ref': {'literal': 'bounded_integer_sort_validity_v1'}}},
                                   'preregistration': {'object': {'evidence_refs': {'array': {'reference': ['study_registration',
                                                                                                            'activity_readiness',
                                                                                                            'core_catalog',
                                                                                                            'artifact',
                                                                                                            'validation_receipt',
                                                                                                            'human_review',
                                                                                                            'adjudication',
                                                                                                            'collection_ledger',
                                                                                                            'extraction',
                                                                                                            'audit_selection',
                                                                                                            'correction_incident',
                                                                                                            'compilation_receipt']}},
                                                                  'exposure_at_registration': {'knowledge': 'text'},
                                                                  'registered_at': {'knowledge': 'timestamp'},
                                                                  'status': {'enum': ['prospectively_registered',
                                                                                      'retrospective',
                                                                                      'not_registered',
                                                                                      'unknown']}}},
                                   'protocol': {'object': {'budget': {'object': {'currency': {'knowledge': 'text'},
                                                                                 'max_calls': {'knowledge': 'nonnegative'},
                                                                                 'max_output_tokens': {'knowledge': 'nonnegative'},
                                                                                 'max_positions': {'knowledge': 'nonnegative'},
                                                                                 'monetary_ceiling': {'knowledge': 'exact_nonnegative'}}},
                                                           'controls': {'object': {'cap_semantics': {'knowledge': 'text'},
                                                                                   'frequency_penalty': {'knowledge': 'exact'},
                                                                                   'fresh_context': {'knowledge': 'bool'},
                                                                                   'hidden_controls': {'knowledge': 'text'},
                                                                                   'output_allowance': {'knowledge': 'nonnegative'},
                                                                                   'presence_penalty': {'knowledge': 'exact'},
                                                                                   'seed': {'knowledge': 'integer_or_null'},
                                                                                   'temperature': {'knowledge': 'exact_nonnegative'},
                                                                                   'tools_requested': {'knowledge': 'bool'},
                                                                                   'top_p': {'knowledge': 'probability'},
                                                                                   'wrapper_knowledge': {'knowledge': 'text'}}},
                                                           'design': {'enum': ['sorting_abc',
                                                                               'supplied_longitudinal',
                                                                               'descriptive']},
                                                           'legacy_profile_input': {'knowledge': {'object': {
                                                               'artifact_ref': {'reference': ['artifact']},
                                                               'input_schema_version': {'literal': '0.1'},
                                                               'profile': {'enum': ['m_only', 'hero_sort_abc_v1', 'structdet_longitudinal_v1']}}}},
                                                           'longitudinal_input': {'knowledge': {'reference': ['artifact']}},
                                                           'prompt_refs': {'array': {'reference': ['artifact']}},
                                                           'protocol_id': 'id',
                                                           'protocol_version': 'id'}},
                                   'requested_profile': {'enum': ['m_only',
                                                                  'hero_sort_abc_v1',
                                                                  'structdet_longitudinal_v1']},
                                   'source_pins': {'object': {'EC': {'literal': '002d2393d05cb2c8b1db0a70e844e3d775e2be2155db7b2ffaadaa8080c8b950'},
                                                              'SD': {'literal': '357c0c3994e34fc1831ce91bf1c7e579925d64827579f80eb0a8708e85c93f32'},
                                                              'SI': {'literal': '80c193231af343d383544cee924a11fbb063a5c4ccee02d996ea4f904979565a'}}}}},
 'validation_receipt': {'object': {'artifact_ref': {'reference': ['artifact']},
                                   'artifact_sha256': 'hash',
                                   'conformance_review': {'object': {'basis': {'knowledge': 'text'},
                                                                     'evidence_refs': {'array': {'reference': ['study_registration',
                                                                                                               'activity_readiness',
                                                                                                               'core_catalog',
                                                                                                               'artifact',
                                                                                                               'validation_receipt',
                                                                                                               'human_review',
                                                                                                               'adjudication',
                                                                                                               'collection_ledger',
                                                                                                               'extraction',
                                                                                                               'audit_selection',
                                                                                                               'correction_incident',
                                                                                                               'compilation_receipt']}},
                                                                     'outcome': {'enum': ['satisfied_for_scope',
                                                                                          'unsatisfied',
                                                                                          'unresolved',
                                                                                          'not_applicable']},
                                                                     'reviewer_ref': {'knowledge': {'reference': ['human_review']}}}},
                                   'counterexamples': {'array': {'object': {'input_packet_id': 'id',
                                                                            'observation_packet_id': 'id',
                                                                            'test_id': 'id',
                                                                            'violation': 'text'}}},
                                   'coverage': {'object': {'declared_status': {'enum': ['complete',
                                                                                        'partial',
                                                                                        'not_performed']},
                                                           'log_provenance': {'enum': ['locally_verified_content',
                                                                                       'verified_external_receipt',
                                                                                       'unavailable_attachment',
                                                                                       'unchecked']},
                                                           'representation': {'literal': 'ordered_test_ids_v1'},
                                                           'segments': {'array': {'object': {'expected_count': 'nonnegative',
                                                                                             'full_log_packets': {'array': 'id'},
                                                                                             'observed_ids': {'array': 'id'},
                                                                                             'segment_id': 'id'}}}}},
                                   'environment': {'object': {'configuration_sha256': {'knowledge': 'hash'},
                                                              'environment_id': {'knowledge': 'id'},
                                                              'image_sha256': {'knowledge': 'hash'},
                                                              'isolation_review_ref': {'knowledge': {'reference': ['human_review']}}}},
                                   'harness_status': {'enum': ['ok', 'failed', 'not_assessed']},
                                   'limits': {'object': {'cpu_seconds': {'knowledge': 'exact_nonnegative'},
                                                         'elapsed_seconds': {'knowledge': 'exact_nonnegative'},
                                                         'memory_bytes': {'knowledge': 'nonnegative'},
                                                         'output_bytes': {'knowledge': 'nonnegative'}}},
                                   'mechanism_observations': {'array': {'object': {'evidence_packet_id': {'knowledge': 'id'},
                                                                                   'relation': 'text',
                                                                                   'witness_id': 'id'}}},
                                   'oracle': {'object': {'oracle_id': {'knowledge': 'id'},
                                                         'review_ref': {'knowledge': {'reference': ['human_review']}},
                                                         'source_sha256': {'knowledge': 'hash'}}},
                                   'provenance': {'object': {'attestation_ref': {'knowledge': {'reference': ['study_registration',
                                                                                                             'activity_readiness',
                                                                                                             'core_catalog',
                                                                                                             'artifact',
                                                                                                             'validation_receipt',
                                                                                                             'human_review',
                                                                                                             'adjudication',
                                                                                                             'collection_ledger',
                                                                                                             'extraction',
                                                                                                             'audit_selection',
                                                                                                             'correction_incident',
                                                                                                             'compilation_receipt']}},
                                                             'authenticity': {'enum': ['stipulated_fixture',
                                                                                       'unverified',
                                                                                       'externally_attested']},
                                                             'operator': {'knowledge': 'id'},
                                                             'original_receipt_packet': {'knowledge': 'id'},
                                                             'performed_at': {'knowledge': 'timestamp'}}},
                                   'suite': {'object': {'expected_test_count': 'nonnegative',
                                                        'manifest_sha256': 'hash',
                                                        'suite_id': 'id',
                                                        'suite_version': 'id'}},
                                   'termination': {'enum': ['completed',
                                                            'counterexample',
                                                            'resource_exhausted',
                                                            'cancelled',
                                                            'not_started',
                                                            'unknown']},
                                   'trusted_observations': {'array': {'object': {'evidence_packet_id': {'knowledge': 'id'},
                                                                                 'observation': 'text',
                                                                                 'outcome': {'enum': ['pass',
                                                                                                      'violation',
                                                                                                      'undetermined',
                                                                                                      'harness_failure',
                                                                                                      'resource_exhausted']},
                                                                                 'test_id': 'id'}}},
                                   'validity_status': {'enum': ['valid',
                                                                'invalid',
                                                                'undetermined',
                                                                'not_assessed']}}}}

ENVELOPE_SCHEMA = {'object': {'evidence_policy': {'enum': ['fixture_only', 'adjudicated_import']},
            'import_budget': {'object': {'max_packets': 'nonnegative',
                                         'max_total_bytes': 'positive',
                                         'max_total_records': 'positive'}},
            'material_role': {'enum': ['fixture', 'pilot', 'confirmatory', 'descriptive']},
            'packet_inventory': {'array': {'object': {'format': {'enum': ['bytes', 'json', 'jsonl']},
                                                      'location': {'knowledge': {'choice': [{'object': {'kind': {'literal': 'local'},
                                                                                                        'path': 'path'}},
                                                                                            {'object': {'kind': {'literal': 'external'},
                                                                                                        'locator': 'text'}}]}},
                                                      'packet_id': 'id',
                                                      'purpose': {'enum': ['artifact',
                                                                           'evidence',
                                                                           'review',
                                                                           'original_response',
                                                                           'compiled_output',
                                                                           'registration']},
                                                      'record_count': {'knowledge': 'nonnegative'},
                                                      'sha256': {'knowledge': 'hash'},
                                                      'size_bytes': {'knowledge': 'nonnegative'},
                                                      'verification': {'enum': ['unchecked',
                                                                                'locally_verified_content',
                                                                                'verified_external_receipt',
                                                                                'unavailable_attachment']},
                                                      'verification_ref': {'knowledge': {'reference': ['study_registration',
                                                                                                       'activity_readiness',
                                                                                                       'core_catalog',
                                                                                                       'artifact',
                                                                                                       'validation_receipt',
                                                                                                       'human_review',
                                                                                                       'adjudication',
                                                                                                       'collection_ledger',
                                                                                                       'extraction',
                                                                                                       'audit_selection',
                                                                                                       'correction_incident',
                                                                                                       'compilation_receipt']}}}}},
            'prior_study_versions': {'array': 'id'},
            'records': {'array': 'record'},
            'study_id': 'id',
            'study_schema_version': {'literal': '0.1'},
            'study_version': 'id'}}

RECORD_TYPES = frozenset(FAMILY_SCHEMAS)


@dataclass(frozen=True)
class StudyRecord:
    record_type: str
    record_id: str
    record_version: str
    study_version: str
    data: Mapping[str, Any] = field(repr=False)


@dataclass(frozen=True)
class StudyPacket:
    data: Any = field(repr=False)
    records: tuple[StudyRecord, ...] = field(repr=False)
    diagnostics: tuple[Diagnostic, ...]
    substantive_validation_performed: bool = False

    @property
    def has_errors(self) -> bool:
        return any(d.severity == "error" for d in self.diagnostics)

    @property
    def exit_code(self) -> int:
        return 2 if self.has_errors else 0


@dataclass(frozen=True)
class AttachmentInspection:
    packet_id: str
    declared_verification: str
    status: str
    expected_sha256: str | None
    actual_sha256: str | None
    expected_size_bytes: int | None
    actual_size_bytes: int | None
    checked_record_count: int | None


@dataclass(frozen=True)
class LoadedStudy:
    packet: StudyPacket | None = field(repr=False)
    snapshots: Mapping[str, ByteSnapshot] = field(repr=False)
    attachments: tuple[AttachmentInspection, ...]
    diagnostics: tuple[Diagnostic, ...]
    total_read_bytes: int
    acquisition_complete: bool
    substantive_validation_performed: bool = False

    @property
    def has_errors(self) -> bool:
        return any(d.severity == "error" for d in self.diagnostics)

    @property
    def exit_code(self) -> int:
        return 2 if self.has_errors else 0


def _diag(code: str, path: str = "", severity: str = "error") -> Diagnostic:
    # Only schema-owned field names and ordinal indexes reach public diagnostics.
    return Diagnostic(code, "study", "study", path, severity=severity)


def _limits(limits: ReadLimits | None) -> ReadLimits:
    limits = HARD_LIMITS if limits is None else limits
    if not isinstance(limits, ReadLimits):
        raise InputError("unsupported_read_limit")
    if any(type(v) is not int or v < 1 or v > getattr(HARD_LIMITS, k)
           for k, v in vars(limits).items()):
        raise InputError("unsupported_read_limit")
    return limits


def _physical(data: bytes, limits: ReadLimits) -> Any:
    if not isinstance(data, bytes):
        raise InputError("input_not_bytes")
    if len(data) > limits.max_file_bytes:
        raise InputError("file_size_exceeded")
    if any(len(line) > limits.max_line_bytes for line in data.splitlines(keepends=True)):
        raise InputError("line_size_exceeded")
    return parse_json_bytes(data, limits)


def _preflight(raw: Any, limits: ReadLimits) -> None:
    # Iterative enter/leave walk rejects recursive Python objects before freeze.
    active: set[int] = set()
    todo = [(raw, 0, False)]
    total = 0
    while todo:
        value, depth, leave = todo.pop()
        if leave:
            active.remove(id(value))
            continue
        total += 1
        if total > limits.max_file_bytes:
            raise InputError("file_size_exceeded")
        if isinstance(value, Mapping) or isinstance(value, (tuple, list)):
            if depth + 1 > limits.max_depth:
                raise InputError("json_depth_exceeded")
            if id(value) in active:
                raise InputError("invalid_json_value")
            active.add(id(value))
            todo.append((value, depth, True))
            if isinstance(value, Mapping):
                for key in value:
                    if not isinstance(key, str):
                        raise InputError("invalid_json_value")
                    try:
                        key.encode("utf-8")
                    except UnicodeEncodeError as exc:
                        raise InputError("unpaired_unicode_surrogate") from exc
                todo.extend((v, depth + 1, False) for v in reversed(tuple(value.values())))
            else:
                todo.extend((v, depth + 1, False) for v in reversed(value))
        elif isinstance(value, str):
            if len(value) > limits.max_file_bytes:
                raise InputError("file_size_exceeded")
            try:
                value.encode("utf-8")
            except UnicodeEncodeError as exc:
                raise InputError("unpaired_unicode_surrogate") from exc
        elif type(value) is int or isinstance(value, ExactNumber):
            try:
                token = str(value) if type(value) is int else value.token
            except ValueError as exc:
                raise InputError("number_token_too_long") from exc
            if len(token) > limits.max_number_chars:
                raise InputError("number_token_too_long")
        elif value is not None and type(value) is not bool:
            raise InputError("invalid_json_value")


def _number(value: Any, lower: Decimal | None = None,
            upper: Decimal | None = None, positive: bool = False) -> bool:
    if type(value) is int:
        token = str(value)
    elif isinstance(value, ExactNumber):
        token = value.token
    elif isinstance(value, str):
        token = value
    else:
        return False
    if len(token) > HARD_LIMITS.max_number_chars:
        return False
    try:
        # ExactNumber rejects whitespace, Infinity and incidental decimal syntax.
        number = ExactNumber(token).decimal
        # Bound exponent before comparisons; no expansion into a huge integer.
        if abs(number.as_tuple().exponent) > 10000:
            return False
        return ((lower is None or number >= lower) and
                (upper is None or number <= upper) and (not positive or number > 0))
    except (InputError, InvalidOperation, ValueError):
        return False


def _primitive(value: Any, spec: str) -> bool:
    if spec == "text":
        return isinstance(value, str) and bool(value.strip())
    if spec == "id":
        return is_id(value)
    if spec == "hash":
        return is_hash(value)
    if spec == "class_id":
        return value in CLASS_IDS if isinstance(value, str) else False
    if spec == "core_role":
        if not isinstance(value, str):
            return False
        return (value in {f"CORE-{c[5:]}-{v}" for c in CLASS_IDS for v in ("A", "B", "D")}
                or value in {f"CORE-X{i:02}" for i in range(1, 9)})
    if spec == "bool":
        return type(value) is bool
    if spec in {"positive", "nonnegative"}:
        return type(value) is int and value >= (1 if spec == "positive" else 0)
    if spec == "integer_or_null":
        return value is None or type(value) is int
    if spec == "path":
        relative_parts(value)
        return True
    if spec == "timestamp":
        if not isinstance(value, str) or "T" not in value:
            return False
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return dt.tzinfo is not None and dt.utcoffset() is not None
        except (ValueError, OverflowError):
            return False
    if spec.startswith("exact"):
        return _number(value, Decimal(0) if spec == "exact_nonnegative" else None)
    if spec == "probability":
        return _number(value, Decimal(0), Decimal(1), positive=True)
    return False


def _validate(value: Any, spec: Any, path: str, issues: list[Diagnostic]) -> None:
    def bad(code: str) -> None:
        issues.append(_diag(code, path))
    if isinstance(spec, str):
        if spec == "record":
            if not isinstance(value, Mapping):
                bad("invalid_type")
                return
            kind = value.get("record_type")
            if not isinstance(kind, str) or kind not in RECORD_TYPES:
                bad("unsupported_record_type")
                return
            if value.get("record_version") != STUDY_SCHEMA_VERSION:
                bad("unsupported_record_version")
            _validate(value, {"object": {**COMMON_FIELDS, **FAMILY_SCHEMAS[kind]["object"]}}, path, issues)
            return
        try:
            if not _primitive(value, spec):
                bad("invalid_type" if spec in {"positive", "nonnegative", "bool", "text"} else "invalid_value")
        except InputError as exc:
            bad(exc.code)
        return
    if "literal" in spec:
        if type(value) is not type(spec["literal"]) or value != spec["literal"]:
            bad("invalid_value")
    elif "enum" in spec:
        if not isinstance(value, str) or value not in spec["enum"]:
            bad("invalid_value")
    elif "object" in spec:
        if not isinstance(value, Mapping):
            bad("invalid_type")
            return
        fields = spec["object"]
        for key in sorted(set(fields) - set(value)):
            issues.append(_diag("missing_field", path + "." + key))
        if set(value) - set(fields):
            bad("unknown_field")
        for key in fields:
            if key in value:
                _validate(value[key], fields[key], path + "." + key, issues)
    elif "array" in spec:
        if not isinstance(value, (list, tuple)):
            bad("invalid_type")
            return
        for index, item in enumerate(value):
            _validate(item, spec["array"], f"{path}[{index}]", issues)
    elif "knowledge" in spec:
        if not isinstance(value, Mapping):
            bad("invalid_knowledge")
            return
        state = value.get("state")
        if not isinstance(state, str) or state not in {"known", "unknown", "unavailable", "not_applicable"}:
            bad("invalid_knowledge_state")
        elif state == "known":
            if "value" not in value:
                bad("known_value_missing")
            elif set(value) != {"state", "value"}:
                bad("invalid_knowledge")
            else:
                _validate(value["value"], spec["knowledge"], path + ".value", issues)
        else:
            if "value" in value:
                bad("value_in_unknown_state")
            if not isinstance(value.get("reason"), str) or not value["reason"].strip():
                bad("missing_knowledge_reason")
            if set(value) - {"state", "reason"}:
                bad("invalid_knowledge")
    elif "reference" in spec:
        if not isinstance(value, Mapping) or set(value) != {"record_type", "record_id", "record_version"}:
            bad("invalid_reference")
            return
        if not is_id(value["record_id"]):
            bad("invalid_reference")
        if not isinstance(value["record_type"], str) or value["record_type"] not in spec["reference"]:
            bad("reference_type_mismatch")
        if value["record_version"] != STUDY_SCHEMA_VERSION:
            bad("reference_version_mismatch")
    elif "choice" in spec:
        if not isinstance(value, Mapping):
            bad("invalid_type")
            return
        choices = [s for s in spec["choice"] if s["object"]["kind"]["literal"] == value.get("kind")]
        if len(choices) != 1:
            bad("invalid_value")
        else:
            _validate(value, choices[0], path, issues)


def _known(value: Mapping[str, Any]) -> Any:
    return value["value"] if value["state"] == "known" else None


def _references(value: Any, path: str = ""):
    # Shape validation has already rejected unsupported structures.
    todo = [(value, path)]
    while todo:
        node, prefix = todo.pop()
        if isinstance(node, Mapping):
            if set(node) == {"record_type", "record_id", "record_version"}:
                yield prefix, node
            else:
                todo.extend((v, prefix + "." + k) for k, v in reversed(tuple(node.items())))
        elif isinstance(node, (list, tuple)):
            todo.extend((v, f"{prefix}[{i}]") for i, v in reversed(tuple(enumerate(node))))


def _cycle(graph: Mapping[str, tuple[str, ...]]) -> bool:
    degree = {key: 0 for key in graph}
    outgoing: dict[str, list[str]] = {key: [] for key in graph}
    for key, refs in graph.items():
        for target in refs:
            if target in graph:
                degree[key] += 1
                outgoing[target].append(key)
    ready = deque(key for key, n in degree.items() if n == 0)
    seen = 0
    while ready:
        key = ready.popleft()
        seen += 1
        for target in outgoing[key]:
            degree[target] -= 1
            if degree[target] == 0:
                ready.append(target)
    return seen != len(graph)


def _semantic(raw: Mapping[str, Any], limits: ReadLimits, issues: list[Diagnostic]) -> None:
    records, inventory = raw["records"], raw["packet_inventory"]
    def bad(code: str, path: str = "", severity: str = "error") -> None:
        issues.append(_diag(code, path, severity))
    def unique(values: Any, path: str, code: str = "duplicate_value") -> None:
        if len(values) != len(set(values)):
            bad(code, path)
    versions = [raw["study_version"], *raw["prior_study_versions"]]
    unique(versions, "prior_study_versions")
    unique([r["record_id"] for r in records], "records", "duplicate_record_id")
    unique([p["packet_id"] for p in inventory], "packet_inventory", "duplicate_packet_id")
    known_paths = [_known(p["location"])["path"] for p in inventory
                   if _known(p["location"]) and _known(p["location"])["kind"] == "local"]
    unique(known_paths, "packet_inventory", "duplicate_packet_path")
    budget = raw["import_budget"]
    if (budget["max_packets"] > limits.max_records or budget["max_total_bytes"] > limits.max_bundle_bytes
            or budget["max_total_records"] > limits.max_records
            or len(inventory) > budget["max_packets"]
            or len(records) > budget["max_total_records"]
            or sum(_known(p["size_bytes"]) or 0 for p in inventory) > budget["max_total_bytes"]
            or sum(_known(p["record_count"]) or 0 for p in inventory) + len(records) > budget["max_total_records"]):
        bad("budget_exceeded_partition_required", "import_budget")
    if len(records) > limits.max_records:
        bad("record_count_exceeded", "records")
    if raw["material_role"] == "fixture" and raw["evidence_policy"] != "fixture_only":
        bad("fixture_policy_mismatch", "evidence_policy")
    if raw["evidence_policy"] == "fixture_only" and raw["material_role"] != "fixture":
        bad("fixture_policy_mismatch", "material_role")
    by_id = {r["record_id"]: r for r in records}
    by_packet = {p["packet_id"]: p for p in inventory}
    # Known claims bind one artifact identity even when no bytes have yet been
    # acquired. Different artifact IDs remain distinct even with equal hashes.
    claimed_hashes: dict[str, set[str]] = {}
    for record in records:
        reference = digest = None
        if record["record_type"] == "artifact":
            digest = _known(record["sha256"])
            reference = {"record_id": record["record_id"]}
            content = _known(record["content"])
            if content and content["packet_id"] in by_packet:
                packet_hash = _known(by_packet[content["packet_id"]]["sha256"])
                if packet_hash is not None:
                    claimed_hashes.setdefault(record["record_id"], set()).add(packet_hash)
        elif record["record_type"] in {"validation_receipt", "human_review", "adjudication"}:
            reference, digest = record["artifact_ref"], record["artifact_sha256"]
        elif record["record_type"] == "collection_ledger":
            reference, digest = _known(record["prompt_ref"]), _known(record["sent_prompt_sha256"])
        elif record["record_type"] == "extraction":
            reference, digest = _known(record["raw_response_ref"]), _known(record["raw_response_sha256"])
        if reference is not None and digest is not None:
            claimed_hashes.setdefault(reference["record_id"], set()).add(digest)
    if any(len(values) > 1 for values in claimed_hashes.values()):
        bad("artifact_hash_mismatch", "records")
    position_associations: dict[tuple[Any, ...], dict[str, Any]] = {}
    superseded_ids = {_known(r["supersedes"])["record_id"] for r in records if _known(r["supersedes"])}
    for extraction in records:
        if extraction["record_type"] != "extraction" or extraction["record_id"] in superseded_ids:
            continue
        call = by_id.get(extraction["collection_ref"]["record_id"])
        if call is None or call["record_type"] != "collection_ledger":
            continue
        for position in extraction["positions"]:
            key = (extraction["study_version"], call["block_id"], call["condition"], call["group_index"], position["within_group_index"])
            state = position_associations.setdefault(key, {"missing": False, "selected": False, "artifacts": set()})
            state["missing"] |= position["selection"] == "missing"
            state["selected"] |= position["selection"] == "selected"
            if _known(position["artifact_ref"]):
                state["artifacts"].add(_known(position["artifact_ref"])["record_id"])
    registrations = {}
    registration_groups: dict[str, list[Any]] = {}
    for record in records:
        if record["record_type"] == "study_registration":
            registration_groups.setdefault(record["study_version"], []).append(record)
    for version in versions:
        found = registration_groups.get(version, [])
        if len(found) != 1:
            bad("registration_count", "records")
        else:
            registrations[version] = found[0]
    for i, rec in enumerate(records):
        path = f"records[{i}]"
        if rec["study_id"] != raw["study_id"]:
            bad("study_identity_mismatch", path + ".study_id")
        if rec["study_version"] not in versions:
            bad("study_version_mismatch", path + ".study_version")
        reg = registrations.get(rec["study_version"])
        if reg and (rec["scope"] != reg["scope"] or rec["scope"]["task_id"] != reg["pins"]["task_id"]
                    or rec["scope"]["task_version"] != reg["pins"]["task_version"]):
            bad("scope_mismatch", path + ".scope")
        for ref_path, ref in _references(rec):
            target = by_id.get(ref["record_id"])
            if target is None:
                bad("missing_reference", path + ref_path)
                continue
            if target["record_type"] != ref["record_type"]:
                bad("reference_type_mismatch", path + ref_path)
            historical = (ref_path.startswith(".lineage_refs[") or ref_path.startswith(".supersedes.")
                          or rec["record_type"] == "correction_incident" and ref_path.startswith(".affected_refs["))
            if not historical and target["study_version"] != rec["study_version"]:
                bad("study_version_mismatch", path + ref_path)
            if target["scope"] != rec["scope"]:
                bad("scope_mismatch", path + ref_path)
            if ref_path.startswith(".supersedes."):
                if target["record_type"] != rec["record_type"]:
                    bad("supersession_type_mismatch", path + ref_path)
                if target["revision"] >= rec["revision"]:
                    bad("supersession_revision_order", path + ref_path)
        for group in ("depends_on", "lineage_refs"):
            unique([r["record_id"] for r in rec[group]], path + "." + group)
        _record_semantics(rec, reg, by_id, by_packet, position_associations, path, bad)
    for i, packet in enumerate(inventory):
        path = f"packet_inventory[{i}]"
        size = _known(packet["size_bytes"])
        if size is not None and size > limits.max_file_bytes:
            bad("budget_exceeded_partition_required", path + ".size_bytes")
        if packet["format"] == "bytes" and _known(packet["record_count"]) not in (None, 0):
            bad("attachment_record_count_mismatch", path + ".record_count")
        for ref_path, ref in _references(packet):
            target = by_id.get(ref["record_id"])
            if target is None:
                bad("missing_reference", path + ref_path)
            elif target["record_type"] != ref["record_type"]:
                bad("reference_type_mismatch", path + ref_path)
        if packet["verification"] != "unchecked":
            bad("unverified_attachment", path + ".verification", "warning")
    depends = {r["record_id"]: tuple(v["record_id"] for v in r["depends_on"]) for r in records}
    supersedes = {r["record_id"]: ((_known(r["supersedes"])["record_id"],)
                  if _known(r["supersedes"]) else ()) for r in records}
    if _cycle(depends):
        bad("dependency_cycle", "records")
    if _cycle(supersedes):
        bad("supersession_cycle", "records")


def _record_semantics(rec: Mapping[str, Any], reg: Mapping[str, Any] | None,
                      by_id: Mapping[str, Any], packets: Mapping[str, Any],
                      position_associations: Mapping[tuple[Any, ...], Any],
                      path: str, bad: Any) -> None:
    kind = rec["record_type"]
    def packet_ref(pid: str, field: str) -> None:
        if pid not in packets:
            bad("packet_not_declared", path + "." + field)
    def unique(values: Any, field: str, code: str = "duplicate_value") -> None:
        if len(values) != len(set(values)):
            bad(code, path + "." + field)
    def artifact_hash(target: Mapping[str, Any]) -> str | None:
        digest = _known(target["sha256"])
        content = _known(target["content"])
        if digest is None and content and content["packet_id"] in packets:
            digest = _known(packets[content["packet_id"]]["sha256"])
        return digest
    def role_check(reference: Mapping[str, Any] | None, roles: set[str], field: str) -> None:
        target = by_id.get(reference["record_id"]) if reference else None
        if target and target["record_type"] == "artifact" and target["artifact_role"] not in roles:
            bad("reference_type_mismatch", path + "." + field)
    # All packet-ID slots are explicit grammar fields, including nested lists.
    todo = [(rec, "")]
    while todo:
        value, prefix = todo.pop()
        if isinstance(value, Mapping):
            if value.get("outcome") == "not_applicable" and "basis" in value and _known(value["basis"]) is None:
                bad("state_contradiction", path + prefix + ".basis")
            for key, v in value.items():
                field = prefix + "." + key
                if key in {"packet_id", "input_packet_id", "observation_packet_id"}:
                    packet_ref(v, field)
                elif key in {"roster_packet_id", "evidence_packet_id", "original_receipt_packet", "original_submission_packet"}:
                    if _known(v) is not None:
                        packet_ref(_known(v), field)
                elif key == "full_log_packets":
                    unique(v, field)
                    for pid in v:
                        packet_ref(pid, field)
                todo.append((v, field))
        elif isinstance(value, (list, tuple)):
            todo.extend((v, f"{prefix}[{i}]") for i, v in enumerate(value))
    if kind == "study_registration":
        design, profile = rec["protocol"]["design"], rec["requested_profile"]
        supplied = _known(rec["protocol"]["legacy_profile_input"])
        if supplied and supplied["profile"] != profile:
            bad("profile_contradiction", path + ".protocol.legacy_profile_input")
        for reference in rec["protocol"]["prompt_refs"]:
            role_check(reference, {"prompt"}, "protocol.prompt_refs")
        role_check(_known(rec["protocol"]["longitudinal_input"]), {"longitudinal_input", "source"}, "protocol.longitudinal_input")
        if supplied:
            role_check(supplied["artifact_ref"], {"source", "longitudinal_input"}, "protocol.legacy_profile_input")
        if ((profile == "structdet_longitudinal_v1") != (design == "supplied_longitudinal")
                or profile == "hero_sort_abc_v1" and design != "sorting_abc"):
            bad("profile_contradiction", path + ".protocol.design")
        if design != "supplied_longitudinal" and _known(rec["protocol"]["longitudinal_input"]) is not None:
            bad("profile_contradiction", path + ".protocol.longitudinal_input")
    elif kind == "activity_readiness":
        rows = rec["prerequisites"]
        unique([p["requirement_id"] for p in rows], "prerequisites")
        unique(rec["outstanding_requirements"], "outstanding_requirements")
        expected = [p["requirement_id"] for p in rows if p["mandatory"] and p["outcome"] != "satisfied_for_scope"]
        if any(p["mandatory"] and p["outcome"] == "not_applicable" for p in rows):
            bad("state_contradiction", path + ".prerequisites")
        if set(expected) != set(rec["outstanding_requirements"]):
            bad("state_contradiction", path + ".outstanding_requirements")
        if rec["state"] == "ready" and expected:
            bad("state_contradiction", path + ".state")
    elif kind == "core_catalog":
        artifact = _known(rec["artifact_ref"])
        role_check(artifact, {"core_positive", "core_defect", "core_boundary", "source"}, "artifact_ref")
        if (rec["role_status"] == "missing" and artifact is not None
                or rec["role_status"] in {"supplied", "reviewed"} and artifact is None):
            bad("state_contradiction", path + ".role_status")
    elif kind == "artifact":
        content = _known(rec["content"])
        if content and content["packet_id"] in packets:
            packet = packets[content["packet_id"]]
            for field, code in (("sha256", "artifact_hash_mismatch"), ("size_bytes", "attachment_size_mismatch")):
                left, right = _known(rec[field]), _known(packet[field])
                if left is not None and right is not None and left != right:
                    bad(code, path + "." + field)
    elif kind in {"validation_receipt", "human_review", "adjudication"}:
        target = by_id.get(rec["artifact_ref"]["record_id"])
        if target and target["record_type"] == "artifact":
            digest = artifact_hash(target)
            if digest is not None and digest != rec["artifact_sha256"]:
                bad("artifact_hash_mismatch", path + ".artifact_sha256")
        if kind in {"human_review", "adjudication"}:
            judgment = rec["judgment"]
            if ((judgment["assignment_status"] == "assigned") != (_known(judgment["structural_class_id"]) is not None)):
                bad("state_contradiction", path + ".judgment.structural_class_id")
        if kind == "human_review":
            initial = _known(rec["initial_submission_ref"])
            if ((rec["submission_stage"] == "revision") != (initial is not None)):
                bad("state_contradiction", path + ".initial_submission_ref")
            if initial:
                prior = by_id.get(initial["record_id"])
                if prior and prior["record_type"] == "human_review" and (
                        prior["submission_stage"] != "initial" or prior["artifact_ref"] != rec["artifact_ref"]
                        or prior["artifact_sha256"] != rec["artifact_sha256"]
                        or prior["reviewer"]["reviewer_id"] != rec["reviewer"]["reviewer_id"]):
                    bad("state_contradiction", path + ".initial_submission_ref")
        elif kind == "adjudication":
            unique([r["record_id"] for r in rec["initial_review_refs"]], "initial_review_refs")
            for ref in rec["initial_review_refs"]:
                initial = by_id.get(ref["record_id"])
                if initial and initial["record_type"] == "human_review" and (
                        initial["submission_stage"] != "initial" or initial["artifact_ref"] != rec["artifact_ref"]
                        or initial["artifact_sha256"] != rec["artifact_sha256"]):
                    bad("state_contradiction", path + ".initial_review_refs")
        else:
            reviewer = _known(rec["conformance_review"]["reviewer_ref"])
            if reviewer:
                review = by_id.get(reviewer["record_id"])
                if review and review["record_type"] == "human_review" and (
                        review["artifact_ref"] != rec["artifact_ref"] or review["artifact_sha256"] != rec["artifact_sha256"]):
                    bad("state_contradiction", path + ".conformance_review.reviewer_ref")
            coverage = rec["coverage"]
            segments = coverage["segments"]
            unique([s["segment_id"] for s in segments], "coverage.segments")
            ids = [tid for s in segments for tid in s["observed_ids"]]
            unique(ids, "coverage.segments", "coverage_duplicate_test_id")
            if sum(s["expected_count"] for s in segments) != rec["suite"]["expected_test_count"]:
                bad("coverage_count_mismatch", path + ".coverage")
            if any(len(s["observed_ids"]) > s["expected_count"] for s in segments):
                bad("coverage_overflow", path + ".coverage")
            if coverage["declared_status"] == "complete" and any(len(s["observed_ids"]) != s["expected_count"] for s in segments):
                bad("coverage_count_mismatch", path + ".coverage")
            if coverage["declared_status"] == "not_performed" and ids:
                bad("state_contradiction", path + ".coverage")
            if rec["validity_status"] == "valid" and (coverage["declared_status"] != "complete"
                    or rec["termination"] != "completed" or rec["harness_status"] != "ok"
                    or rec["conformance_review"]["outcome"] != "satisfied_for_scope"):
                bad("state_contradiction", path + ".validity_status")
            if rec["validity_status"] == "invalid" and not rec["counterexamples"]:
                bad("state_contradiction", path + ".validity_status")
    elif kind == "collection_ledger":
        role_check(_known(rec["prompt_ref"]), {"prompt"}, "prompt_ref")
        role_check(_known(rec["raw_response_ref"]), {"raw_response"}, "raw_response_ref")
        if ((rec["phase"] == "pilot") != (rec["block_id"] == "P00")
                or rec["group_index"] > (2 if rec["phase"] == "pilot" else 4)
                or tuple(rec["planned_positions"]) != (1, 2, 3, 4, 5)):
            bad("position_contradiction", path)
        if rec["attempt_status"] == "not_attempted" and any(_known(rec[f]) is not None for f in ("attempt_id", "raw_response_ref", "attempted_at")):
            bad("state_contradiction", path + ".attempt_status")
        prompt = _known(rec["prompt_ref"])
        digest = _known(rec["sent_prompt_sha256"])
        target = by_id.get(prompt["record_id"]) if prompt else None
        if target and target["record_type"] == "artifact" and digest and artifact_hash(target) not in (None, digest):
            bad("artifact_hash_mismatch", path + ".sent_prompt_sha256")
    elif kind == "extraction":
        role_check(_known(rec["raw_response_ref"]), {"raw_response"}, "raw_response_ref")
        unique([p["within_group_index"] for p in rec["positions"]], "positions")
        if tuple(p["within_group_index"] for p in rec["positions"]) != (1, 2, 3, 4, 5):
            bad("position_contradiction", path + ".positions")
        target = by_id.get(rec["collection_ref"]["record_id"])
        if target and target["record_type"] == "collection_ledger" and rec["raw_response_ref"] != target["raw_response_ref"]:
            # Unknown reasons do not need identical wording, only known associations.
            if _known(rec["raw_response_ref"]) != _known(target["raw_response_ref"]):
                bad("state_contradiction", path + ".raw_response_ref")
        ref = _known(rec["raw_response_ref"])
        source = by_id.get(ref["record_id"]) if ref else None
        digest = _known(rec["raw_response_sha256"])
        if source and source["record_type"] == "artifact" and digest and artifact_hash(source) not in (None, digest):
            bad("artifact_hash_mismatch", path + ".raw_response_sha256")
        for index, pos in enumerate(rec["positions"]):
            role_check(_known(pos["artifact_ref"]), {"candidate", "source"}, f"positions[{index}].artifact_ref")
            byte_range = _known(pos["byte_range"])
            if pos["selection"] == "selected" and (_known(pos["artifact_ref"]) is None or byte_range is None or ref is None):
                bad("state_contradiction", path + f".positions[{index}]")
            if pos["selection"] == "missing" and (_known(pos["artifact_ref"]) is not None or byte_range is not None):
                bad("state_contradiction", path + f".positions[{index}]")
            if byte_range and (byte_range["end"] < byte_range["start"] or source and source["record_type"] == "artifact"
                    and _known(source["size_bytes"]) is not None and byte_range["end"] > _known(source["size_bytes"])):
                bad("position_contradiction", path + f".positions[{index}].byte_range")
        for extra in rec["extras"]:
            if extra["byte_range"]["end"] < extra["byte_range"]["start"]:
                bad("position_contradiction", path + ".extras")
    elif kind == "audit_selection":
        pos = rec["position"]
        if pos["within_group_index"] > 5 or pos["group_index"] > (2 if pos["block_id"] == "P00" else 4):
            bad("position_contradiction", path + ".position")
        unique(rec["reasons"], "reasons")
        if rec["opportunity"] == "missing" and (_known(rec["artifact_ref"]) is not None or rec["distinct_artifact_count"] != 0):
            bad("state_contradiction", path + ".opportunity")
        if rec["opportunity"] == "present" and (_known(rec["artifact_ref"]) is None or rec["distinct_artifact_count"] != 1):
            bad("state_contradiction", path + ".opportunity")
        audit_artifact = _known(rec["artifact_ref"])
        for reference in rec["review_refs"]:
            review = by_id.get(reference["record_id"])
            if (audit_artifact is not None and review and review["record_type"] == "human_review"
                    and review["artifact_ref"] != audit_artifact):
                bad("state_contradiction", path + ".review_refs")
        # A known extraction for the exact registered position cannot be replaced
        # by another artifact (or turned from missing into present) by an audit row.
        association = position_associations.get((rec["study_version"], pos["block_id"], pos["condition"], pos["group_index"], pos["within_group_index"]))
        if association and ((rec["opportunity"] == "present" and association["missing"])
                or audit_artifact is not None and any(ident != audit_artifact["record_id"] for ident in association["artifacts"])
                or rec["opportunity"] == "missing" and association["selected"]):
            bad("state_contradiction", path + ".position")
    elif kind == "correction_incident":
        if rec["action_status"] == "performed" and (_known(rec["action"]) is None or _known(rec["performed_at"]) is None):
            bad("state_contradiction", path + ".action_status")
        if rec["action_status"] == "proposed" and _known(rec["performed_at"]) is not None:
            bad("state_contradiction", path + ".performed_at")
    elif kind == "compilation_receipt":
        if reg and rec["target_profile"] != reg["requested_profile"]:
            bad("profile_contradiction", path + ".target_profile")
        if rec["analysis_bundle_created"] and (rec["disposition"] != "eligible"
                or sum(o["role"] == "bundle" for o in rec["outputs"]) != 1 or rec["mapping_errors"]):
            bad("state_contradiction", path + ".analysis_bundle_created")
        if not rec["analysis_bundle_created"] and any(o["role"] == "bundle" for o in rec["outputs"]):
            bad("state_contradiction", path + ".outputs")
        unique([o["path"] for o in rec["outputs"]], "outputs")
        for snap in rec["input_snapshots"]:
            if snap["packet_id"] in packets and _known(packets[snap["packet_id"]]["sha256"]) not in (None, snap["sha256"]):
                bad("attachment_hash_mismatch", path + ".input_snapshots")


def parse_study(raw: Any, limits: ReadLimits | None = None) -> StudyPacket:
    """Validate shapes and relationships, returning bounded content-free errors."""
    issues: list[Diagnostic] = []
    try:
        limits = _limits(limits)
        _preflight(raw, limits)
        # Physical reserialization enforces byte/line limits for direct callers too.
        serialized = _serialize(raw)
        _physical(serialized, limits)
    except InputError as exc:
        return StudyPacket(None, (), (_diag(exc.code),))
    if isinstance(raw, Mapping) and raw.get("study_schema_version") != STUDY_SCHEMA_VERSION:
        issues.append(_diag("unsupported_study_schema_version", "study_schema_version"))
    _validate(raw, ENVELOPE_SCHEMA, "study", issues)
    if not issues:
        _semantic(raw, limits, issues)
        if len(serialized) + sum(_known(p["size_bytes"]) or 0 for p in raw["packet_inventory"]) > raw["import_budget"]["max_total_bytes"]:
            issues.append(_diag("budget_exceeded_partition_required", "import_budget"))
    data = freeze(raw)
    records = ()
    if isinstance(data, Mapping) and isinstance(data.get("records"), tuple):
        records = tuple(StudyRecord(r["record_type"], r["record_id"], r["record_version"], r["study_version"], r)
                        for r in data["records"] if isinstance(r, Mapping)
                        and all(isinstance(r.get(k), str) for k in ("record_type", "record_id", "record_version", "study_version")))
    return StudyPacket(data, records, tuple(issues))


def parse_study_bytes(data: bytes, limits: ReadLimits | None = None) -> StudyPacket:
    """Read strict UTF-8 JSON without duplicate keys or floating-point coercion."""
    try:
        checked = _limits(limits)
        raw = _physical(data, checked)
    except InputError as exc:
        return StudyPacket(None, (), (_diag(exc.code),))
    result = parse_study(raw, checked)
    if (not result.has_errors and len(data) + sum(_known(p["size_bytes"]) or 0 for p in result.data["packet_inventory"])
            > result.data["import_budget"]["max_total_bytes"]):
        return StudyPacket(result.data, result.records,
                           result.diagnostics + (_diag("budget_exceeded_partition_required", "import_budget"),))
    return result


def _serialize(value: Any, level: int = 0) -> bytes:
    def encode(node: Any, depth: int) -> str:
        if isinstance(node, Mapping):
            if not node:
                return "{}"
            lead = "  " * (depth + 1)
            return "{\n" + ",\n".join(lead + json.dumps(k, ensure_ascii=False) + ": " + encode(node[k], depth + 1)
                                       for k in sorted(node)) + "\n" + "  " * depth + "}"
        if isinstance(node, (tuple, list)):
            if not node:
                return "[]"
            lead = "  " * (depth + 1)
            return "[\n" + ",\n".join(lead + encode(v, depth + 1) for v in node) + "\n" + "  " * depth + "]"
        if isinstance(node, ExactNumber):
            return node.token
        return json.dumps(node, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
    try:
        return (encode(value, level) + "\n").encode("utf-8")
    except (TypeError, ValueError, UnicodeError, RecursionError) as exc:
        raise InputError("invalid_json_value") from exc


def canonical_study_bytes(packet_or_mapping: StudyPacket | Mapping[str, Any]) -> bytes:
    """Canonical sorted-key, two-space UTF-8 JSON + LF; exact number lexemes retained."""
    raw = packet_or_mapping.data if isinstance(packet_or_mapping, StudyPacket) else packet_or_mapping
    packet = parse_study(raw)
    if packet.has_errors:
        raise InputError("invalid_study_for_serialization")
    return _serialize(packet.data)


def _attachment_records(data: bytes, form: str, limits: ReadLimits) -> int:
    if form == "bytes":
        return 0
    if form == "json":
        _physical(data, limits)
        return 1
    count = 0
    for line in data.splitlines(keepends=True):
        if not line.strip():
            raise InputError("invalid_jsonl_record")
        value = _physical(line, limits)
        if not isinstance(value, Mapping):
            raise InputError("invalid_jsonl_record")
        count += 1
        if count > limits.max_records:
            raise InputError("record_count_exceeded")
    return count


def load_study(path: str | Path, limits: ReadLimits | None = None) -> LoadedStudy:
    """Snapshot only the declared finite local inventory, never follow/fetch URLs.

    A missing local attachment is inspectable uncertainty. Unsafe paths, changed
    files, hashes, counts and budget overruns are malformed input. A declared
    external attestation remains an assertion at this structural layer.
    """
    issues: list[Diagnostic] = []
    inspections: list[AttachmentInspection] = []
    packet = None
    reader = None
    complete = True
    try:
        limits = _limits(limits)
        source = Path(path)
        if ".." in source.parts:
            raise InputError("unsafe_local_path")
        relative_parts(source.name)
        with LocalReader(source.absolute().parent, limits) as reader:
            snap = reader.read(source.name)
            packet = parse_study_bytes(snap.content, limits)
            issues.extend(packet.diagnostics)
            if not packet.has_errors:
                raw = packet.data
                budget = raw["import_budget"]
                count = len(packet.records)
                if reader.total > budget["max_total_bytes"]:
                    raise InputError("budget_exceeded_partition_required")
                # Runtime budget is capped before any attachment is opened.
                reader.limits = ReadLimits(max_file_bytes=limits.max_file_bytes,
                    max_bundle_bytes=min(limits.max_bundle_bytes, budget["max_total_bytes"]),
                    max_line_bytes=limits.max_line_bytes,
                    max_records=min(limits.max_records, budget["max_total_records"]),
                    max_depth=limits.max_depth, max_number_chars=limits.max_number_chars)
                for i, entry in enumerate(raw["packet_inventory"]):
                    prefix = f"packet_inventory[{i}]"
                    location = _known(entry["location"])
                    expected_hash, expected_size = _known(entry["sha256"]), _known(entry["size_bytes"])
                    actual_hash = actual_size = observed_count = None
                    status = "unavailable_attachment"
                    if location is None:
                        complete = False
                        issues.append(_diag("attachment_unavailable", prefix, "warning"))
                    elif location["kind"] == "external":
                        complete = False
                        status = "external_not_fetched"
                        issues.append(_diag("external_attachment_not_fetched", prefix, "warning"))
                    else:
                        try:
                            if location["path"] == source.name:
                                raise InputError("invalid_value")
                            acquired = reader.read(location["path"])
                            actual_hash, actual_size = acquired.sha256, acquired.size_bytes
                            observed_count = _attachment_records(acquired.content, entry["format"], reader.limits)
                            count += observed_count
                            if count > budget["max_total_records"] or count > limits.max_records:
                                raise InputError("budget_exceeded_partition_required")
                            status = "snapshot_verified" if expected_hash is not None and expected_size is not None else "snapshot_read_unverified"
                            if expected_hash is not None and actual_hash != expected_hash:
                                status = "hash_mismatch"
                                issues.append(_diag("attachment_hash_mismatch", prefix))
                            if expected_size is not None and actual_size != expected_size:
                                status = "size_mismatch"
                                issues.append(_diag("attachment_size_mismatch", prefix))
                            if _known(entry["record_count"]) is not None and observed_count != _known(entry["record_count"]):
                                status = "record_count_mismatch"
                                issues.append(_diag("attachment_record_count_mismatch", prefix))
                        except InputError as exc:
                            complete = False
                            if isinstance(exc.__cause__, FileNotFoundError):
                                issues.append(_diag("attachment_unavailable", prefix, "warning"))
                            else:
                                issues.append(_diag(exc.code, prefix))
                                status = "rejected"
                    inspections.append(AttachmentInspection(entry["packet_id"], entry["verification"], status,
                        expected_hash, actual_hash, expected_size, actual_size, observed_count))
                observed = {item.packet_id: item for item in inspections}
                for i, record in enumerate(raw["records"]):
                    if record["record_type"] != "artifact" or _known(record["content"]) is None:
                        continue
                    inspected = observed.get(_known(record["content"])["packet_id"])
                    if inspected is None or inspected.actual_sha256 is None:
                        continue
                    digest, size = _known(record["sha256"]), _known(record["size_bytes"])
                    if digest is not None and digest != inspected.actual_sha256:
                        issues.append(_diag("artifact_hash_mismatch", f"records[{i}].sha256"))
                    if size is not None and size != inspected.actual_size_bytes:
                        issues.append(_diag("attachment_size_mismatch", f"records[{i}].size_bytes"))
                artifact_observations = {}
                for record in raw["records"]:
                    if record["record_type"] == "artifact" and _known(record["content"]) is not None:
                        item = observed.get(_known(record["content"])["packet_id"])
                        if item and item.actual_sha256 is not None:
                            artifact_observations[record["record_id"]] = item
                for i, record in enumerate(raw["records"]):
                    reference = digest = None
                    if record["record_type"] in {"validation_receipt", "human_review", "adjudication"}:
                        reference, digest = record["artifact_ref"], record["artifact_sha256"]
                    elif record["record_type"] == "collection_ledger":
                        reference, digest = _known(record["prompt_ref"]), _known(record["sent_prompt_sha256"])
                    elif record["record_type"] == "extraction":
                        reference, digest = _known(record["raw_response_ref"]), _known(record["raw_response_sha256"])
                    if reference and digest is not None:
                        actual = artifact_observations.get(reference["record_id"])
                        if actual and actual.actual_sha256 != digest:
                            issues.append(_diag("artifact_hash_mismatch", f"records[{i}]"))
    except (InputError, TypeError, ValueError) as exc:
        complete = False
        issues.append(_diag(exc.code if isinstance(exc, InputError) else "unsafe_local_path"))
    snapshots = MappingProxyType(dict(reader.snapshots)) if reader else MappingProxyType({})
    return LoadedStudy(packet, snapshots, tuple(inspections), tuple(issues), reader.total if reader else 0,
                       complete and not any(d.severity == "error" for d in issues))
