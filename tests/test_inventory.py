import unittest

from forge_audit.inventory import drift, summarize


class TestDrift(unittest.TestCase):
    def test_identical(self):
        d = drift({"a": "2026-01-01T00:00:00Z"}, {"a": "2026-01-01T00:00:00Z"})
        self.assertEqual(d["missing_in_mirror"], [])
        self.assertEqual(d["missing_in_primary"], [])
        self.assertEqual(d["behind_in_mirror"], {})

    def test_missing_in_mirror(self):
        d = drift({"a": "t", "b": "t"}, {"a": "t"})
        self.assertEqual(d["missing_in_mirror"], ["b"])

    def test_missing_in_primary(self):
        d = drift({"a": "t"}, {"a": "t", "extra": "t"})
        self.assertEqual(d["missing_in_primary"], ["extra"])

    def test_behind(self):
        d = drift({"a": "2026-02-01T00:00:00Z"}, {"a": "2026-01-01T00:00:00Z"})
        self.assertIn("a", d["behind_in_mirror"])

    def test_summarize_mentions_counts(self):
        s = summarize(drift({"a": "t"}, {"a": "t", "b": "t"}))
        self.assertIn("missing_in_primary=1", s)


if __name__ == "__main__":
    unittest.main()
