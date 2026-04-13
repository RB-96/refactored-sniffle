import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
os.environ.setdefault("CREWAI_STORAGE_DIR", str(PROJECT_ROOT / ".crewai"))
os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")

from crewai import Agent, Crew, LLM, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool


@CrewBase
class ContentCrew:
    """Debate crew."""

    agents: list[BaseAgent]
    tasks: list[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @staticmethod
    def _research_tools() -> list:
        if not os.getenv("SERPER_API_KEY"):
            return []
        return [SerperDevTool()]

    @staticmethod
    def _pro_llm() -> LLM:
        return LLM(
            model=os.getenv("OPENAI_MODEL"),
            temperature=0.7,
            top_p=0.9,
        )

    @staticmethod
    def _con_llm() -> LLM:
        return LLM(
            model=os.getenv("OPENAI_MODEL"),
            temperature=0.7,
            top_p=0.9,
        )

    @staticmethod
    def _judge_llm() -> LLM:
        return LLM(
            model=os.getenv("ANTHROPIC_MODEL"),
            temperature=0.2,
            top_p=0.8,
            max_tokens=20000,
        )

    @agent
    def pro_debater(self) -> Agent:
        return Agent(
            config=self.agents_config["pro_debater"],  # type: ignore[index]
            verbose=True,
            allow_delegation=False,
            tools=self._research_tools(),
            llm=self._pro_llm(),
        )

    @agent
    def con_debater(self) -> Agent:
        return Agent(
            config=self.agents_config["con_debater"],  # type: ignore[index]
            verbose=True,
            allow_delegation=False,
            tools=self._research_tools(),
            llm=self._con_llm(),
        )

    @agent
    def judge(self) -> Agent:
        return Agent(
            config=self.agents_config["judge"],  # type: ignore[index]
            verbose=True,
            allow_delegation=False,
            llm=self._judge_llm(),
        )

    @task
    def pro_opening_task(self) -> Task:
        return Task(
            config=self.tasks_config["pro_opening_task"],  # type: ignore[index]
        )

    @task
    def con_opening_task(self) -> Task:
        return Task(
            config=self.tasks_config["con_opening_task"],  # type: ignore[index]
        )

    @task
    def pro_rebuttal_task(self) -> Task:
        return Task(
            config=self.tasks_config["pro_rebuttal_task"],  # type: ignore[index]
            context=[self.con_opening_task()],
        )

    @task
    def con_rebuttal_task(self) -> Task:
        return Task(
            config=self.tasks_config["con_rebuttal_task"],  # type: ignore[index]
            context=[self.pro_opening_task()],
        )

    @task
    def judging_task(self) -> Task:
        return Task(
            config=self.tasks_config["judging_task"],  # type: ignore[index]
            context=[
                self.pro_opening_task(),
                self.con_opening_task(),
                self.pro_rebuttal_task(),
                self.con_rebuttal_task(),
            ],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the debate crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
