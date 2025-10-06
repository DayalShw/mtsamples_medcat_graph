import pandas as pd
import os
from medcat.cat import CAT
from medcat.cdb import CDB
from medcat.vocab import Vocab
from neo4j import GraphDatabase

# ================================================================
# mtsamples.csv was manually downloaded from Kaggle:
# https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions
# ================================================================

# === Load Dataset ===
try:
    if not os.path.exists("mtsamples.csv"):
        raise FileNotFoundError("mtsamples.csv not found in the current directory.")
    df = pd.read_csv("mtsamples.csv")
    texts = df['transcription'].dropna().tolist()[:20]  # Limit to 20 notes
    print("Loaded mtsamples.csv successfully.")
except Exception as e:
    print(f"Error loading mtsamples.csv: {e}")
    exit(1)

# === Load MedCAT SNOMED Model ===
try:
    if not os.path.exists("cdb.dat") or not os.path.exists("vocab.dat"):
        raise FileNotFoundError("cdb.dat or vocab.dat file is missing.")
    cdb = CDB.load("cdb.dat")
    vocab = Vocab.load("vocab.dat")
    cat = CAT(cdb=cdb, vocab=vocab)
    print("MedCAT SNOMED model loaded.")
except Exception as e:
    print(f"Error loading MedCAT model: {e}")
    exit(1)

# === Annotate Notes ===
note_entities = []
try:
    for idx, text in enumerate(texts):
        entities = cat.get_entities(text)
        for ent_id, ent in entities['entities'].items():
            note_entities.append({
                'note_id': f'note_{idx}',
                'cui': ent['cui'],
                'name': ent['pretty_name']
            })
    print("Entity annotation completed.")
except Exception as e:
    print(f"Error during annotation: {e}")
    exit(1)

# === Neo4j Connection Setup ===
uri = "bolt+s://9f72140b.databases.neo4j.io" 
user = "neo4j"
password = "U4dnFqO-SntTl23-QMaGdmhEylroq-tE23_tA8NEDmk"

def upload_to_neo4j(tx, data):
    for ent in data:
        tx.run("""
            MERGE (n:Note {id: $note_id})
            MERGE (c:Concept {cui: $cui, name: $name})
            MERGE (n)-[:MENTIONS]->(c)
        """, note_id=ent['note_id'], cui=ent['cui'], name=ent['name'])

# === Push Entities to Neo4j ===
try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        session.execute_write(upload_to_neo4j, note_entities)
    print("Graph uploaded to Neo4j successfully!")
except Exception as e:
    print(f"Error uploading to Neo4j: {e}")
    exit(1)