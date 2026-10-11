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
