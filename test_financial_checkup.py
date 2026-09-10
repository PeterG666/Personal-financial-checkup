"""Exercise the submit workflow and financial edge cases through Streamlit."""
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


class FinancialCheckupTest(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(Path(__file__).with_name("financial_checkup_web.py"))).run()

    def submit(self):
        self.app.button[0].click().run()
        self.assertFalse(self.app.exception)

    def values(self):
        return {metric.label: metric.value for metric in self.app.metric}

    def test_report_only_after_submit_and_snapshot_retained(self):
        self.assertFalse(self.app.exception)
        self.assertEqual(len(self.app.metric), 0)
        self.submit()
        self.assertEqual(self.values()["每月花完、还完后剩下的钱"], "¥3,000")
        self.assertEqual(self.values()["扣掉欠款后，还剩多少家底"], "还没填欠款")
        self.app.number_input[0].set_value(20000).run()
        self.assertEqual(self.values()["每月花完、还完后剩下的钱"], "¥3,000")
        self.submit()
        self.assertEqual(self.values()["每月花完、还完后剩下的钱"], "¥8,000")

    def test_impossible_savings_blocks_report(self):
        self.submit()
        self.app.number_input[2].set_value(4000)
        self.submit()
        self.assertTrue(self.app.error)
        self.assertEqual(len(self.app.metric), 0)
        self.app.number_input[2].set_value(3000)
        self.submit()
        self.assertEqual(len(self.app.error), 0)
        self.assertEqual(len(self.app.metric), 8)

    def test_zero_income_with_debt_is_not_safe(self):
        self.app.number_input[0].set_value(0)
        self.app.number_input[2].set_value(0)
        self.submit()
        self.assertEqual(self.values()["每月花完、还完后剩下的钱"], "¥-12,000")
        self.assertIn("暂无收入基数", [metric.value for metric in self.app.metric])
        self.assertTrue(any("summary-card risk" in item.value for item in self.app.markdown))

    def test_zero_data_no_division_error(self):
        for item in self.app.number_input:
            item.set_value(0)
        self.submit()
        self.assertIn("暂无资产", [metric.value for metric in self.app.metric])
        self.assertIn("暂不可计算", [metric.value for metric in self.app.metric])

    def test_negative_net_worth_and_target_selection(self):
        self.app.number_input[7].set_value(100000)
        self.app.selectbox[0].set_value(9)
        self.submit()
        self.assertEqual(self.values()["扣掉欠款后，还剩多少家底"], "¥-20,000")
        self.assertTrue(any("summary-card risk" in item.value for item in self.app.markdown))
        self.assertTrue(any("尚差约 ¥78,000" in item.value for item in self.app.markdown))

    def test_contradictory_debt(self):
        self.app.number_input[7].set_value(0)
        self.submit()
        self.assertTrue(self.app.error)


if __name__ == "__main__":
    unittest.main()
