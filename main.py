import pandas as pd
from medcat.cat import CAT
from medcat.cdb import CDB
from medcat.vocab import Vocab
from neo4j import GraphDatabase  # ✅ NEW: using Neo4j driver

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
uri = "bolt+s://<your-uri>.databases.neo4j.io"  # e.g. bolt+s://9f72140b.databases.neo4j.io
user = "neo4j"
password = "U4dnFqO-SntTl23-QMaGdmhEylroq-tE23_tA8NEDmk"  # 🔐 Replace with your Aura DB password

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