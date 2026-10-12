# StudioNet deployment evidence

This record contains observed evidence for the ContextFold deployment on GenLayer
StudioNet only.

| Item | Observed result |
|---|---|
| Network | StudioNet, chain ID `61999` (`0xF22F`) |
| RPC | `https://studio.genlayer.com/api` |
| Local CLI | `genlayer@0.39.1` (`npm run gl -- --version`) |
| Contract | `0xc6359cDc332F78D5f06BFD2e8212e9E8E0477653` |
| Deployment transaction | `0xab7eb386ffd82faf3ae0e6f5659f9cd875e777504e52151598d670501d9e8a05` |
| Deployment receipt | `FINALIZED`, `MAJORITY_AGREE`, leader/validator execution `SUCCESS`, return `null` |
| Contract explorer | [StudioNet contract](https://explorer-studio.genlayer.com/address/0xc6359cDc332F78D5f06BFD2e8212e9E8E0477653) |
| Local source SHA-256 | `38e83573f0786b398618efd900065a1434db3580f4f31af1992492797d8ede88` (UTF-8, CRLF-normalized) |
| Deployed code SHA-256 | `71a39d617a1468d2bd18fd290e59209001b0ff95256d5a9c31b3df14e82e88c2` (CLI-returned source, CRLF-normalized) |
| Source parity | Exact substantive parity confirmed; the RPC-returned source has two additional trailing newlines. Shared-content SHA-256 after removing trailing newlines: `60ff28f960790157a3b74298507640aee948a27fdaab861b445ca48d7b02c8d3`. |
| GenVM AST lint | `3/3` passed for `contracts/contextfold.py` (`genvm-lint lint ... --json`) |
| GenVM semantic validation | Not verified: `genvm-lint validate`, `check` and `schema` did not complete in this Windows environment. |
| Unit suite | `14 passed` |
| Direct Mode suite | `13 passed` |
| Package lock | Existing `package-lock.json` was present; `npm install --no-audit --no-fund` produced no lockfile diff. |

## Live lifecycle evidence

All writes below were submitted with the repository-local CLI/account and then
polled to `FINALIZED`. Successful writes returned `MAJORITY_AGREE`; readbacks
were performed with finalized contract calls.

### Accepted and multi-generation folds

Space `3` (`Duplicate-fact-lifecycle`) demonstrates an accepted fold followed by
a second accepted generation:

| Step | Transaction | Final readback |
|---|---|---|
| Create space | `0xf9a72a556a5a06d37be4d3115b5266ba7b23506feebf60d9d0477ee1947f6400` | Space `3` created |
| Append duplicate fact 1 | `0x723d38f2cf3921aeec4c90d9172622fa10059f954bc4a09d8da1489d2449b686` | Record `5`, finalized success |
| Append duplicate fact 2 | `0xeb98ab5f4f66dc01bbfbbc44c0c55c4eb649b7e378eff1f336a9236995bef3a6` | Record `6`, finalized success |
| Propose fold 3 | `0xf65806fb9b69965dd339f3f886ed90a5cba222d1c08e0a083ffa988636a78ff7` | Fold `3` proposed, finalized success |
| Resolve fold 3 | `0x62af1826f34a167ec3b8bf8dcc3791ecde059eb79db8aa2bc4754d31355278bc` | Fold `3`: `status=1` (`F_ACCEPTED`), certificate `1a1462bf7bb4ec6c9ab4488e3155af770181fbbc1aad305b55130f9d396eb0c6`, `current=true` |
| Append duplicate fact 3 | `0x828b273f2e0cdc91c0e9ac42251f74dd0aced863f0d97c382cabce050b65eaa8` | Record `7`, finalized success |
| Propose fold 4 | `0xea0c61c9c5e0fb0a558ae18cf405f7e49b04309fee922a1d1a64e94b50e6e45a` | Fold `4` proposed, finalized success |
| Resolve fold 4 | `0x0ba88ec3fb60807cdf84a0fffb3e0e37485a231c63ea3963564ee2c033b01a93` | Fold `4`: `status=1` (`F_ACCEPTED`), parent `3`, certificate `5f19cde05d25a473dd5b786eca860cea502337ccc12ba030a2974c6db5368cc3`, `current=true` |

### Rejected folds

Spaces `1` and `2` contain over-compressed proposals. Their resolution
transactions finalized with successful GenVM execution and validator agreement,
while the contract recorded `F_REJECTED` (`status=2`) because semantic
conservation was not established:

| Space / fold | Proposal | Resolution | Readback |
|---|---|---|---|
| Space `1`, fold `1` | `0xde9e31d911e1e5716e0d1dd612c3c807491454a81d4be4eb25660fd6e9af3318` | `0x147c4f48f80fe72c0f094a228ab405e41d2b7cb4600ba91948b563996a9f3643` | `status=2`, reason `semantic conservation not independently established` |
| Space `2`, fold `2` | `0xa68f5a023d5ca156fea460eb3a484b108d49cb6671ab50f9b28762e1d60c69f6` | `0x4ae556fca4e2f78b947ff51235a2e78194830db39a31f6402d69617bd77e9759` | `status=2`, reason `semantic conservation not independently established` |

### Stale proposal

Space `3`, fold `5` was proposed against a finalized frontier, then a new
record was appended before resolution. Its finalized resolution safely marked
the proposal stale without activating it:

| Step | Transaction | Final readback |
|---|---|---|
| Append records 8 and 9 | `0x258011d7f2483d636228a57fc8e05d7a00e791a68739cf4328fcc2581fc56498`, `0x2aab498b404c7ae02a9ae5a1c794a98238f569081eafbc10ace1116092a08902` | Both finalized success |
| Propose fold 5 | `0xb222c932b65739f530d35dc59ee124835f8a1a5cae8ffeca74e1ef940fa6743c` | Fold `5` pending proposal finalized success |
| Advance frontier | `0xd69279743b059781e3845aefad869ecb1e12a5c7b8f8b7a214c44d152970dcfc` | Record `10`, finalized success |
| Resolve fold 5 | `0xb631b5da55112b9655586feb7dee6436b1b843b43aa09d6692cd23ee988cebd5` | Fold `5`: `status=3` (`F_STALE`), reason `frontier advanced; proposal cannot be activated`; current capsule remains fold `4` |

## Failed deployment attempt

The first deployment attempt is retained as a failure record, not deployment
evidence. Transaction
`0xde3e6e3ae7bde190862c220e0fab9275ee93ebee0b43a7388a4bfadb60256a9b`
finalized with `MAJORITY_AGREE` but leader/validator execution `ERROR` and
`invalid_contract`; no usable contract address was produced. The contract was
then corrected by removing a non-pinned comment above the required dependency
header and deployed successfully using the transaction recorded above.

Transaction explorer links use:
`https://explorer-studio.genlayer.com/tx/<transaction-hash>`.
