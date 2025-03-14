- Download ollama
```cd ollama-0.5.4-ipex-llm-2.2.0b20250226-win``` 

- Starting ollama server 
```start-ollama.bat```

- Downloading llama3.2 model 
```ollama pull llama3.2 ```

- Hosting model for LangChain programs to use it.. Need to keep it prompt running 
```ollama run llama3.2```

- Download chroma
```pip install chromadb```

- Start chroma db 
```chroma run --path /Apps/chromadb-data ```

- Load java project source code into chroma db 
```python34 load-data-to-chromadb-langchain.py ```

- Run similar search to find callers of a method (just chromdb only)
```python34 similarity-search-chromadb.py ```

 

 

 

  