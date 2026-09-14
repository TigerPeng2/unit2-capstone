from multi_rag.agents.Agent import Agent
from multi_rag.agents.QualAgent import QualAgent
from multi_rag.agents.QuantAgent import QuantAgent
import re

MANAGER_PROMPT = """
You are an orchestrator agent who is helping to answer questions about the technology services company
Delight. You have to route the query to the appropriate agent, one that has quantitative information
in the company's SQL databases and another that has qualitative information using the company's reference documents.

In order to route to the quantitative agent, prefix with QUANT, and in order to route to the qualitative agent, prefix with QUAL.

Break down the query into multiple sub-queries if needed, simply placing each new query on a new line.

Example:
How does our employee satisfaction compare to industry standards and what policies might impact this?
QUANT: How do our employees rank employee satisfaction in the employee satisfaction surveys?
QUAL: What policies of ours might impact employee satisfaction?
"""

class ManagerAgent(Agent):
    def __init__(self, client, config):
        super().__init__(client, config, system=MANAGER_PROMPT)
        self.qual_agent = QualAgent(client, config)
        self.quant_agent = QuantAgent(client, config)

    def __call__(self, message):
            """Handle user input and generate a response."""
            self.messages.append({"role": "user", "content": message})
            result = self.execute()
            self.messages.append({"role": "assistant", "content": result})

            queries = []

            for match in re.finditer(r"^\s*(QUANT|QUAL)\s*:\s*(.+?)\s*$", result, re.MULTILINE):
                prefix, subquery = match.groups()
                queries.append((prefix, subquery))

            message_history = "" # for preserving the answers of subqueries for subsequent queries

            for prefix, subquery in queries:
                if prefix == "QUANT":
                    result = self.quant_agent(message_history + subquery)
                    self.messages.append({"role": "assistant", "content": result})
                elif prefix == "QUAL":
                    result = self.qual_agent(message_history + subquery)
                    self.messages.append({"role": "assistant", "content": result})

            self.messages.append({"role": "user", "content": "What is the final answer to the initial query?"})
            result = self.execute()
            self.messages.append({"role": "assistant", "content": result})
            return result