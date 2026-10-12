"""Local state-machine simulations against the exact contract source.

These intentionally do not masquerade as GenVM/validator tests. They inject a
minimal SDK-compatible façade and check logical edge cases without network.
"""
import dataclasses
import hashlib
import importlib.util
import json
import sys
import types
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[2] / "contracts/contextfold.py"


def load_with_stub():
    package = types.ModuleType("genlayer")
    class UserError(Exception):
        pass
    class Ret:
        def __init__(self, value): self.calldata = value
    class VM:
        Return = Ret
        @staticmethod
        def run_nondet_unsafe(leader, validator):
            result = leader()
            if not validator(Ret(result)):
                raise ValueError("simulated validator disagreed")
            return result
    VM.UserError = UserError
    class Public:
        write = staticmethod(lambda method: method)
        view = staticmethod(lambda method: method)
    class Event:
        def __init__(self, *args, **kwargs): pass
        def emit(self): pass
    class GenericList(list):
        @classmethod
        def __class_getitem__(cls, item): return cls
    class Tree:
        @classmethod
        def __class_getitem__(cls, item): return cls
    class StorageMap(dict):
        def __init__(self, cls): super().__init__(); self.cls = cls
        def get_or_insert_default(self, key):
            if key not in self:
                item = object.__new__(self.cls)
                for name, typ in self.cls.__annotations__.items():
                    if typ is GenericList: value = GenericList()
                    elif typ is str: value = ""
                    elif typ is int: value = 0
                    else: value = ""
                    setattr(item, name, value)
                self[key] = item
            return self[key]
    class Keccak:
        def __init__(self, value): self.value = value
        def hexdigest(self): return hashlib.sha3_256(self.value).hexdigest()
    class Message:
        sender_address = "owner"
    gl = types.SimpleNamespace(
        vm=VM(), public=Public(), message=Message(), Event=Event,
        contract_interface=lambda cls: cls, Contract=object,
    )
    package.gl = gl
    package.u256 = int
    package.u32 = int
    package.u8 = int
    package.Address = str
    package.TreeMap = Tree
    package.DynArray = GenericList
    package.Keccak256 = Keccak
    package.allow_storage = lambda cls: cls
    package.__all__ = ["gl", "u256", "u32", "u8", "Address", "TreeMap", "DynArray", "Keccak256", "allow_storage"]
    sys.modules["genlayer"] = package
    try:
        spec = importlib.util.spec_from_file_location("contextfold_simulated", SRC)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    finally:
        del sys.modules["genlayer"]
    contract = module.ContextFold()
    contract.spaces = StorageMap(module.Space)
    contract.records = StorageMap(module.MemoryRecord)
    contract.folds = StorageMap(module.Fold)
    return contract, module, gl


def fixture():
    ic, mod, gl = load_with_stub()
    sid = ic.create_space("Testing")
    ic.append_record(sid, mod.K_OBLIGATION,
                     "The operator must obtain written Security approval before publishing any production customer information to an external system.")
    ic.append_record(sid, mod.K_EXCEPTION,
                     "An emergency may waive Finance approval, but Security approval must always remain mandatory before external customer-data publication.")
    return ic, mod, gl, sid


def candidate():
    return ["Written Security approval is required before external publication of production customer information.",
            "Emergency waives Finance approval, never Security approval for external customer-data publication."]


def test_success_and_invalidation_on_append():
    ic, m, gl, sid = fixture()
    gl.nondet = types.SimpleNamespace(exec_prompt=lambda *a, **k: {"equivalent": [True, True]})
    fid = ic.propose_fold(sid, candidate(), [0, 1])
    ic.resolve_fold(fid)
    cert = ic.get_fold(fid)["certificate_hash"]
    assert ic.is_current(sid, fid, cert)
    assert not ic.is_current(sid, fid, "invalid")
    ic.append_record(sid, m.K_FACT, "The release date remains unknown pending review.")
    assert not ic.is_current(sid, fid, cert)
    assert not ic.current_capsule(sid)["current"]


def test_stale_proposal_does_not_activate():
    ic, m, gl, sid = fixture()
    fid = ic.propose_fold(sid, candidate(), [0, 1])
    ic.append_record(sid, m.K_FACT, "The release date remains unknown pending review.")
    ic.resolve_fold(fid)
    assert ic.get_fold(fid)["status"] == m.F_STALE
    assert ic.get_space(sid)["latest_fold_id"] == 0


def test_rejected_fold_is_not_live_memory():
    ic, m, gl, sid = fixture()
    gl.nondet = types.SimpleNamespace(exec_prompt=lambda *a, **k: {"equivalent": [False, True]})
    fid = ic.propose_fold(sid, candidate(), [0, 1])
    ic.resolve_fold(fid)
    assert ic.get_fold(fid)["status"] == m.F_REJECTED
    assert not ic.current_capsule(sid)["current"]


def test_folding_prior_capsule_and_new_delta():
    ic, m, gl, sid = fixture()
    gl.nondet = types.SimpleNamespace(exec_prompt=lambda *a, **k: {"equivalent": [True, True]})
    f1 = ic.propose_fold(sid, candidate(), [0, 1])
    ic.resolve_fold(f1)
    ic.append_record(sid, m.K_FACT, "The release date remains unknown pending review and must not be described as final.")
    f2 = ic.propose_fold(sid, [
        "Security must approve production customer data before outside publication.",
        "Emergency can skip Finance signoff, not Security signoff for outside customer data.",
        "The release date is unresolved and not final."], [0, 1, 2])
    assert ic.get_fold(f2)["parent_fold_id"] == f1
    gl.nondet = types.SimpleNamespace(exec_prompt=lambda *a, **k: {"equivalent": [True, True, True]})
    ic.resolve_fold(f2)
    assert ic.get_fold(f2)["status"] == m.F_ACCEPTED
    assert not ic.is_current(sid, f1, ic.get_fold(f1)["certificate_hash"])


def test_invalid_parent_lineage_fails_closed():
    ic, m, gl, sid = fixture()
    gl.nondet = types.SimpleNamespace(exec_prompt=lambda *a, **k: {"equivalent": [False, False]})
    rejected = ic.propose_fold(sid, candidate(), [0, 1])
    ic.resolve_fold(rejected)
    assert ic.get_fold(rejected)["status"] == m.F_REJECTED

    space = ic.spaces.get(sid)
    space.latest_fold_id = rejected
    with pytest.raises(m.gl.vm.UserError, match="invalid parent fold"):
        ic.propose_fold(sid, candidate(), [0, 1])


def test_nonowner_cannot_write_or_cancel():
    ic, m, gl, sid = fixture()
    gl.message.sender_address = "attacker"
    with pytest.raises(m.gl.vm.UserError):
        ic.append_record(sid, m.K_FACT, "Unapproved text")
    with pytest.raises(m.gl.vm.UserError):
        ic.propose_fold(sid, candidate(), [0, 1])
    gl.message.sender_address = "owner"
    fid = ic.propose_fold(sid, candidate(), [0, 1])
    gl.message.sender_address = "attacker"
    with pytest.raises(m.gl.vm.UserError):
        ic.cancel_fold(fid)


def test_boolean_forgeries_reject_and_history_persists():
    ic, m, gl, sid = fixture()
    gl.nondet = types.SimpleNamespace(exec_prompt=lambda *a, **k: '{"equivalent":["true",true]}')
    fid = ic.propose_fold(sid, candidate(), [0, 1])
    ic.resolve_fold(fid)
    assert ic.get_fold(fid)["status"] == m.F_REJECTED
    assert len(ic.get_space(sid)["record_ids"]) == 2
