# MTSamples MedCAT Knowledge Graph

This project turns unstructured medical transcription notes into a **queryable knowledge graph** by extracting clinical concepts with MedCAT and storing the results in Neo4j.

## What it does

1. Loads real-world-style medical transcription notes from the public **MTSamples** dataset (`mtsamples.csv`).
2. Runs each note through **MedCAT** (Medical Concept Annotation Toolkit), using a pretrained SNOMED CT concept database and vocabulary, to detect medical entities (diagnoses, symptoms, procedures) in free text.
3. Uploads the results to a **Neo4j** graph database:
   - Each note becomes a `Note` node
   - Each detected medical concept becomes a `Concept` node
   - A `MENTIONS` relationship links a note to every concept it contains

The result is a graph you can query to explore relationships between documents and clinical concepts — e.g. "which notes mention hypertension" or "which notes share the most concepts with this one."

## Project structure

```
mtsamples_medcat_graph/
├── main.py              # Pipeline: load data → extract concepts → upload to Neo4j
├── mtsamples.csv         # MTSamples dataset (medical transcription notes)
├── cdb.dat               # Pretrained MedCAT concept database (SNOMED CT) — not in repo, see below
├── vocab.dat              # Pretrained MedCAT vocabulary — not in repo, see below
└── visualisation.png      # Screenshot of the resulting graph in Neo4j Browser
```

## Setup

1. Install dependencies:
   ```
   pip install pandas medcat neo4j python-dotenv
   ```
2. Add your Neo4j credentials to the project's `.env` file (never commit this file):
   ```
   NEO4J_URI=bolt+s://<your-uri>.databases.neo4j.io
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=<your-password>
   ```
3. Obtain MedCAT's pretrained SNOMED CT model files (`cdb.dat` and `vocab.dat`) — these are excluded from the repo because they exceed GitHub's 100MB file limit. Place them in this folder before running.

## Run

```
python main.py
```

This processes the first 20 notes in `mtsamples.csv` and uploads the extracted concepts and relationships to your Neo4j instance.

## Notes

- Credentials are loaded from environment variables via `python-dotenv` — never hardcoded.
- `cdb.dat` and `vocab.dat` are large pretrained model files and are git-ignored; download or regenerate them separately.
