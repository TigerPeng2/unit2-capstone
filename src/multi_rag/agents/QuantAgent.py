from multi_rag.agents.Agent import Agent
from multi_rag.data.loader import SQLDataLoader
import re

QUANT_PROMPT = """
You are an agent who is helping to answer questions about the technology services company
Delight. You are responsible for using the company's internal database. Always check the schema 
of the table before you attempt to query it.

You run in a loop of Thought, Action, PAUSE, Observation.
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run a query on the SQLite3 Database using the prefix sql: or get more information on 
a given table's schema using the schema: prefix
Observation will be the result of running those actions.

Example session:
The tables that are available are revenue, sales records, employee expenses, and employee satisfaction .
Question: What have sales performance trends looked like over the last 6 months?
Thought: I have access to a revenue table, I should query this table to determine the sales performance trends.
Action: schema: revenue
PAUSE

You will be called again with this:

Observation: <Revenue table schema>

You then output:

Thought: Now that I know the schema of the revenue table, I can input a specific SQL query to determine the trend over the last 6 months.
Action: sql: <SQL Query>
PAUSE

You will be called again with this:

Observation: <SQL Query results>

Answer: <Answer based on SQL query results>
"""

class QuantAgent(Agent):
    def __init__(self, client, config):
        super().__init__(client, config, QUANT_PROMPT)
        self.sql_loader = SQLDataLoader(config)
        self.messages.append({"role": "system", "content": f"Available {self.sql_loader.list_tables()}"})

    def __call__(self, message):
        """Handle user input and generate a response."""
        self.messages.append({"role": "user", "content": message})


        for _ in range(5):
            result = self.execute()
            self.messages.append({"role": "assistant", "content": result})
            print(result)

            action = self._get_action(result)
            if action is None:
                return result

            action_name, action_value = action
            observation = self._run_action(action_name, action_value)
            self.messages.append({
                "role": "user",
                "content": f"Observation: {observation}",
            })

            print(observation)

        return "Unable to complete the query within the action limit."

    @staticmethod
    def _get_action(response):
        """Extract the first schema or SQL action from a model response."""
        fenced_sql_match = re.search(
            r"```(?:sql)?\s*(SELECT\b[\s\S]*?)\s*```",
            response,
            re.IGNORECASE,
        )
        if fenced_sql_match:
            return "sql", fenced_sql_match.group(1).strip()

        schema_match = re.search(
            r"(?:Action:\s*)?schema\s*:\s*(.+)",
            response,
            re.IGNORECASE,
        )
        if schema_match:
            return "schema", schema_match.group(1).strip()

        sql_match = re.search(
            r"(?:Action:\s*)?sql\s*:\s*(.+)",
            response,
            re.IGNORECASE,
        )
        if sql_match:
            return "sql", sql_match.group(1).strip()

        return None

    def _run_action(self, action_name, action_value):
        """Run a requested SQL loader action and format its observation."""
        try:
            if action_name == "schema":
                return self.sql_loader.get_table_schema(action_value)

            result = self.sql_loader.execute_sql(action_value)
            if not result["valid"]:
                return result["reason"]
            if "error" in result:
                return result["error"]
            return f"Columns: {result['columns']}\nRows: {result['rows']}"
        except (ValueError, TypeError) as error:
            return f"SQL action error: {error}"