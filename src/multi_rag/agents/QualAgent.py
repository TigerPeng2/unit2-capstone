from multi_rag.agents.Agent import Agent
from multi_rag.data.loader import DocRagDataLoader
import re

QUAL_PROMPT = """
You are a RAG agent who is helping to answer questions about the technology services company
Delight. You are responsible for using the company's internal documents to answer qualitative questions.

You run in a loop of Thought, Action, PAUSE, Observation.
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run a query on the RAG database using the prefix rag
Observation will be the result of running those actions.

Example session:

Question: What aspect our benefits program might have the largest impact on employee satisfaction?
Thought: I need to query the database to learn about our employee benefits program.
Action: rag: employee benefits program
PAUSE

You will be called again with this:

Observation: <Employee Benefits Details>

You then output:

Answer: <Details about which elements of the benefits program would have the greatest impact on employee satisfaction.>
"""

class QualAgent(Agent):
    def __init__(self, client, config):
        super().__init__(client, config, QUAL_PROMPT)
        self.doc_loader = DocRagDataLoader(config)
        self.doc_loader.load_doc_data()

    def __call__(self, message):
        """Generate an answer, handling one RAG action when requested."""
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})

        rag_match = re.search(r"(?:Action:\s*)?rag\s*:\s*(.+)", result, re.IGNORECASE)
        if not rag_match:
            return result

        rag_query = rag_match.group(1).strip()
        matches = self.doc_loader.query_documents(rag_query)
        observation = self._format_observation(matches)

        self.messages.append({
            "role": "user",
            "content": f"Observation: {observation}",
        })
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    @staticmethod
    def _format_observation(matches):
        if not matches:
            return "No relevant documents were found."

        return "\n\n".join(
            f"Source: {match['metadata']['source']}\n{match['document']}"
            for match in matches
        )