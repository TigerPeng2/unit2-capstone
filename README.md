# Unit 2 Capstone: Multi-Agent RAG for Enterprise Documentation
This project is a CLI-based multi-agent RAG system that allows the user to query qualitative and quantitative information about a set of enterprise documentation.

The qualitative data is accessed through an agent using the vector database Chroma, while the qualitative data is accessed through an SQL agent.

The data used for this system is entirely artificial, generated through a more-or-less hardcoded script `generate-data.py` in the `/data` directory, in order to answer the test questions posed in the project requirements.

## Installing the Environment and Generating Data
Run 

`python -m venv venv`

`source venv/bin/activate`

`pip install -r requirements.txt`

`python data/generate-data.py`

Also make sure to add the GEMINI_API_KEY to your .env in the project top level directory.

## Running the CLI
In order to run the tool, install and then run the project as a module

`pip install -e .`

`python -m multi_rag add-source`
To add a source

`python -m multi_rag query`
To run a query

## Architecture
The entire project is not functional, because I could not figure out how to get the SQL agent to follow instructions and request the table schema rather than making up column names. But the basic structure is as follows:

The ManagerAgent is called when the query is input, and is instructed to break down the main query into a sequential set of sub-queries, directed at either the quantitative or qualitative agents.

The respective agents are called, using a chroma collection and the sql database as their sources, respectively, and their answers are added to the message that's passed into the next subquery.

At the end, the entire message log is passed into the ManagerAgent to provide the final answer.