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

## Running the CLI
In order to run the tool, install and then run the project as a module

`pip install -e .`
`python -m multi_rag`

TO-DO:
- Read through config and add loader class for database info string interface
    - CLI loads config -> loads data sources -> data sources provide data summary strings -> loaders provide data acess to respective agents
- Routing qualitative and quantitative queries
- Qualitative document rag (Chroma) wtih source attribution
- Quantitative queries - natural language to SQL translation
- Multi-step queries and advanced orchestration - ReAct for task decomposition, query splitting and human-in-the-loop verification.
- SQL Validation and Tokenomics

myproject/  
├── pyproject.toml  
├── README.md  
├── config/  
│   └── config.json  
├── src/  
│   └── multi_rag/  
│       ├── __init__.py  
│       ├── __main__.py  
│       ├── cli.py  
│       ├── config.py  
│       │  
│       ├── agents/  
│       │   ├── __init__.py  
│       │   ├── base.py  
│       │   ├── qualitative.py  
│       │   └── quantitative.py  
│       │  
│       ├── data/  
│       │   ├── __init__.py  
│       │   ├── loader.py  
│       │   └── types.py  
│       │  
│       ├── models/  
│       │   ├── __init__.py  
│       │   ├── results.py  
│       │   └── documents.py  
│       │  
│       ├── orchestrator.py  
│       └── utils/  
│           ├── __init__.py  
│           └── logging.py  
│  
├── tests/  
├── docs/  
└── data/  