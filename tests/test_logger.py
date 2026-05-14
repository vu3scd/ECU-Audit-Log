import json
import os
import tempfile
import unittest

from ecu_audit.main import SecureAuditLogger, GENESIS


class TestSecureAuditLogger(unittest.TestCase):
    """Tests for the hash-chained secure audit logger."""

    def setUp(self):
        # Each test gets its own throwaway log file so tests stay isolated
        # and don't litter the working directory.
        fd, self.log_path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.remove(self.log_path)  # logger should handle a non-existent path

    def tearDown(self):
        if os.path.exists(self.log_path):
            os.remove(self.log_path)

    def _logger(self, key="test"):
        return SecureAuditLogger(secret_key=key, log_path=self.log_path)

    # --- basic behaviour ---------------------------------------------------

    def test_log_entry_signature(self):
        """An entry is created with a signature and the correct event_id."""
        logger = self._logger()
        logger.log_event(1001, 0, "TEST", "test message")
        logs = logger.export_logs()
        self.assertIn("signature", logs[0])
        self.assertEqual(logs[0]["event_id"], 1001)

    def test_empty_secret_key_rejected(self):
        """Constructing without a key is a hard error."""
        with self.assertRaises(ValueError):
            SecureAuditLogger(secret_key="", log_path=self.log_path)

    def test_first_entry_links_to_genesis(self):
        """The first entry in a fresh log chains to the GENESIS marker."""
        logger = self._logger()
        logger.log_event(1, 0, "A", "first")
        self.assertEqual(logger.export_logs()[0]["prev_sig"], GENESIS)

    def test_persistence_across_instances(self):
        """Entries written by one instance are visible to a later one."""
        self._logger().log_event(1, 0, "A", "first")
        reloaded = self._logger()
        self.assertEqual(len(reloaded.export_logs()), 1)

    def test_appends_chain_to_previous(self):
        """Each new entry's prev_sig is the previous entry's signature."""
        logger = self._logger()
        logger.log_event(1, 0, "A", "first")
        logger.log_event(2, 0, "B", "second")
        logs = logger.export_logs()
        self.assertEqual(logs[1]["prev_sig"], logs[0]["signature"])

    # --- integrity: a clean chain verifies --------------------------------

    def test_clean_chain_verifies(self):
        """An untampered chain reports no failures."""
        logger = self._logger()
        logger.log_event(1001, 2, "CAN", "unexpected arbitration id")
        logger.log_event(1002, 0, "AUTH", "login ok")
        logger.log_event(1003, 3, "MEM", "memory access error")
        self.assertEqual(logger.verify_logs(), [])

    # --- integrity: tampering is detected ---------------------------------

    def test_detects_field_edit(self):
        """Editing any field of an entry fails that entry's signature."""
        logger = self._logger()
        logger.log_event(1001, 2, "CAN", "original message")
        logger.log_event(1002, 0, "AUTH", "login ok")

        with open(self.log_path) as f:
            data = json.load(f)
        data[0]["message"] = "tampered message"
        with open(self.log_path, "w") as f:
            json.dump(data, f)

        failures = self._logger().verify_logs()
        failed_indices = [i for i, _ in failures]
        self.assertIn(0, failed_indices)

    def test_detects_deletion(self):
        """Deleting an entry breaks the following entry's chain link."""
        logger = self._logger()
        logger.log_event(1, 0, "A", "first")
        logger.log_event(2, 0, "B", "second")
        logger.log_event(3, 0, "C", "third")

        with open(self.log_path) as f:
            data = json.load(f)
        del data[1]  # remove the middle entry
        with open(self.log_path, "w") as f:
            json.dump(data, f)

        failures = self._logger().verify_logs()
        # what was entry 2 ("third") is now at index 1 with a dangling prev_sig
        self.assertEqual([i for i, _ in failures], [1])

    def test_detects_reorder(self):
        """Swapping two entries breaks the chain links."""
        logger = self._logger()
        logger.log_event(1, 0, "A", "first")
        logger.log_event(2, 0, "B", "second")

        with open(self.log_path) as f:
            data = json.load(f)
        data = [data[1], data[0]]  # swap
        with open(self.log_path, "w") as f:
            json.dump(data, f)

        failures = self._logger().verify_logs()
        self.assertTrue(len(failures) > 0)

    def test_detects_wrong_key(self):
        """A log signed with one key fails verification under another."""
        SecureAuditLogger(secret_key="right-key", log_path=self.log_path).log_event(
            1, 0, "A", "x"
        )
        failures = SecureAuditLogger(
            secret_key="wrong-key", log_path=self.log_path
        ).verify_logs()
        self.assertTrue(len(failures) > 0)

    def test_detects_appended_forgery(self):
        """An entry appended without the real key fails verification."""
        logger = self._logger("real-key")
        logger.log_event(1, 0, "A", "legit")

        # Attacker appends a plausible-looking entry but cannot sign it.
        with open(self.log_path) as f:
            data = json.load(f)
        data.append({
            "prev_sig": data[-1]["signature"],
            "timestamp": "2026-01-01T00:00:00+00:00",
            "event_id": 9999,
            "severity": 0,
            "module": "FAKE",
            "message": "forged entry",
            "signature": "deadbeef",
        })
        with open(self.log_path, "w") as f:
            json.dump(data, f)

        failures = self._logger("real-key").verify_logs()
        self.assertEqual([i for i, _ in failures], [1])


if __name__ == "__main__":
    unittest.main()
