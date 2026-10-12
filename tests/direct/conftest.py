"""Direct Mode compatibility fixes for the pinned test suite on Windows.

genlayer-test 0.29.2 keeps the injected stdin file open through the VM
context. POSIX permits unlinking that open file; Windows requires the file to
be unlinked after stdin is restored. This shim keeps the suite's real loader
and VM behavior while deferring only that cleanup operation.
"""

import os
import tempfile


def pytest_configure(config):
    if os.name != "nt":
        return

    from gltest.direct import loader, vm as vm_module

    if getattr(loader, "_contextfold_windows_patch", False):
        return

    def inject_message_to_fd0(vm):
        from genlayer.py import calldata
        from genlayer.py.types import Address

        sender_addr = vm.sender
        if isinstance(sender_addr, bytes):
            sender_addr = Address(sender_addr)

        contract_addr = vm._contract_address
        if isinstance(contract_addr, bytes):
            contract_addr = Address(contract_addr)

        origin_addr = vm.origin
        if isinstance(origin_addr, bytes):
            origin_addr = Address(origin_addr)

        message_data = {
            "contract_address": contract_addr,
            "sender_address": sender_addr,
            "origin_address": origin_addr,
            "stack": [],
            "value": vm._value,
            "datetime": vm._datetime,
            "is_init": False,
            "chain_id": vm._chain_id,
            "entry_kind": 0,
            "entry_data": b"",
            "entry_stage_data": None,
        }
        encoded = calldata.encode(message_data)

        fd, path = tempfile.mkstemp()
        try:
            os.write(fd, encoded)
            os.lseek(fd, 0, os.SEEK_SET)
            vm._original_stdin_fd = os.dup(0)
            os.dup2(fd, 0)
        finally:
            os.close(fd)

        try:
            os.unlink(path)
        except PermissionError:
            paths = getattr(vm, "_contextfold_stdin_paths", [])
            paths.append(path)
            vm._contextfold_stdin_paths = paths

    original_cleanup = vm_module.VMContext._cleanup_after_deactivate

    def cleanup(self):
        try:
            original_cleanup(self)
        finally:
            for path in getattr(self, "_contextfold_stdin_paths", []):
                try:
                    os.unlink(path)
                except OSError:
                    pass
            self._contextfold_stdin_paths = []

    loader._inject_message_to_fd0 = inject_message_to_fd0
    vm_module.VMContext._cleanup_after_deactivate = cleanup
    loader._contextfold_windows_patch = True
