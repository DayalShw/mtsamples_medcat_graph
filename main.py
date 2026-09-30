import os
import pandas as pd
from dotenv import load_dotenv
from medcat.cat import CAT
from medcat.cdb import CDB
from medcat.vocab import Vocab
from neo4j import GraphDatabase  # ✅ NEW: using Neo4j driver

load_dotenv()  # reads variables from the project's .env file

# === Load Dataset ===
df = pd.read_csv("mtsamples.csv")
texts = df['transcription'].dropna().tolist()[:20]  # Limit to 20 notes

# === Load MedCAT SNOMED Model ===
cdb = CDB.load("cdb.dat")           # ✅ your pretrained concept model
vocab = Vocab.load("vocab.dat")     # ✅ your vocab model
cat = CAT(cdb=cdb, vocab=vocab)

# === Annotate Notes ===
note_entities = []
for idx, text in enumerate(texts):
    entities = cat.get_entities(text)
    for ent_id, ent in entities['entities'].items():
        note_entities.append({
            'note_id': f'note_{idx}',
            'cui': ent['cui'],
            'name': ent['pretty_name']
        })

# === Neo4j Connection Setup ===
# Credentials are loaded from .env (never hardcoded / never committed)
uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")

if not all([uri, user, password]):
    raise RuntimeError(
        "Missing Neo4j credentials. Set NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD in your .env file."
    )

driver = GraphDatabase.driver(uri, auth=(user, password))

# === Push Entities to Neo4j ===
def upload_to_neo4j(tx, data):
    for ent in data:
        tx.run("""
            MERGE (n:Note {id: $note_id})
            MERGE (c:Concept {cui: $cui, name: $name})
            MERGE (n)-[:MENTIONS]->(c)
        """, note_id=ent['note_id'], cui=ent['cui'], name=ent['name'])

with driver.session() as session:
    session.write_transaction(upload_to_neo4j, note_entities)

print("✅ Graph uploaded to Neo4j successfully!")