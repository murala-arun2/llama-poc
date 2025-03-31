list_of_files_prompt = """
```
You are a java developer. Assume you dont have any knowledge of spring security framework. 
Generate a list of class names based on following PlantUML class diagram:
```plantuml
{context}
```

Question: you are asked to generate a list of associated classes ( class names ) based on below user query
"{question}"

generate list of classes in below format along with their package names, skip generating any description or explaination
- ClassA
- ClassB
- ClassC
"""