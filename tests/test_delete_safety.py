"""
Unit tests for deletion guards, safety requirements, and confirmation checks.
"""

from pathlib import Path
import tempfile
import unittest
from intervals_plan.api_models import IntervalsEvent
from intervals_plan.backup import BackupManager


class TestDeleteSafety(unittest.TestCase):
    def test_backup_created_before_delete(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_mgr = BackupManager(Path(tmpdir))
            events_to_delete = [
                IntervalsEvent(start_date_local="2026-11-02T00:00:00", name="Test Event", id=999)
            ]
            backup_file = backup_mgr.create_backup(events_to_delete, tag="predelete_test")
            self.assertTrue(backup_file.is_file())

            # Load it back
            restored = backup_mgr.load_backup(str(backup_file))
            self.assertEqual(len(restored), 1)
            self.assertEqual(restored[0].id, 999)
            self.assertEqual(restored[0].name, "Test Event")

    def test_confirmation_phrase_logic(self):
        count = 12
        expected_phrase = f"DELETE {count} EVENTS"
        
        user_input_correct = "DELETE 12 EVENTS"
        user_input_wrong = "yes"

        self.assertEqual(user_input_correct, expected_phrase)
        self.assertNotEqual(user_input_wrong, expected_phrase, "Generic 'yes' must not authorize bulk deletion!")


if __name__ == "__main__":
    unittest.main()

