#!/usr/bin/env python
import os
import re
from pathlib import Path

from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("CREWAI_STORAGE_DIR", str(PROJECT_ROOT / ".crewai"))
os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")

from crewai.flow import Flow, listen, start

from refactored_sniffle.crews.content_crew.content_crew import ContentCrew


DEFAULT_MOTION = "AI should replace traditional exams in higher education."


class DebateState(BaseModel):
    motion: str = ""
    pro_opening: str = ""
    con_opening: str = ""
    pro_rebuttal: str = ""
    con_rebuttal: str = ""
    verdict: str = ""
    winner: str = ""
    judge_description: str = ""
    transcript: str = ""


def resolve_motion(payload: dict | None = None) -> str:
    payload = payload or {}
    return payload.get("motion") or payload.get("topic") or DEFAULT_MOTION


def _task_output(outputs: list, index: int) -> str:
    if index >= len(outputs):
        return ""
    return getattr(outputs[index], "raw", "").strip()


def extract_winner(verdict: str) -> str:
    lowered = verdict.lower()
    if "winner: pro" in lowered or "winner - pro" in lowered:
        return "Pro"
    if "winner: con" in lowered or "winner - con" in lowered:
        return "Con"
    if "final winner: pro" in lowered:
        return "Pro"
    if "final winner: con" in lowered:
        return "Con"
    return "See judge scorecard above."


def extract_judge_description(verdict: str) -> str:
    patterns = [
        r"rationale:\s*(.+)",
        r"description:\s*(.+)",
        r"reasoning:\s*(.+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, verdict, flags=re.IGNORECASE | re.DOTALL)
        if match:
            text = match.group(1).strip()
            if text:
                return text.split("\n\n", 1)[0].strip()
    return "See the judge scorecard for the full decision."


def build_transcript(state: DebateState) -> str:
    sections = [
        "# Debate Transcript",
        "",
        "## Motion",
        state.motion,
        "",
        "## Pro Opening",
        state.pro_opening or "_No opening generated._",
        "",
        "## Con Opening",
        state.con_opening or "_No opening generated._",
        "",
        "## Pro Rebuttal",
        state.pro_rebuttal or "_No rebuttal generated._",
        "",
        "## Con Rebuttal",
        state.con_rebuttal or "_No rebuttal generated._",
        "",
        "## Judge Scorecard",
        state.verdict or "_No verdict generated._",
        "",
        "## Winner",
        state.winner or "See judge scorecard above.",
        "",
        "## Judge Description",
        state.judge_description or "See the judge scorecard for details.",
    ]
    return "\n".join(sections).strip() + "\n"


def save_transcript(transcript: str) -> Path:
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "debate.md"
    output_path.write_text(transcript, encoding="utf-8")
    return output_path


def run_debate_session(motion: str, save_output: bool = True) -> DebateState:
    result = ContentCrew().crew().kickoff(inputs={"motion": motion})
    outputs = list(getattr(result, "tasks_output", []) or [])

    state = DebateState(
        motion=motion,
        pro_opening=_task_output(outputs, 0),
        con_opening=_task_output(outputs, 1),
        pro_rebuttal=_task_output(outputs, 2),
        con_rebuttal=_task_output(outputs, 3),
        verdict=_task_output(outputs, 4) or result.raw,
    )
    state.winner = extract_winner(state.verdict)
    state.judge_description = extract_judge_description(state.verdict)
    state.transcript = build_transcript(state)

    if save_output:
        save_transcript(state.transcript)

    return state


class DebateFlow(Flow[DebateState]):

    @start()
    def prepare_motion(self, crewai_trigger_payload: dict | None = None):
        print("Preparing debate motion")
        self.state.motion = resolve_motion(crewai_trigger_payload)

        print(f"Motion: {self.state.motion}")

    @listen(prepare_motion)
    def run_debate(self):
        print(f"Running debate on: {self.state.motion}")
        self.state = run_debate_session(self.state.motion, save_output=False)

        print("Debate complete")
        return self.state.transcript

    @listen(run_debate)
    def save_debate(self):
        print("Saving debate transcript")
        output_path = save_transcript(self.state.transcript)
        print(f"Debate saved to {output_path.as_posix()}")
        return self.state.transcript


def kickoff():
    debate_flow = DebateFlow()
    return debate_flow.kickoff()


def plot():
    debate_flow = DebateFlow()
    debate_flow.plot()


def run_with_trigger():
    """
    Run the flow with trigger payload.
    """
    import json
    import sys

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError as exc:
        raise Exception("Invalid JSON payload provided as argument") from exc

    debate_flow = DebateFlow()

    try:
        return debate_flow.kickoff({"crewai_trigger_payload": trigger_payload})
    except Exception as exc:
        raise Exception(f"An error occurred while running the flow with trigger: {exc}") from exc


if __name__ == "__main__":
    kickoff()
