import json
from typing import Dict
from pathlib import Path
from nexus.utils import NexusLLM, get_logger

logger = get_logger(__name__)

class ResearchReportGenerator:
    """Generates research reports summarizing simulation runs using LLMs."""

    def __init__(self):
        self.llm = NexusLLM()

    def generate_abstract(self, sim_results: Dict) -> str:
        """Uses LLM to write an abstract summarizing the simulation results."""
        prompt = (
            "Write a formal academic abstract (around 150-250 words) summarizing the following cybersecurity "
            f"simulation results:\n{json.dumps(sim_results, indent=2)}"
        )
        return self.llm.generate(prompt)

    def generate_methodology(self, config: Dict) -> str:
        """Generates a methodology section from the simulation config."""
        prompt = (
            "Describe the methodology of the cybersecurity simulation based on this configuration. "
            "Write it in a formal, academic tone:\n"
            f"{json.dumps(config, indent=2)}"
        )
        return self.llm.generate(prompt)

    def generate_results_section(self, stats: Dict) -> str:
        """Generates the results section analyzing the provided statistics."""
        prompt = (
            "Write the results section for a research paper detailing the findings from these simulation "
            f"statistics:\n{json.dumps(stats, indent=2)}"
        )
        return self.llm.generate(prompt)

    def generate_full_report(self, sim_results: Dict, config: Dict) -> str:
        """Synthesizes all components into a full Markdown research report."""
        abstract = self.generate_abstract(sim_results)
        methodology = self.generate_methodology(config)
        
        stats = sim_results.get("stats", sim_results)
        results_sec = self.generate_results_section(stats)

        report = f"# NEXUS Cybersecurity Simulation Research Report\n\n"
        report += f"## Abstract\n{abstract}\n\n"
        report += f"## Methodology\n{methodology}\n\n"
        report += f"## Results and Findings\n{results_sec}\n\n"
        report += "## Conclusion\nThe simulation results demonstrate complex interactions between autonomous attacking and defending agents, offering vital insights into AI-driven threat landscapes."
        return report

    def save_report(self, report: str, output_path: str) -> None:
        """Saves the generated markdown report to a file."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Saved research report to {output_path}")
