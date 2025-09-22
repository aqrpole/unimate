
# Unimate

A small independent project running Ollama mistral code for private PDF insights. Additonally, FastAPI python server for incoming requests of questions. It process the contents before hand and keeps the data in ChromaDB on disk. A quesy can be processed with max. delay of 2 minutes. Still possible to reduce further. Please note that Ollama runs on port 11434 and no API has been changed.

Please update the external : true enviorment variable in docker compose file as per requirement.



## Deployment

To deploy this project run
```bash
  docker compose up -d
```
The mistral image is not installed by default, run command:
```bash
  docker compose exec ollama ollama pull mistral
```
Verify the model is installed
```bash
  docker compose exec ollama ollama list
```
To start only rag-service or ollama
```bash
  docker compose up -d rag-service
  docker compose up -d ollama
```
## Running Tests

To run tests, run the following command

```bash
  curl -X PUT "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is political economy?"}'
```
To check the status
```bash
  curl http://ollama:11434
```
To test the health status
```bash
  curl http://ollama:11434/health
```
