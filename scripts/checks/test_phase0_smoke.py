"""The compatibility spike must prove native Qt, bounded spawn and CPU forward."""

import json
from pathlib import Path
import subprocess
import sys
import unittest


class Phase0SmokeTest(unittest.TestCase):
    def test_real_process_reports_native_event_loop_and_both_model_shapes(self):
        script = Path(__file__).with_name("phase0_smoke.py")
        self.check_diagnostic([sys.executable, str(script)], frozen=False)

    def test_frozen_process_reports_native_event_loop_and_both_model_shapes(self):
        executable = (Path(__file__).resolve().parents[2] /
                      "artifacts/S01/dist/phase0_smoke/phase0_smoke.exe")
        self.check_diagnostic([str(executable)], frozen=True)

    def check_diagnostic(self, command, *, frozen):
        result = subprocess.run(
            command, capture_output=True, text=True,
            encoding="utf-8", timeout=120,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["frozen"], frozen)
        self.assertEqual(report["qt"]["platform"], "windows")
        self.assertTrue(report["qt"]["window_exposed"])
        self.assertTrue(report["qt"]["timer_fired"])
        self.assertEqual(report["worker_exitcode"], 0)
        self.assertNotEqual(report["parent_pid"], report["worker"]["pid"])
        self.assertEqual(report["worker"]["device"], "cpu")
        self.assertEqual(report["worker"]["efficientnet_b0"], [1, 10])
        self.assertEqual(report["worker"]["resnet50"], [1, 10])
        self.assertTrue(report["worker"]["finite"])
        self.assertFalse(report["pretrained_weights_loaded"])
        self.assertFalse(report["training_performed"])


if __name__ == "__main__":
    unittest.main()
