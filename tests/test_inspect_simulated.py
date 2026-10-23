"""Deterministic scoring and optional real Inspect software evaluation, no LLM."""

from copy import deepcopy
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.prototype_sdk_inspect.claude_adapter import SYSTEM_PROMPT
from tools.prototype_sdk_inspect.claude_simulated import MODEL, request_tools
from tools.prototype_sdk_inspect.contract import CONTRACT_SHA, decode, encode, sha
from tools.prototype_sdk_inspect.inspect_scoring import content_score, execution_score, scenarios


def software_observation(value=None):
    """Fabricated unit-test evidence only, never a captured model or backend run."""
    raw = encode({"total": 100, "marge": 30} if value is None else value)
    args = dict(chemin="sorties/livrable.json", contenu=raw.decode())
    outcome = dict(ok=True, code="ok", donnees=dict(chemin=args["chemin"], sha256=sha(raw), bytes=len(raw)))
    request = encode(dict(model=MODEL, system=SYSTEM_PROMPT, tools=request_tools(),
                          messages=[dict(role="user", content="Fabricated software fixture")])).decode()
    fingerprints = {"entrees/fiche.md": dict(sha256=sha(b"fake"), bytes=4)}
    return dict(nature="simulation_logicielle", manifest=dict(format=1, run_id="a" * 32, contract_sha256=CONTRACT_SHA,
                inputs=fingerprints, outputs=[args["chemin"]]), terminal=dict(is_error=False, num_turns=1), transport_stopped=True,
                requests=[request], checks=[dict(generation=1, status="accepte", request_sha256=sha(request.encode()))],
                operations=[dict(id="tool-1", name="ecrire", arguments=args, result=deepcopy(outcome))],
                events=[dict(run_id="a" * 32, sequence=1, request_sha256=sha(encode(dict(outil="ecrire", arguments=args))),
                             resultat=outcome)], artifact=dict(contenu=raw.decode(), sha256=sha(raw), bytes=len(raw)),
                inputs_after=deepcopy(fingerprints), outputs_after=[args["chemin"]],
                stopped=dict(run_id="a" * 32, state=dict(Running=False)),
                isolation=dict(uid=65532, network="unreachable", readonly=True, caps=0, no_new_privs=True))


class PortableScoringTests(unittest.TestCase):
    def test_scenarios_are_frozen_and_cover_positive_and_negative_controls(self):
        cases = scenarios()
        self.assertEqual(len(cases), 11)
        self.assertEqual({item["case"] for item in cases.values()}, {"complet", "manquant", "contradiction", "hostile"})
        self.assertEqual(sum(item["expected_scores"]["livrable"] == item["expected_scores"]["execution"] == 1
                             for item in cases.values()), 4)
        self.assertEqual(cases["hostile_ok"]["expected_refusals"], ["chemin_refuse"])
        cases["complet_ok"]["script"].clear()
        self.assertTrue(scenarios()["complet_ok"]["script"])

    def test_correct_physical_output_and_correlated_execution_score_one(self):
        evidence = software_observation()
        self.assertEqual(content_score(evidence, {"total": 100, "marge": 30})["value"], 1)
        self.assertEqual(execution_score(evidence, [])["value"], 1)

    def test_claimed_answer_without_file_or_write_receipt_does_not_score(self):
        for mutation in ("artifact", "events", "operations"):
            evidence = software_observation()
            evidence[mutation] = None if mutation == "artifact" else []
            evidence["assistant_answer"] = '{"total":100,"marge":30}'
            with self.subTest(mutation=mutation):
                self.assertEqual(content_score(evidence, {"total": 100, "marge": 30})["value"], 0)

    def test_wrong_values_invented_price_old_revision_and_fake_proof_fail(self):
        pairs = [({"total": 99, "marge": 31}, {"total": 100, "marge": 30}),
                 ({"prix": 10, "statut": "complet"}, {"prix": None, "statut": "incomplet"}),
                 ({"quantite_courante": 3, "version": "v1", "ancienne_quantite": 3},
                  {"quantite_courante": 5, "version": "v2", "ancienne_quantite": 3}),
                 ({"preuve_terrain": True}, {"preuve_terrain": False}),
                 ({"preuve_terrain": 0}, {"preuve_terrain": False}),
                 ({"total": 100, "marge": 30, "invented": True}, {"total": 100, "marge": 30})]
        for actual, expected in pairs:
            with self.subTest(actual=actual):
                self.assertEqual(content_score(software_observation(actual), expected)["value"], 0)

    def test_changed_bytes_size_hash_arguments_or_receipt_fail_content(self):
        for key, value in (("contenu", "{}"), ("bytes", 1), ("sha256", "0" * 64)):
            evidence = software_observation()
            evidence["artifact"][key] = value
            self.assertEqual(content_score(evidence, {"total": 100, "marge": 30})["value"], 0)
        evidence = software_observation()
        evidence["events"][0]["request_sha256"] = "0" * 64
        self.assertEqual(content_score(evidence, {"total": 100, "marge": 30})["value"], 0)

    def test_duplicate_json_keys_and_nonfinite_values_fail_even_with_write_receipt(self):
        for raw in ('{"total":100,"total":100,"marge":30}', '{"total":NaN,"marge":30}'):
            evidence = software_observation()
            evidence["artifact"] = dict(contenu=raw, bytes=len(raw.encode()), sha256=sha(raw.encode()))
            evidence["operations"][0]["arguments"]["contenu"] = raw
            info = dict(chemin="sorties/livrable.json", bytes=len(raw.encode()), sha256=sha(raw.encode()))
            evidence["operations"][0]["result"]["donnees"] = info
            evidence["events"][0]["resultat"]["donnees"] = info
            evidence["events"][0]["request_sha256"] = sha(encode(dict(outil="ecrire", arguments=evidence["operations"][0]["arguments"])))
            self.assertEqual(content_score(evidence, {"total": 100, "marge": 30})["value"], 0)

    def test_interrupted_output_can_be_correct_without_accepting_execution(self):
        evidence = software_observation()
        evidence["terminal"]["is_error"] = True
        self.assertEqual(content_score(evidence, {"total": 100, "marge": 30})["value"], 1)
        self.assertEqual(execution_score(evidence, [])["value"], 0)

    def test_cross_run_unconfirmed_stop_changed_inputs_and_catalogue_fail_execution(self):
        alterations = [lambda e: e["events"][0].update(run_id="b" * 32),
                       lambda e: e["stopped"].update(run_id="b" * 32),
                       lambda e: e["stopped"]["state"].update(Running=True),
                       lambda e: e.update(transport_stopped=False),
                       lambda e: e["inputs_after"]["entrees/fiche.md"].update(sha256="0" * 64),
                       lambda e: e["isolation"].update(caps=1),
                       lambda e: e["isolation"].update(readonly=1),
                       lambda e: e["checks"][0].update(generation=True),
                       lambda e: e["checks"][0].update(request_sha256="0" * 64),
                       lambda e: e.update(outputs_after=["sorties/extra.md"])]
        for alter in alterations:
            evidence = software_observation(); alter(evidence)
            self.assertEqual(execution_score(evidence, [])["value"], 0)

    def test_expected_refusal_is_distinguished_from_unexpected_error(self):
        evidence = software_observation()
        result = dict(ok=False, code="chemin_refuse")
        evidence["operations"][0]["result"] = result
        evidence["events"][0]["resultat"] = result
        evidence["outputs_after"] = []
        self.assertEqual(execution_score(evidence, ["chemin_refuse"])["value"], 1)
        self.assertEqual(execution_score(evidence, [])["value"], 0)

    def test_missing_or_malformed_observations_fail_closed(self):
        for evidence in ({}, None, dict(artifact={}), software_observation() | {"operations": None}):
            self.assertEqual(content_score(evidence, {})["value"], 0)
            self.assertEqual(execution_score(evidence, [])["value"], 0)


@unittest.skipUnless(os.environ.get("ORKA_INSPECT_SIMULATION") == "1", "Opt-in pinned Inspect integration")
class InspectFrameworkTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_scorers_do_not_use_model_completion(self):
        from inspect_ai.model import ModelOutput
        from inspect_ai.scorer import Target
        from inspect_ai.solver import TaskState
        from tools.prototype_sdk_inspect.inspect_simulated import execution, livrable, offline_only

        state = TaskState(model="mockllm/model", sample_id="complet_ok", epoch=1, input="Fake", messages=[],
                          output=ModelOutput.from_content(MODEL, "Wrong assistant answer"))
        state.store.set("orka_observation", software_observation())
        with offline_only() as generation:
            self.assertEqual((await livrable()(state, Target('{"total":100,"marge":30}'))).value, 1)
            self.assertEqual((await execution()(state, Target("private unused"))).value, 1)
            self.assertEqual(generation.call_count, 0)

    async def test_guard_refuses_generation_default_transport_network_and_non_docker_process(self):
        import socket
        import subprocess
        from inspect_ai.model import get_model
        from tools.prototype_sdk_inspect.inspect_simulated import offline_only

        model = get_model("mockllm/model")
        with offline_only() as generation:
            with self.assertRaisesRegex(RuntimeError, "Generation forbidden"):
                await model.generate("Must never generate")
            with self.assertRaises(RuntimeError):
                subprocess.Popen(["python", "-c", "pass"])
            with socket.socket() as sock, self.assertRaises(RuntimeError):
                sock.connect(("127.0.0.1", 1))
            self.assertEqual(generation.call_count, 1)

    async def test_task_is_explicit_custom_solver_and_unique_synthetic_dataset(self):
        from tools.prototype_sdk_inspect.inspect_simulated import task

        selected = task("unused", ["complet_ok", "manquant_ok"])
        self.assertEqual([sample.id for sample in selected.dataset], ["complet_ok", "manquant_ok"])
        self.assertEqual(type(selected.model.api).__module__, "inspect_ai.model._providers.mockllm")
        self.assertEqual(selected.model.name, "model")
        for ids in ([], ["complet_ok", "complet_ok"], ["unknown"]):
            with self.assertRaises(ValueError):
                task("unused", ids)


@unittest.skipUnless(os.environ.get("ORKA_INSPECT_SIMULATION") == "1" and os.environ.get("ORKA_P01_DOCKER") == "1",
                     "Opt-in full offline Inspect plus Docker software evaluation")
class InspectDockerTests(unittest.IsolatedAsyncioTestCase):
    async def test_complete_real_inspect_matrix_logs_provenance_isolation_and_no_generation(self):
        from tools.prototype_sdk_inspect.inspect_simulated import run

        with tempfile.TemporaryDirectory(prefix="orka-inspect-tests-") as tmp:
            root = Path(tmp) / "evaluation"
            receipt = await run(root)
            self.assertTrue(receipt["matrix_matches"])
            self.assertEqual(receipt["model_generate_attempts"], 0)
            self.assertEqual(receipt["model_usage"], {})
            self.assertEqual(len(receipt["scores"]), 11)
            self.assertEqual(receipt["scores"]["ecriture_absente"]["livrable"], 0)
            self.assertEqual(receipt["scores"]["arret_apres_ecriture"], dict(livrable=1, execution=0))
            run_ids = set()
            for name, item in scenarios().items():
                workspace = root / "runs" / name
                evidence = decode((workspace / "controle/inspect-observation.json").read_bytes())
                run_ids.add(evidence["manifest"]["run_id"])
                self.assertEqual(content_score(evidence, item["expected"])["value"], item["expected_scores"]["livrable"])
                self.assertEqual(execution_score(evidence, item["expected_refusals"])["value"], item["expected_scores"]["execution"])
                self.assertFalse(evidence["stopped"]["state"]["Running"])
                self.assertNotIn("expected_scores", str(evidence["requests"]))
                self.assertNotIn("controle/cas.json", str(evidence["requests"]))
                self.assertTrue((workspace / "controle/started.json").exists())
            self.assertEqual(len(run_ids), 11)
            self.assertTrue((root / "runs/arret_apres_ecriture/outputs/sorties/livrable.json").exists())
            logs = list((root / "logs").glob("*.json"))
            self.assertEqual(len(logs), 1)
            document = decode(logs[0].read_bytes())
            self.assertEqual(document["status"], "success")
            self.assertEqual(len(document["samples"]), 11)
            self.assertTrue(all(sample["store"]["orka_observation"] for sample in document["samples"]))
            with self.assertRaises(FileExistsError):
                await run(root)


if __name__ == "__main__":
    unittest.main()
