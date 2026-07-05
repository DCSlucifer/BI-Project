import subprocess
import sys
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_MINING = ROOT / "DataMining"
OUT = DATA_MINING / "outputs"


class DataMiningOutputTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        result = subprocess.run(
            [sys.executable, "data_mining.py"],
            cwd=DATA_MINING,
            text=True,
            capture_output=True,
            timeout=120,
        )
        cls.stdout = result.stdout
        cls.stderr = result.stderr
        cls.returncode = result.returncode

    def test_script_runs_successfully(self):
        self.assertEqual(
            self.returncode,
            0,
            msg=f"stdout:\n{self.stdout}\nstderr:\n{self.stderr}",
        )

    def test_professional_report_artifacts_exist(self):
        expected = [
            "class_balance.png",
            "confusion_matrix.png",
            "decision_tree.png",
            "feature_importance.png",
            "loss_rules.png",
            "elbow_silhouette.png",
            "rfm_profile.png",
            "segments.png",
            "decision_rules.csv",
            "loss_rules.csv",
            "rfm_profile.csv",
            "rfm_customers.csv",
            "model_summary.txt",
        ]
        missing = [name for name in expected if not (OUT / name).exists()]
        self.assertEqual([], missing)

    def test_loss_rules_are_validated_on_test_set(self):
        rules = pd.read_csv(OUT / "loss_rules.csv")
        required_cols = {
            "rule",
            "predicted_class",
            "support_test",
            "correct_test",
            "incorrect_test",
            "precision",
        }
        self.assertTrue(required_cols.issubset(rules.columns))
        self.assertGreaterEqual(len(rules), 1)

        top_rule = rules.sort_values(
            ["precision", "support_test"], ascending=[False, False]
        ).iloc[0]
        self.assertEqual("Loss", top_rule["predicted_class"])
        self.assertGreaterEqual(top_rule["support_test"], 30)
        self.assertGreaterEqual(top_rule["precision"], 0.9)
        self.assertIn("Discount", top_rule["rule"])

    def test_rfm_cluster_names_stay_stable(self):
        profile = pd.read_csv(OUT / "rfm_profile.csv")
        expected = {
            0: "Trung thanh / Active",
            1: "Pho thong / Trung binh",
            2: "VIP / Champions",
            3: "Roi bo / Lost",
        }
        actual = dict(zip(profile["Cluster"], profile["SegmentName"]))
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
