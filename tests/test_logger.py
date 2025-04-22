
import unittest
from ecu_audit.main import SecureAuditLogger

class TestSecureAuditLogger(unittest.TestCase):
    def test_log_entry_signature(self):
        logger = SecureAuditLogger(secret_key="test")
        logger.log_event(1001, 0, "TEST", "test message")
        logs = logger.export_logs()
        self.assertTrue("signature" in logs[0])
        self.assertEqual(logs[0]["event_id"], 1001)

if __name__ == '__main__':
    unittest.main()
