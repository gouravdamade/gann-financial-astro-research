from __future__ import annotations

import unittest

from companion_capabilities import CONTRACT, build_companion_capabilities


class CompanionCapabilitiesTests(unittest.TestCase):
    def test_contract_keeps_python_private_and_execution_locked(self) -> None:
        payload = build_companion_capabilities()
        self.assertEqual(payload["contract"], CONTRACT)
        self.assertTrue(payload["transport"]["gatewayRequired"])
        self.assertFalse(payload["transport"]["directPythonExposureAllowed"])
        self.assertTrue(payload["transport"]["tlsRequired"])
        self.assertTrue(payload["transport"]["gatewayImplemented"])
        self.assertTrue(payload["transport"]["encryptedPairingEnvelope"])
        self.assertTrue(payload["transport"]["certificatePinning"])
        self.assertFalse(payload["features"]["orderPlacement"])
        self.assertFalse(payload["features"]["offlineCache"])
        self.assertTrue(payload["features"]["boundedWebSocketStreaming"])
        self.assertFalse(payload["guardrails"]["executionAllowed"])
        self.assertEqual(payload["guardrails"]["sessionPersistence"], "memory_only")

    def test_windows_remains_authoritative_for_research_evidence(self) -> None:
        payload = build_companion_capabilities()
        topology = payload["computeTopology"]
        self.assertEqual(topology["authoritativeEvidence"], "windows")
        self.assertIn("chart_rendering", topology["android"])
        self.assertIn("mt5", topology["windows"])
        self.assertIn("market_synthesis", topology["windows"])


if __name__ == "__main__":
    unittest.main()
