import json
from cog.torque import Graph


g = Graph("spring-security-core")

with open('spring-security-core.json', 'r') as f:
    data = json.loads(f.read())

# Function to create relationships between nodes
def create_relationship(node_a, relationship, node_b):
    g.put(node_a, relationship, node_b, update=True)

def get_class_node(class_name):
    all_splits = class_name.split('.')
    all_splits = all_splits[1:-1]
    node = g.v("org")
    for split in all_splits:
        child_nodes = node.filter(func=lambda x: x == 'sub_package').out().all()
        if len(child_nodes["result"]) > 0:
            node = g.v(child_nodes["result"][0]["id"])
            continue
        g.put(node, 'sub_package', split)
        node = 
    

# Iterate over each class object in the parsed data
for class_obj in data:
    # Extract package and subpackage information
    package_parts = class_obj["package"].split('.')
    
    # Create package and subpackage nodes
    for i in range(len(package_parts)):
        if i + 1 < len(package_parts):
            create_relationship(package_parts[i], 'sub_package', package_parts[i + 1])
    
    # Create class node
    create_relationship(package_parts[-1], 'class', class_obj["class_name"])

    # Create relationships for fields
    for field in class_obj["fields"]:
        create_relationship(class_obj["class_name"], 'member_field', field["field_name"])
        create_relationship(field["field_name"], 'type', field["field_type"])
    
    # Create relationships for methods
    for method in class_obj["methods"]:
        create_relationship(class_obj["class_name"], 'member_method', method["method_name"])
        create_relationship(method["method_name"], 'return_type', f'{method["return_type"]}')
        
        # Create relationships for method parameters
        for param in method["formal_params"]:
            create_relationship(method["method_name"], 'param', f'{param["param_type"]}')
        
        # Create relationships for method calls
        for method_call in method["methodCalls"]:
            create_relationship(method["method_name"], 'method_call', f'{method_call["target_type"]}')

# Output the graph data (it will represent nodes and their relationships)
g.v('org').render()

