# ContextFold — standalone GenLayer Intelligent Contract

ContextFold is a bounded, owner-isolated semantic-memory compression
primitive. It freezes an active frontier, requires a total source-to-claim
mapping, preserves normative kinds, and requires independent validator
re-execution before a shorter capsule becomes current.

## Current verified deployment

- Network: StudioNet, chain `61999`
- RPC: `https://studio.genlayer.com/api`
- Local CLI: repository-local `genlayer@0.39.1`
- Contract: `0xae293Cb699FF2c09E1D6281325157647900e5601`
- Deployment transaction: `0x7b2edc209bd0553e0b99381334ee99f6360fef58f9dd9f4932809765cf398677`
- Deployment status: `FINALIZED / MAJORITY_AGREE / SUCCESS`
- Source parity: exact after newline normalization; see [deployment evidence](docs/DEPLOYMENT.md)

## Live proof

The current deployment has live finalized evidence for:

- accepted obligation-plus-exception compression with `current=true`;
- rejected omission, negation, deadline, invented-permission, exception-loss,
  and unresolved-uncertainty candidates;
- competing-fold stale invalidation;
- accepted second-generation re-fold with parent certificate lineage;
- downstream `is_current()` enforcement, including safe zero-fold rejection.

## Engineering evidence

- Unit tests: `15 passed`
- Direct Mode tests: `16 passed`
- GenVM AST lint: `3/3`
- GitHub CI: use the run attached to the final commit.
- The pinned Windows environment did not complete extended local
  `genvm-lint validate/check/schema`; this limitation is not presented as a
  semantic validation pass.

## Limits

Natural-language equivalence remains probabilistic: validators can share model
mistakes. ContextFold does not prove that source records are true or complete,
does not access outside web sources, and retains historical storage while
compressing only the active semantic frontier. See [THREAT_MODEL.md](docs/THREAT_MODEL.md).
