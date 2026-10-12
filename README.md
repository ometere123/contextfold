# ContextFold

**A contract-only GenLayer primitive for consensus-audited semantic memory compaction.**

**Network lock:** StudioNet **61999** (`0xF22F`) · RPC **`https://studio.genlayer.com/api`** · **repository-local `genlayer@0.39.1`**. **No frontend. No Studio Dev/Next. No global CLI.**

## The problem

An agent can shorten 30 pages of earlier instructions into one compact memory, but it cannot prove to other parties that it retained every live duty, prohibition, exception and unresolved point. ContextFold turns compression into an immutable, provenance-mapped, independently checked state transition. It does **not** delete history or claim mathematical proof of free-form natural-language equivalence.

```text
Owner registers immutable memory records
             |
             v
Freeze current frontier (previous accepted capsule + later records)
             |
             v
Propose compact claims and source -> claim map
             |
             +--- deterministic: no source omitted, no extra claim,
             |    all kinds in one group match, text actually shorter
             |
             v
Leader audits ALL source groups for semantic conservation
             |
             v
Validators independently redo same substantive comparison
             |
       +-----+-------+
       |             |
  all groups PASS   any failure / ambiguity
       |             |
 ACCEPTED capsule   REJECTED (no activation)
       |
       v
Version-pinned current certificate; immutable parents and records remain
```

**The powerful part:** one verified capsule becomes a single active memory frontier item for the next revision. Additional records can be folded into it without repeatedly passing the entire original history through the model. Historical records remain accessible for audits. Bounded group mapping permits genuinely redundant clauses to collapse into one shorter claim.

## Claim conservation (not hand-wavy “losslessness”)

Each record has one normative kind: `OBLIGATION=1`, `PROHIBITION=2`, `PERMISSION=3`, `EXCEPTION=4`, `UNRESOLVED=5`, `FACT=6`. For every source slot, the proposer must supply exactly one claim-group index. Every claim group must be referenced; mixed kinds cannot be grouped; and the total proposed claim text must be shorter than the frozen source text.

A GenLayer leader independently inspects every group and returns exactly N booleans; validators perform the full same comparison independently. **All** groups must pass for activation. The audit explicitly preserves actors, scope, numbers, deadlines, exceptions, conditions, permissions, prohibitions and uncertainty, while forbidding new rights or claims. A malformed/ambiguous model response is a FAIL. This is more than format validation: validators reassess the original immutable sources against proposed claims, not the leader's rationale.

A detected omission, invented exception, broadened permission, or disagreement must never activate a new capsule. LLM consensus is not a formal equivalence proof and can share biases: trust is bounded to the frozen record corpus and the independently verified semantic decision. The contract is not a legal compliance or safety certification system.

## State design and bounds

- `Space`: owner, label, revision, latest accepted fold, immutable record IDs.
- `MemoryRecord`: owner-authorized append, kind, text, hash, revision; never rewritten or deleted.
- `Fold`: frozen source texts/kinds/lineage refs, source hash, proposed claims/group mapping, parent fold, version, status and certificate hash.
- `F_PENDING=0`, `F_ACCEPTED=1`, `F_REJECTED=2`, `F_STALE=3`, `F_CANCELLED=4`.
- Up to 160 source records per space, a frontier of up to 16 source clauses and up to 15 folded claims; 1,400 chars per record/claim. Larger histories are supported through successive folds, not one unbounded prompt.
- A later append changes the revision and immediately makes `is_current()` false for older certificates. Competing fold proposals on the same parent are invalidated when the first is accepted. Source/frontier hash is checked again before a pending fold resolves.
- A current capsule returns only the approved claims, never rejected candidate text; full inputs remain queryable through historical reads.

## Public contract API

| Operation | Mode | Purpose |
|---|---|---|
| `create_space(label)` | write, owner established | create independent memory namespace |
| `append_record(space_id, kind, text)` | owner write | immutable fact/norm record |
| `propose_fold(space_id, claims, mapping)` | owner write | frozen candidate and total lineage mapping |
| `resolve_fold(fold_id)` | permissionless write | independent semantic consensus, activate only on all PASS |
| `cancel_fold(fold_id)` | owner write | terminal cancel pending proposal |
| `get_space / get_record / get_fold` | views | inspect all histories, source references and hashes |
| `current_capsule(space_id)` | view | return current claims only while revision valid |
| `is_current(space_id, fold_id, hash)` | view | downstream contract pin to exact certificate/version |

Example (illustrative pseudocode, not an existing on-chain transaction):

```python
sid = contextfold.create_space("Agent policy memory")
r1 = contextfold.append_record(sid, 1, "The agent must obtain Security approval before exporting production customer data.")
r2 = contextfold.append_record(sid, 4, "An emergency may waive Finance signoff, but never Security approval.")
fid = contextfold.propose_fold(sid, [
    "Security approval is mandatory for production customer-data export.",
    "Emergencies may bypass Finance, not Security approval."
], [0, 1])
contextfold.resolve_fold(fid)
assert contextfold.current_capsule(sid)["current"]  # only if full consensus agrees
```

**Note:** The requirement that a candidate be strictly shorter is checked before consensus; the example must be sufficiently shorter than the originals.

## Develop/test (do not invoke global CLI)

```bash
npm install                 # installs EXACTLY genlayer@0.39.1 locally
npm run gl -- --version     # check local version
python -m pip install pytest
python scripts/preflight.py
python -m pytest tests/unit -q
python -m pip install -r requirements-test.txt
python -m pytest tests/direct -q    # requires GenVM Direct Mode runtime
```

The local unit suite includes a simulated SDK state-machine harness; **that is not equivalent to GenVM consensus tests**. The real Direct Mode suite runs in CI with the pinned GenVM runner bundle, alongside GenVM lint/schema validation. Neither test mode is a substitute for remote finality.

## Deploy (requires actual chain verification)

1. Ensure Node.js 20+ and an account already configured/unlocked with your *local* CLI. No key is needed in repository files.
2. Run `npm install` from this repository; never use a global `genlayer` binary.
3. Run `python scripts/deploy_studionet.py`.
4. This checks `eth_chainId` of `https://studio.genlayer.com/api` and requires **61999** before any deployment. If the chain-ID endpoint is unavailable or returns anything else, deployment **stops**. Investigate RPC behavior rather than switching networks or bypassing the guard.
5. Wait for `FINALIZED`, inspect validator result, fetch on-chain source via local CLI, and record verified parity and receipts in `docs/DEPLOYMENT.md`.

Full handoff/proof checklist: [docs/AGENT_HANDOFF.md](docs/AGENT_HANDOFF.md). Threat model: [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md).

## Verified status

The current source is deployed at
`0xae293Cb699FF2c09E1D6281325157647900e5601` on StudioNet `61999`.
Deployment, source parity, finalized live lifecycle receipts, and limitations
are recorded in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md). Current regression
evidence is 15 unit tests, 16 Direct Mode tests, and 3/3 AST lint checks.
Extended local semantic linter commands did not complete on Windows; that is
explicitly not claimed as a pass.

MIT licensed. Built for the reusable **Intelligent Contracts** category, not Projects.
