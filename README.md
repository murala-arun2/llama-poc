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
```chroma run --path e:\\code\\chromadb-data-1 ```

- Load java project source code into chroma db 
```python34 load-data-to-chromadb-langchain.py ```
  - discussion items
    - chunking with small size - picks few lines of function
    - adjusted chunks seperators (public, private, class etc) to use selective splitting
    - adjuted chunck size to very big value to fit whole file in 1 document

- Run similar search to find callers of a method (just chromdb only)
`python34 docs-in-collection.py `


**TODO list**
- handle costructor calls
``` enterCreator :Acc  es  sD  eni  edEx  ce  pt  ion("Can't change pas  s  w  ord as no Au  th  en  tic  ation object found in context "+"for cur  r  e  nt u   se   r.") ```

- handle method referenceswhich are not identied..mostly parent method calls
``` getJdbcTemplate().query(getUs  er  sB  yUs  er  na  me  Query(),this.us  er  Det  ai  lsMapper,us  er  na  me)\ngetU  se  rs  ByU  se  rn  am eQuery() is method from parent class ```

- handle call chaining .. is not detected
```ctx member reference expression text:  ps.getParameterMetaData().getParameterCount()\n.getParameterCount() ``` 

- add annotation info in notes on class and fields
``` note left of A::counter\n  This member is annotated\nend note\n\nnote right of A::"start(int timeoutms)"\n  This method with int\nend\nnote```

``` note top of Object : In java, every class\nextends this one. ```

- construct graph based on user query using llm. sample for call_chian on method calls
``` g.v(func=lambda x: x.find(class_method_name) > 0).inc("method_call").all() ```

**Other notes**

``` java -DPLANTUML_LIMIT_SIZE=999999 -jar .\plantuml-1.2025.2.jar .\apache-hertzbeat-output.puml ```

starcoder with ta-prompt ==> in-context training mimic-ing previous conversation log
https://huggingface.co/datasets/bigcode/ta-prompt
https://github.com/bigcode-project/starcoder/issues/101

codebert 512 length issue ??
