from __future__ import annotations

import os
import unittest


class CgvoApiRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ["GANN_ASTRO_API_TOKEN"] = "cgvo-test-token-20260821"
        os.environ["GANN_ASTRO_MT5_AUTOCONNECT"] = "0"
        os.environ["GANN_ASTRO_SHADOW_AUTOSTART"] = "0"
        os.environ["GANN_ASTRO_CANDLE_SHADOW_AUTOSTART"] = "0"
        os.environ["GANN_ASTRO_REFRESH_AUTOSTART"] = "0"
        from server import app
        cls.app = app
        cls.app.config.update(TESTING=True, PROPAGATE_EXCEPTIONS=False)

    def setUp(self) -> None:
        self.client = self.app.test_client()
        self.headers = {"X-Gann-Astro-Token": "cgvo-test-token-20260821"}

    def test_cgvo_status_and_workbench_are_json_read_only(self) -> None:
        status = self.client.get("/api/experiments/cgvo/status", headers=self.headers)
        self.assertEqual(status.status_code, 200)
        self.assertTrue(status.content_type.startswith("application/json"))
        self.assertFalse(status.get_json()["status"]["guardrails"]["executionAllowed"])
        self.assertEqual(status.get_json()["status"]["milestone"], "CGVO-G3-S1-R1")
        self.assertEqual(status.get_json()["status"]["milestones"], {
            "current": "CGVO-G3-S1-R1", "astronomy": "CGVO-S1B-R1", "geography": "CGVO-G2-R1A",
            "siteVisibility": "CGVO-G3-D1", "sourceComposition": "CGVO-G3-S1-R1",
        })
        self.assertEqual(status.get_json()["status"]["sourceCompositionAdjudication"]["chapterVtoXivReferenceStatus"], "SOURCE_CLOSED_ROOT_KURMA_REFERENCE")
        self.assertFalse(status.get_json()["status"]["s1bSourceAudit"]["absoluteFrameAudit"]["auditProfilesRuntimeSelectable"])
        workbench = self.client.get(
            "/api/experiments/cgvo/workbench?eventType=SOLAR&globalMaxUtc=2027-08-02T10:06:41Z&localityId=UJJAIN&label=Ujjain&latitude=23.1765&longitude=75.7885&elevationM=0&timezone=Asia%2FKolkata",
            headers=self.headers,
        )
        self.assertEqual(workbench.status_code, 200)
        self.assertTrue(workbench.content_type.startswith("application/json"))
        payload = workbench.get_json()
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["workbench"]["event"]["modernAstronomy"]["localEclipseType"], "PARTIAL")
        self.assertEqual(payload["workbench"]["event"]["sourceAdapters"]["varahamihiraFrame"]["absoluteFrameStatus"], "NULL")
        self.assertFalse(payload["workbench"]["guardrails"]["marketDirectionInferred"])

    def test_s1a_workbench_profile_selection_and_invalid_profile_are_json(self) -> None:
        query = (
            "eventType=SOLAR&globalMaxUtc=2027-08-02T10:06:41Z&localityId=UJJAIN&label=Ujjain"
            "&latitude=23.1765&longitude=75.7885&elevationM=0&timezone=Asia%2FKolkata"
        )
        selected = self.client.get(
            "/api/experiments/cgvo/workbench?" + query + "&absoluteFrameProfileId=VARAHAMIHIRA_CHITRA_180_RECONSTRUCTION_V1",
            headers=self.headers,
        )
        self.assertEqual(selected.status_code, 200)
        self.assertTrue(selected.content_type.startswith("application/json"))
        adapters = selected.get_json()["workbench"]["event"]["sourceAdapters"]
        self.assertEqual(adapters["varahamihiraFrame"]["selectedProfileId"], "VARAHAMIHIRA_CHITRA_180_RECONSTRUCTION_V1")
        self.assertEqual(adapters["varahamihiraAspect"]["effectMagnitudeMultiplier"], None)
        self.assertEqual(adapters["varahamihiraAspect"]["auditGeometryAtMaximum"]["role"], "GEOMETRY_SNAPSHOT_ONLY")
        self.assertIsNone(adapters["varahamihiraAspect"]["sourcePhaseActivation"]["effectActivated"])
        rejected = self.client.get(
            "/api/experiments/cgvo/workbench?" + query + "&absoluteFrameProfileId=RAMAN",
            headers=self.headers,
        )
        self.assertEqual(rejected.status_code, 400)
        self.assertTrue(rejected.content_type.startswith("application/json"))
        self.assertNotIn("<!doctype", rejected.get_data(as_text=True).lower())
        self.assertIn("absoluteFrameProfileId", rejected.get_json()["error"])

    def test_invalid_locality_is_typed_json_error(self) -> None:
        response = self.client.get(
            "/api/experiments/cgvo/eclipse-search?eventType=SOLAR&startUtc=2027-01-01T00:00:00Z&endUtc=2028-01-01T00:00:00Z&limit=1",
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content_type.startswith("application/json"))
        bad = self.client.get(
            "/api/experiments/cgvo/workbench?eventType=SOLAR&globalMaxUtc=2027-08-02T10:06:41Z&latitude=91&longitude=0&timezone=UTC",
            headers=self.headers,
        )
        self.assertEqual(bad.status_code, 400)
        self.assertTrue(bad.content_type.startswith("application/json"))
        self.assertNotIn("<!doctype", bad.get_data(as_text=True).lower())
        self.assertIn("latitude", bad.get_json()["error"])

    def test_causal_event_url_is_checked_against_reconstructed_event(self) -> None:
        search = self.client.get(
            "/api/experiments/cgvo/eclipse-search?eventType=SOLAR&startUtc=2027-01-01T00:00:00Z&endUtc=2028-01-01T00:00:00Z&limit=24",
            headers=self.headers,
        ).get_json()["search"]
        event = next(item for item in search["events"] if item["astronomyEventIdentity"]["globalMaxUtc"].startswith("2027-08-02"))
        query = "eventType=SOLAR&globalMaxSwissUt={}&localityId=UJJAIN&label=Ujjain&latitude=23.1765&longitude=75.7885&elevationM=0&timezone=Asia%2FKolkata".format(event["astronomyEventIdentity"]["globalMaxSwissUt"])
        valid = self.client.get(f"/api/experiments/cgvo/event/{event['causalEventId']}/local-circumstances?{query}", headers=self.headers)
        self.assertEqual(valid.status_code, 200)
        self.assertTrue(valid.content_type.startswith("application/json"))
        self.assertEqual(valid.get_json()["circumstances"]["event"]["causalEventId"], event["causalEventId"])
        wrong = self.client.get(f"/api/experiments/cgvo/event/CGVO-SOLAR-WRONG/local-circumstances?{query}", headers=self.headers)
        self.assertEqual(wrong.status_code, 400)
        self.assertTrue(wrong.content_type.startswith("application/json"))
        self.assertNotIn("<!doctype", wrong.get_data(as_text=True).lower())
        self.assertIn("causalEventId", wrong.get_json()["error"])

    def test_g1_historical_gazetteer_route_is_read_only_json(self) -> None:
        response = self.client.get("/api/experiments/cgvo/historical-gazetteer", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content_type.startswith("application/json"))
        payload = response.get_json()
        self.assertTrue(payload["ok"])
        gazetteer = payload["gazetteer"]
        self.assertEqual(gazetteer["contract"], "CGVO_HISTORICAL_GEOGRAPHY_GAZETTEER_V1")
        self.assertEqual(gazetteer["schemaVersion"], 2)
        self.assertEqual(gazetteer["startingMaster"], "34659956d1de1ed44e307d0788938e67ac23f7bf")
        self.assertEqual(gazetteer["summary"]["totalSourceNames"], 308)
        self.assertFalse(gazetteer["guardrails"]["marketDirectionInferred"])
        self.assertFalse(gazetteer["guardrails"]["executionAllowed"])
        self.assertNotIn("<html", response.get_data(as_text=True).lower())

    def test_g2_research_footprints_route_is_read_only_json(self) -> None:
        response = self.client.get("/api/experiments/cgvo/historical-gazetteer/research-footprints", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content_type.startswith("application/json"))
        self.assertNotIn("<!doctype", response.get_data(as_text=True).lower())
        payload = response.get_json()
        self.assertTrue(payload["ok"])
        footprints = payload["footprints"]
        self.assertEqual(footprints["contract"], "CGVO_HISTORICAL_GEOGRAPHY_RESEARCH_FOOTPRINTS_V2")
        self.assertEqual(footprints["summary"]["footprintCount"], 12)
        self.assertEqual(footprints["summary"]["coordinateBearingFootprintCount"], 1)
        self.assertEqual(footprints["siteEvidence"]["contract"], "CGVO_G2_R1_HISTORICAL_SITE_COORDINATE_EVIDENCE_V1")
        self.assertFalse(footprints["guardrails"]["downstreamIntersectionAuthorized"])
        self.assertFalse(footprints["guardrails"]["marketUseAllowed"])
        self.assertFalse(footprints["guardrails"]["executionAllowed"])

    def test_g3_d1_site_visibility_audit_is_json_only_and_fail_closed(self) -> None:
        search = self.client.get(
            "/api/experiments/cgvo/eclipse-search?eventType=SOLAR&startUtc=2027-01-01T00:00:00Z&endUtc=2028-01-01T00:00:00Z&limit=24",
            headers=self.headers,
        ).get_json()["search"]
        event = next(item for item in search["events"] if item["astronomyEventIdentity"]["globalMaxUtc"].startswith("2027-08-02"))
        payload = {
            "eventId": event["causalEventId"],
            "eventType": event["astronomyEventIdentity"]["eventType"],
            "globalMaxSwissUt": event["astronomyEventIdentity"]["globalMaxSwissUt"],
            "siteEvidenceId": "G2R1_TAKSASILA_TAXILA_SITE_01",
        }
        response = self.client.post(
            "/api/experiments/cgvo/historical-gazetteer/site-visibility-audit",
            json=payload,
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content_type.startswith("application/json"))
        self.assertNotIn("<!doctype", response.get_data(as_text=True).lower())
        audit = response.get_json()["audit"]
        self.assertEqual(audit["event"]["causalEventId"], event["causalEventId"])
        self.assertEqual(audit["siteAnchor"]["label"], "Taxila research site anchor")
        self.assertIsNone(audit["sourceEffectActivation"])
        self.assertIsNone(audit["regionVisibility"])
        self.assertEqual(audit["sourceCompositionAdjudication"]["siteVisibilityInferenceStatus"], "SITE_ONLY")
        self.assertIsNone(audit["sourceCompositionAdjudication"]["regionVisibility"])
        self.assertIsNone(audit["sourceCompositionAdjudication"]["sourceEffectActivation"])
        self.assertFalse(audit["guardrails"]["executionAllowed"])
        for rejected_payload, code in (
            ({**payload, "siteEvidenceId": "G2R1_MATHURAKA_MATHURA_SITE_01"}, "SITE_ANCHOR_NOT_COORDINATE_BEARING"),
            ({**payload, "eventId": "CGVO-SOLAR-WRONG"}, "EVENT_CAUSAL_ID_MISMATCH"),
            ({**payload, "resultScope": "REGION"}, "REGION_EXTRAPOLATION_PROHIBITED"),
            ({**payload, "includeChapterVEffect": True}, "SOURCE_EFFECT_NOT_AUTHORIZED"),
            ({**payload, "includeGandharaRegion": True}, "REGION_EXTRAPOLATION_PROHIBITED"),
        ):
            with self.subTest(code=code):
                rejected = self.client.post(
                    "/api/experiments/cgvo/historical-gazetteer/site-visibility-audit",
                    json=rejected_payload,
                    headers=self.headers,
                )
                self.assertEqual(rejected.status_code, 400)
                self.assertTrue(rejected.content_type.startswith("application/json"))
                self.assertNotIn("<!doctype", rejected.get_data(as_text=True).lower())
                self.assertEqual(rejected.get_json()["error"]["code"], code)


if __name__ == "__main__":
    unittest.main()
