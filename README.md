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

TO-DO:
- Generate artificial data
    - Security policy
    - Code review process
    - Employee benefits and perks page
    - Customer satisfaction guarantee
    - Customer complaint process
    - Customer success strategies
    - Expense approval policy - when is manager approval needed (receipt value, expense time)
- Quantitative
    - Revenue by region (monthly)
    - Costs by category by region (monthly)
    - Sales records, generating random churn rate by decreasing the percentage chance that you pick an earlier record
        - Customer id, timestamp, region, sales quantity
    - Employee satisfaction polling (employee id, cost center, rating (0-10))
    - Software ticketing - name, description, open timestamp, close timestamp
    - Expense data - employee id, timestamp, expense amount, cost center
- Basic CLI functionality - adding data sources, inputting a query, outputting a response
- Routing qualitative and quantitative queries
- Qualitative document rag (Chroma)
- Quantitative queries - natural language to SQL translation
- Multi-step queries and advanced orchestration - ReAct for task decomposition, query splitting and human-in-the-loop verification.

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