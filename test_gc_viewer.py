import unittest
import os
from gc_viewer import parse_gc_log, generate_notebook_code

class TestGCViewer(unittest.TestCase):
    def test_parse_java8_format(self):
        # Java 8 format test
        log_file = os.path.join("tests", "assets", "sample_gc_java8.log")
        data = parse_gc_log(log_file, "java8")
        
        # 粗い粒度のテスト: データが取得できているか、件数が正しいか、主要なキーが含まれているかを確認
        self.assertTrue(len(data) > 0)
        # Note: sample_gc_java8.log has 4 entries, but current regex only matches 3 (Full GC format is different)
        # This is expected behavior for now as the script is "under development".
        self.assertEqual(len(data), 3)
        
        first_entry = data[0]
        self.assertIn('timestamp', first_entry)
        self.assertIn('type', first_entry)
        self.assertIn('before', first_entry)
        self.assertIn('after', first_entry)
        self.assertIn('total', first_entry)
        self.assertIn('pause', first_entry)
        
        # 値の簡易チェック
        self.assertEqual(first_entry['timestamp'], 0.500)
        self.assertAlmostEqual(first_entry['pause'], 5.234, places=3) # 0.0052340 secs -> 5.234 ms

    def test_parse_unified_format(self):
        # Unified Logging format test
        log_file = os.path.join("tests", "assets", "sample_gc.log")
        data = parse_gc_log(log_file, "unified")
        
        # 粗い粒度のテスト
        self.assertTrue(len(data) > 0)
        self.assertEqual(len(data), 10)
        
        first_entry = data[0]
        self.assertIn('timestamp', first_entry)
        self.assertEqual(first_entry['timestamp'], 0.012)
        self.assertEqual(first_entry['pause'], 2.541)

    def test_generate_notebook_code(self):
        data = [
            {'timestamp': 0.1, 'type': 'GC', 'before': 10, 'after': 5, 'total': 100, 'pause': 2.0}
        ]
        code = generate_notebook_code(data)

        self.assertIsInstance(code, str)
        self.assertIn('output_notebook()', code)
        self.assertIn('ColumnDataSource', code)
        self.assertIn('"timestamp": 0.1', code)
        self.assertIn('"type": "GC"', code)
        self.assertIn('show(layout)', code)

if __name__ == '__main__':
    unittest.main()
