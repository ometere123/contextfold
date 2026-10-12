# StudioNet deployment evidence

This record describes the current ContextFold deployment and observed StudioNet
evidence. Historical deployments are retained only as historical records.

## Current deployment

| Item | Observed result |
|---|---|
| Network | StudioNet, chain ID `61999` (`0xF22F`) |
| RPC | `https://studio.genlayer.com/api` |
| Local CLI | repository-local `genlayer@0.39.1` |
| Contract | `0xae293Cb699FF2c09E1D6281325157647900e5601` |
| Deployment transaction | `0x7b2edc209bd0553e0b99381334ee99f6360fef58f9dd9f4932809765cf398677` |
| Deployment receipt | `FINALIZED / MAJORITY_AGREE / SUCCESS`; five validator votes agreed |
| Explorer | https://explorer-studio.genlayer.com/address/0xae293Cb699FF2c09E1D6281325157647900e5601 |
| Local source SHA-256 | `c281bf8e233cc99930bd3787113a94d3f7f256f28f641cd339f97f1984b24ca0` |
| Deployed source SHA-256 | `c281bf8e233cc99930bd3787113a94d3f7f256f28f641cd339f97f1984b24ca0` |
| Source parity | Exact after CRLF normalization and removal of the CLI wrapper's trailing newline |

## Verification

| Gate | Result |
|---|---|
| Preflight | Passed for StudioNet `61999` and CLI `0.39.1` |
| Unit suite | `15 passed` |
| Direct Mode suite | `16 passed` |
| GenVM AST lint | `3/3` passed |
| Extended semantic linter locally | Not completed; the pinned Windows linter process timed out. This is not claimed as a semantic-validation pass. |
| CI | Use the GitHub Actions run attached to the final commit; no local npm `verify` script exists. |

## Final-deployment live lifecycle evidence

Every transaction below was explicitly polled to `FINALIZED`. Successful
transactions returned `MAJORITY_AGREE`; readbacks are from the final address.

### Accepted obligation-plus-exception compression

Space `2` contains a meaningful obligation and exception:

| Step | Transaction | Readback |
|---|---|---|
| Create space | `0x47d6ae4662fd3073a1cdca20666fd74f587a954b80f008ca133d19fdeae25058` | Space `2` |
| Append obligation | `0x207d65cfb7e35e5953ec55db6928f8b3880814c35917e3b001da3b52b7f7f01a` | Record `3`, finalized success |
| Append exception | `0x5b09cd863265a63a37d25c0eba444da7ace27c83683e727bdebd0ce887290aed` | Record `4`, finalized success |
| Propose fold | `0x1b13d4805e503d15a10a26b73e55932c12204e1aaf443c87e6d4d04899148922` | Fold `2` |
| Resolve fold | `0x3bbc80b1312de6439dcf92e8b7a6cceca6f338110a4d0756538e1503a852ac1c` | `FINALIZED / MAJORITY_AGREE / SUCCESS`, `equivalent=[true,true]` |

Final `current_capsule(2)` readback: `current=true`, `fold_id=2`, kinds
`[OBLIGATION, EXCEPTION]`, certificate
`dfeabfe05976bec1a1702b385704456705af9d000f99906f380e74f9d2fe9071`.

### Rejected semantic candidates

The following finalized resolutions rejected materially unsafe proposals. The
negative matrix contains omitted approval, a negation, a missing deadline,
invented permission, exception loss, and converting unresolved uncertainty to
final:

| Matrix | Proposal | Resolution | Readback |
|---|---|---|---|
| Initial obligation/exception loss | `0x466f83a1192c4e59af4405cd2e76a00fd343a9a7c47858392ad6e2f79988188a` | `0xa8d3a7bb2223550776c5cda33b10682a8395e45ecf602ec235b0bd8f804e2dbd` | `FINALIZED / MAJORITY_AGREE / SUCCESS`; `equivalent=[false,true]`; fold `1` `F_REJECTED` |
| Six-case negative matrix | `0x792c2378192af212a158bad841dcc99ff2337dd0f2119cca89794ed8a8bbac7c` | `0x4086e7261246efeecdf399053029f3f3d86d72856985ce562c36674e6fc89a57` | `FINALIZED / MAJORITY_AGREE / SUCCESS`; fold `3` `F_REJECTED` |

The six source appends were finalized in transactions:
`0xba644f8093c3d6009ae33a3a896c5f33b667c2ca031d2bda2fdd84dc56d1fa6c`,
`0x4e9d72accdc9aba3f8e663da520fc6ee76db78ac3433d9b51b45d86b9e5cf5f3`,
`0x32325ba66d7479739b2a8557c5ecc861a0656df91ec148d7f0e7a298a0555c24`,
`0x8450750db03705680a86836aadecf9852c19547c88e421b2752c75bb088774d3`,
`0xb2193e8b874435d1586295b7b1e2225be0f428c2621a2d3a7e4b7421f802b480`, and
`0x1b0b9d6eb1e809a2f7446d974c9b0420710a9b3ae1d7e89ac490aca7dcd290a5`.

### Multi-generation and stale protection

Space `4` demonstrates accepted compression, competing-fold invalidation, and
an accepted second generation:

| Step | Transaction | Readback |
|---|---|---|
| Create space | `0x09bc6e01d472963c550f75f7faf501cc8c529ae77251b5109e1e5eee0c299c95` | Space `4` |
| Append duplicate facts | `0xc9a7fcebccff8ac63938a6f7cf4ab10589e262a3f31709dc8cbf15a5a1868eb3`, `0xb23f18ee4373ced52005393a63c00d41996b70b6bcfb10d0e4e06639ed97ba9b` | Records `12`, `13` |
| Competing proposals | `0xa433a474c1ad52d92631d54822a734611f1afdac3b574a4c55973e9d7a3036ee`, `0x6e4939091485086a344829ebf1b2dd6d4f1df6779e74fa39ae46143bbe93fe06` | Folds `7`, `8` |
| Resolve fold `7` | `0x78c2cf85641734764fa6f51314ff761693c50a9eecb55e53c9b816c931c41d37` | Fold `7` `F_ACCEPTED`, certificate `5610baf8570242ef49f15505e36ecd37d693b6f2feded6ef5ef9ac84f6ec1e67` |
| Resolve fold `8` | `0xfb47356ec1ea51703292639b1fd9ab10247c4024e4c4894feb376e894455d2b2` | Fold `8` `F_STALE`, `frontier advanced` |
| Append next-generation fact | `0x6d972c798e8eeae6086e48c773e2cc5e83dd6c8a3f6b1fecd2da5bc2348e11a7` | Record `14` |
| Propose/resolve fold `9` | `0x8954461b0696a63dba908428826919b96a15254fa8707e67127897bfd48775f5`, `0x0cdc4bc300268a08a568d25ebfa458fa9de783febfd5e9acc7ce22545b1b3417` | Fold `9` `F_ACCEPTED`, parent `7`, certificate `a70fdb37bfdff95ce9acf61b5a7a323a17a59941e4e8f2dd82735c68bf6adabb` |

Final readbacks: `current_capsule(4).current=true`, `fold_id=9`,
`is_current(4,9,<certificate>)=true`, and `is_current(4,0,<certificate>)=false`.

## Direct Mode adversarial coverage

The `16` Direct Mode tests cover dishonest leader vectors, malformed verdicts,
omitted exceptions, mixed kinds, stale proposals, competing folds, owner
isolation, invalid parent lineage, certificate replay after a frontier change,
zero-fold reads, UTF-8 compression boundaries, and parent-preserving
re-folding. Direct Mode is local evidence, not a substitute for the live
receipts above.

## Historical deployment

The prior deployment `0xc6359cDc332F78D5f06BFD2e8212e9E8E0477653` and its
transaction `0xab7eb386ffd82faf3ae0e6f5659f9cd875e777504e52151598d670501d9e8a05`
are superseded historical evidence. They are not evidence for the current
address.

The first attempted deployment transaction
`0xde3e6e3ae7bde190862c220e0fab9275ee93ebee0b43a7388a4bfadb60256a9b`
finalized with `invalid_contract` and is retained only as a failed attempt.
