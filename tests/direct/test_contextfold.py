"""GenLayer Direct Mode tests (requires genlayer-testing-suite v0.29.2).

Run separately from the network-free unit suite. These tests require the
real GenVM Direct Mode environment and must not be claimed as green until run.
"""
import json

CONTRACT = "contracts/contextfold.py"


def prepared(direct_vm, direct_deploy):
    ic = direct_deploy(CONTRACT)
    space_id = ic.create_space("Agent memory")
    ic.append_record(space_id, 1, "The purchasing agent must obtain Security approval before sending any production customer data to an external provider.")
    ic.append_record(space_id, 4, "The emergency exception allows processing without Finance approval but does not waive Security approval.")
    return ic, space_id


def accepted_result():
    return json.dumps({"equivalent": [True, True]})


def test_successful_fold_has_consumable_certificate(direct_vm, direct_deploy):
    ic, sid = prepared(direct_vm, direct_deploy)
    direct_vm.mock_llm("CONTEXTFOLD / SEMANTIC CONSERVATION AUDIT", accepted_result())
    fid = ic.propose_fold(sid, [
        "Security approval is mandatory before exporting production customer data.",
        "Emergency processing may bypass Finance approval, never Security approval.",
    ], [0, 1])
    ic.resolve_fold(fid)
    out = ic.get_fold(fid)
    assert out["status"] == 1
    assert out["certificate_hash"]
    assert ic.is_current(sid, fid, out["certificate_hash"]) is True
    assert direct_vm.run_validator() is True


def test_semantic_omission_rejected(direct_vm, direct_deploy):
    ic, sid = prepared(direct_vm, direct_deploy)
    direct_vm.mock_llm("CONTEXTFOLD / SEMANTIC CONSERVATION AUDIT", '{"equivalent":[false,true]}')
    fid = ic.propose_fold(sid, [
        "Customer data may be sent to outside providers.",
        "Emergency processing may bypass Finance approval, never Security approval.",
    ], [0, 1])
    ic.resolve_fold(fid)
    assert ic.get_fold(fid)["status"] == 2
    assert ic.current_capsule(sid)["current"] is False
    assert direct_vm.run_validator() is True


def test_append_after_proposal_stales_pending_fold(direct_vm, direct_deploy):
    ic, sid = prepared(direct_vm, direct_deploy)
    fid = ic.propose_fold(sid, [
        "Security approves before production customer data leaves the service.",
        "Emergency processing may skip Finance but never Security approval.",
    ], [0, 1])
    ic.append_record(sid, 2, "The agent must not retain customer data after service completion.")
    ic.resolve_fold(fid)
    assert ic.get_fold(fid)["status"] == 3


def test_mixed_kinds_cannot_be_laundered_into_one_claim(direct_vm, direct_deploy):
    ic, sid = prepared(direct_vm, direct_deploy)
    with direct_vm.expect_revert("EXPECTED"):
        ic.propose_fold(sid, ["Security and emergency processing rules apply."], [0, 0])


def test_uncompressed_proposal_refused(direct_vm, direct_deploy):
    ic, sid = prepared(direct_vm, direct_deploy)
    with direct_vm.expect_revert("EXPECTED"):
        ic.propose_fold(sid, [
            "The purchasing agent must obtain Security approval before sending any production customer data to an external provider.",
            "The emergency exception allows processing without Finance approval but does not waive Security approval.",
        ], [0, 1])


def test_validator_rejects_forged_leader_pass(direct_vm, direct_deploy):
    """A leader result cannot turn a validator FAIL into an ACCEPTED fold."""
    ic, sid = prepared(direct_vm, direct_deploy)
    direct_vm.mock_llm("CONTEXTFOLD / SEMANTIC CONSERVATION AUDIT", '{"equivalent":[false,false]}')
    fid = ic.propose_fold(sid, [
        "Security approval is mandatory before exporting production customer data.",
        "Emergency processing may bypass Finance approval, never Security approval.",
    ], [0, 1])
    ic.resolve_fold(fid)
    assert ic.get_fold(fid)["status"] == 2
    assert direct_vm.run_validator(leader_result={"equivalent": [True, True]}) is False


def test_omitted_exception_is_rejected(direct_vm, direct_deploy):
    ic, sid = prepared(direct_vm, direct_deploy)
    direct_vm.mock_llm(
        "CONTEXTFOLD / SEMANTIC CONSERVATION AUDIT",
        '{"equivalent":[true,false]}',
    )
    fid = ic.propose_fold(sid, [
        "Security approval is mandatory before exporting production customer data.",
        "Emergency processing may bypass Finance approval.",
    ], [0, 1])
    ic.resolve_fold(fid)
    assert ic.get_fold(fid)["status"] == 2
    assert direct_vm.run_validator() is True


def test_certificate_replay_fails_after_frontier_changes(direct_vm, direct_deploy):
    ic, sid = prepared(direct_vm, direct_deploy)
    direct_vm.mock_llm("CONTEXTFOLD / SEMANTIC CONSERVATION AUDIT", accepted_result())
    fid = ic.propose_fold(sid, [
        "Security approval is mandatory before exporting production customer data.",
        "Emergency processing may bypass Finance approval, never Security approval.",
    ], [0, 1])
    ic.resolve_fold(fid)
    certificate = ic.get_fold(fid)["certificate_hash"]
    assert ic.is_current(sid, fid, certificate) is True
    ic.append_record(sid, 6, "The release date remains unresolved pending review.")
    assert ic.is_current(sid, fid, certificate) is False
    assert ic.is_current(sid, fid, "") is False


def test_new_space_zero_fold_is_current_false_not_a_revert(direct_vm, direct_deploy):
    ic = direct_deploy(CONTRACT)
    sid = ic.create_space("Empty")
    assert ic.is_current(sid, 0, "not-a-certificate") is False


def test_compression_boundary_uses_utf8_bytes_not_codepoints(direct_vm, direct_deploy):
    ic = direct_deploy(CONTRACT)
    sid = ic.create_space("Unicode")
    for text in ("a", "b", "c"):
        ic.append_record(sid, 6, text)
    # One code point is shorter than three source code points, but the UTF-8
    # payload for 😀 is four bytes and therefore is not compression.
    with direct_vm.expect_revert("proposal does not shorten"):
        ic.propose_fold(sid, ["😀"], [0, 0, 0])


def test_malformed_verdicts_cannot_activate_a_fold(direct_vm, direct_deploy):
    ic, sid = prepared(direct_vm, direct_deploy)
    direct_vm.mock_llm(
        "CONTEXTFOLD / SEMANTIC CONSERVATION AUDIT",
        '{"equivalent":["true",true]}',
    )
    fid = ic.propose_fold(sid, [
        "Security approval is mandatory before exporting production customer data.",
        "Emergency processing may bypass Finance approval, never Security approval.",
    ], [0, 1])
    ic.resolve_fold(fid)
    assert ic.get_fold(fid)["status"] == 2
    assert direct_vm.run_validator() is True


def test_competing_fold_is_stale_after_parent_activation(direct_vm, direct_deploy):
    ic, sid = prepared(direct_vm, direct_deploy)
    direct_vm.mock_llm(
        "CONTEXTFOLD / SEMANTIC CONSERVATION AUDIT",
        '{"equivalent":[true,true]}',
    )
    claims = [
        "Security approval is mandatory before exporting production customer data.",
        "Emergency processing may bypass Finance approval, never Security approval.",
    ]
    first = ic.propose_fold(sid, claims, [0, 1])
    second = ic.propose_fold(sid, claims, [0, 1])
    ic.resolve_fold(first)
    ic.resolve_fold(second)
    assert ic.get_fold(first)["status"] == 1
    assert ic.get_fold(second)["status"] == 3
    assert ic.get_space(sid)["latest_fold_id"] == first


def test_relabelled_claim_order_keeps_source_lineage_and_kinds(direct_vm, direct_deploy):
    ic, sid = prepared(direct_vm, direct_deploy)
    direct_vm.mock_llm(
        "CONTEXTFOLD / SEMANTIC CONSERVATION AUDIT",
        '{"equivalent":[true,true]}',
    )
    fid = ic.propose_fold(sid, [
        "Emergency processing may bypass Finance approval, never Security approval.",
        "Security approval is mandatory before exporting production customer data.",
    ], [1, 0])
    proposed = ic.get_fold(fid)
    assert proposed["mapping"] == [1, 0]
    assert proposed["claim_kinds"] == [4, 1]
    assert proposed["source_refs"] == ["record:1", "record:2"]
    ic.resolve_fold(fid)
    assert ic.get_fold(fid)["status"] == 1


def test_frontier_bound_requires_a_fold_before_more_records(direct_vm, direct_deploy):
    ic, sid = prepared(direct_vm, direct_deploy)
    for index in range(14):
        ic.append_record(sid, 6, f"Additional bounded fact number {index}.")
    assert ic.get_space(sid)["record_count"] == 16
    with direct_vm.expect_revert("fold the current frontier"):
        ic.append_record(sid, 6, "This seventeenth source must be rejected.")


def test_re_fold_preserves_parent_lineage_and_invalidates_parent(direct_vm, direct_deploy):
    ic, sid = prepared(direct_vm, direct_deploy)
    direct_vm.mock_llm(
        "CONTEXTFOLD / SEMANTIC CONSERVATION AUDIT",
        '{"equivalent":[true,true]}',
    )
    first = ic.propose_fold(sid, [
        "Security approval is mandatory before exporting production customer data.",
        "Emergency processing may bypass Finance approval, never Security approval.",
    ], [0, 1])
    ic.resolve_fold(first)
    first_hash = ic.get_fold(first)["certificate_hash"]
    ic.append_record(sid, 6, "The release date remains unresolved and is not final.")
    direct_vm.clear_mocks()
    direct_vm.mock_llm(
        "CONTEXTFOLD / SEMANTIC CONSERVATION AUDIT",
        '{"equivalent":[true,true,true]}',
    )
    second = ic.propose_fold(sid, [
        "Security approval required before exporting production data.",
        "Emergency bypasses Finance, never Security, for outside data.",
        "The release date is unresolved and not final.",
    ], [0, 1, 2])
    assert ic.get_fold(second)["parent_fold_id"] == first
    assert ic.get_fold(second)["source_refs"][0] == f"fold:{first}:0"
    ic.resolve_fold(second)
    assert ic.get_fold(second)["status"] == 1
    assert ic.is_current(sid, first, first_hash) is False


def test_owner_isolation_blocks_foreign_record_and_fold_writes(
    direct_vm, direct_deploy, direct_bob
):
    ic, sid = prepared(direct_vm, direct_deploy)
    with direct_vm.prank(direct_bob):
        with direct_vm.expect_revert("owner only"):
            ic.append_record(sid, 6, "A foreign writer must not alter this space.")
        with direct_vm.expect_revert("owner only"):
            ic.propose_fold(sid, [
                "Security approval is mandatory before exporting production customer data.",
                "Emergency processing may bypass Finance approval, never Security approval.",
            ], [0, 1])
