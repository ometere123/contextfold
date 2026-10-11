# ContextFold security invariants and limits

## Trust boundaries

* Owner controls the original text and proposed compression, but cannot directly mark a fold accepted.
* Validators independently compare frozen originals against proposed claims. Comparison checks are semantic, not superficial output shape.
* No outside web content is accessed by this primitive. The original user-authored record can itself contain malicious instructions; the prompt frames it as quoted, untrusted JSON data.
* Accepted memory means validator-confirmed *bounded semantic conservation relative to the original corpus*, not that original corpus is true, complete, authorized or safe.
* Independent models can agree on a mistaken comparison. No cryptographic proof of natural-language equivalence is possible from the LLM alone.

## Attacks and mitigations

| Attack | Mitigation |
|---|---|
| Omit one source | mapping length must equal source count; every claim referenced |
| Collapse heterogeneous types | all inputs in a group must share normative kind |
| Invent a clause | full semantic source-vs-candidate validator check |
| Drop exception, qualifier or uncertainty | prompt explicitly verifies conditions/exceptions/uncertainty in each group |
| Leader always returns PASS | validator independently re-runs all grouped audits; boolean vector compared |
| Leader returns truthy strings or shorter result list | strict `type(x) is bool`, exact count; malformed response means FAIL |
| Propose using stale history | source root, base revision and parent fold fixed; rechecked before activation |
| Race two proposals | only first accepted against a given latest parent can activate; second is STALE |
| Reuse accepted certificate after new record | revision mismatch causes `is_current == False` |
| Unauthorized editing | owner-only append/propose/cancel; no mutation of old records |
| Infinite model work | 16-source/claim frontier and per-text limits |
| Silent loss of audit trail | original records, frozen sources, mappings and all fold attempts remain queryable |
| Summary used before finality | no current certificate until consensus-derived ACCEPTED status |

## Important non-guarantees

* Free-form semantic equivalence is probabilistic; validators may share model/systematic errors.
* No cryptographic provenance for upstream record authors beyond the memory space owner.
* This prototype's storage does not physically shrink. It compresses the *active semantic context* while preserving history.
* No cross-network support. Configured for StudioNet 61999 and local CLI 0.39.1 only.
* No independent audit of original text, web truth, or source availability.
* No live GEN economics or external authority over downstream agents; a consumer must explicitly pin a certificate using `is_current` and enforce its own actions.
* No automated recursive multi-level graph proof beyond parent certificate lineage; every new fold is independently audited against its immediate accepted parent claim set and new append-only records.

## Mandatory adversarial tests before a score claim

Model attempts that should fail: missing record, suppressed negation, omitted deadline, altered jurisdiction, invented right, inverted permission, changed number, dropped carveout, hidden unresolved issue, content explicitly instructing model to ignore guards, dishonest leader vector, stale revision, forged certificate hash. Document leader/validator votes rather than reporting only a returned application status.
