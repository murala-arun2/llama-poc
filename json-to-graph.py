import json
from cog.torque import Graph


g = Graph("spring-security-core")

with open('spring-security-core.json', 'r') as f:
    data = json.loads(f.read())

# Function to create relationships between nodes
def create_relationship(node_a, relationship, node_b):
    g.put(node_a, relationship, node_b)
    
# Iterate over each class object in the parsed data
for class_obj in data:
    class_name = f'{class_obj["package"]}.{class_obj["class_name"]}'

    if class_obj["extendz"]:
        create_relationship(class_name, 'extends', class_obj["extendz"])
    
    for imp in class_obj["implementz"]:
        create_relationship(class_name, 'implements', imp)

    # Create relationships for fields
    for field in class_obj["fields"]:
        field_name = f'{class_name}::{field["field_name"]}'
        create_relationship(class_name, 'member_field', field_name)
        create_relationship(field_name, 'type', field["field_type"])
    
    method_name_counts={}

    # Create relationships for methods
    for method in class_obj["methods"]:
        count = method_name_counts.get(method["method_name"])
        idx = count if count else 1
        method_name_counts[method["method_name"]] = idx + 1
        method_name = f'{class_name}::{method["method_name"]}_{idx}'
        create_relationship(class_name, 'member_method', method_name)
        create_relationship(method_name, 'return_type', f'{method["return_type"]}')
        
        # Create relationships for method parameters
        for param in method["formal_params"]:
            create_relationship(method_name, 'param', f'{param["param_type"]}')
        
        # Create relationships for method calls
        for method_call in method["methodCalls"]:
            create_relationship(method_name, 'method_call', f'{method_call["target_type"]}::{method_call["target_method_name"]}_1')

# Output the graph data (it will represent nodes and their relationships)
print('\ncount :', g.v().count())
print('\nscan :', g.scan())
print('\nclass :', g.v("org.springframework.security.access.SecurityConfig").all())
print('\nfields :', g.v("org.springframework.security.access.SecurityConfig").out("member_field").all())
print('\nmethods :', g.v("org.springframework.security.access.SecurityConfig").out("member_method").all())
print('\nmethod_calls :', g.v("org.springframework.security.access.SecurityConfig::createListFromCommaDelimitedString_1").out("method_call").all())
