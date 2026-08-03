from __future__ import annotations

import unittest

from maturity.domain.farmability import is_blocked, karma_farmability
from maturity.domain.gates import AuthorSample, infer_gate_from_survivors
from maturity.domain.guardrails import Draft, HistoryItem, RateState, ViolationKind, check_action
from maturity.domain.phases import (
    Phase,
    ShadowbanStatus,
    WarmupSignals,
    evaluate_transition,
)
from maturity.domain.tfa_audit import CampaignContext, audit_campaign


class PhaseTests(unittest.TestCase):
    def test_setup_requires_email(self):
        s = WarmupSignals(
            verified_email=False,
            joined_target_subs=frozenset({"saas"}),
            target_subs=frozenset({"saas"}),
            per_sub_karma={},
            removals_7d=0,
            shadowban=ShadowbanStatus.CLEAN,
            account_age_days=40,
            max_age_gate_days=0,
            mention_days=0,
            spam_filter_14d=0,
            rate_limit_errors=0,
        )
        r = evaluate_transition(Phase.SETUP, s)
        self.assertFalse(r.advanced)
        self.assertIn("verified_email", r.blocked_by)

    def test_setup_advances(self):
        s = WarmupSignals(
            verified_email=True,
            joined_target_subs=frozenset({"saas"}),
            target_subs=frozenset({"saas"}),
            per_sub_karma={},
            removals_7d=0,
            shadowban=ShadowbanStatus.CLEAN,
            account_age_days=40,
            max_age_gate_days=0,
            mention_days=0,
            spam_filter_14d=0,
            rate_limit_errors=0,
        )
        r = evaluate_transition(Phase.SETUP, s)
        self.assertTrue(r.advanced)
        self.assertEqual(r.next, Phase.VALUE)


class GateTests(unittest.TestCase):
    def test_p5_not_min(self):
        authors = [AuthorSample(f"u{i}", k) for i, k in enumerate([1, 2, 3, 4, 5, 10, 20, 50, 100, 200])]
        est = infer_gate_from_survivors("saas", authors, percentile=5, min_samples=8)
        self.assertIsNotNone(est.karma_gate)
        self.assertGreaterEqual(est.karma_gate, 1)
        # min would be 1; with 10 samples P5 nearest-rank is still low but source passive
        self.assertEqual(est.source.value, "passive")


class GuardrailTests(unittest.TestCase):
    def test_shortener_blocks(self):
        r = check_action(
            Draft(text="try https://bit.ly/x now", is_promo=False),
            [],
            RateState(),
        )
        self.assertTrue(r.block)
        self.assertIn(ViolationKind.SHORTENER, r.violations)

    def test_promo_needs_disclosure(self):
        r = check_action(
            Draft(text="try this http://example.com for growth", is_promo=True, canonical_link="http://example.com"),
            [],
            RateState(),
        )
        self.assertIn(ViolationKind.MISSING_DISCLOSURE, r.violations)

    def test_flood_canonical(self):
        hist = [HistoryItem(text="a", canonical_link="https://www.example.com/app?utm=1")]
        r = check_action(
            Draft(text="b", canonical_link="https://example.com/app", is_promo=False),
            hist,
            RateState(),
        )
        self.assertIn(ViolationKind.REPOST, r.violations)


class FarmTests(unittest.TestCase):
    def test_blocklist(self):
        self.assertTrue(is_blocked("r/FreeKarma4U"))
        s = karma_farmability("FreeKarma4U", avg_comment_score=10, newbie_author_share=1, gate_ease=1)
        self.assertTrue(s.avoid)


class TfaTests(unittest.TestCase):
    def test_bought_account_fails(self):
        r = audit_campaign(
            CampaignContext(
                account_age_days=2000,
                days_since_last_activity_before_burst=400,
                product_mention=True,
                hired_upvotes=False,
                friend_support_comments=False,
                bought_aged_account=True,
                formulaic_username=False,
                plagiarized_comments=False,
                abnormal_engagement=False,
                multi_account_herd=False,
            )
        )
        self.assertFalse(r.ok)


if __name__ == "__main__":
    unittest.main()
