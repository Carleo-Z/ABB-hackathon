import os
import json
from neo4j import GraphDatabase, exceptions
from fastapi import FastAPI
from pydantic import BaseModel

# --- FastAPI App Initialization ---
app = FastAPI()

# --- Pydantic Model for Request Body ---
# This defines the expected input JSON: {"cypher_query": "..."}
class QueryRequest(BaseModel):
    cypher_query: str

# --- Configuration (from environment variables) ---
NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j+s://e5636b4a.databases.neo4j.io")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "FrCgy_TpBuTR7uYM0AMlpHRq4hcWB3mxMR88OghOyMc")

# The Neo4jConnection class and query logic remain the same
class Neo4jConnection:
    # (Your Neo4jConnection class from the previous answer goes here, unchanged)
    def __init__(self, uri, user, password):
        try:
            self._driver = GraphDatabase.driver(uri, auth=(user, password))
            self._driver.verify_connectivity()
        except exceptions.ServiceUnavailable:
            self._driver = None # Handle connection error gracefully

    def close(self):
        if self._driver is not None:
            self._driver.close()

    def query(self, cypher_query: str) -> str:
        if self._driver is None:
            return json.dumps({"error": "Database connection is not available."})
        try:
            with self._driver.session() as session:
                result = session.run(cypher_query)
                records = [record.data() for record in result]
                return json.dumps(records, indent=2)
        except Exception as e:
            return json.dumps({"error": "Query failed", "details": str(e)})


# --- API Endpoint ---
@app.post("/run-query")
def execute_query_endpoint(request: QueryRequest) -> dict:
    """
    This is the API endpoint that Dify will call.
    It receives the cypher_query from the request body.
    """
    conn = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    query_result = conn.query(request.cypher_query)
    conn.close()
    
    # The endpoint returns a dictionary that FastAPI converts to JSON
    return {"result": query_result}

