import json
from cog.torque import Graph
from uuid import uuid4
import os.path

def construct_graph(json_data):
    g = Graph(str(uuid4()))

    # identify parent and interface classes
    parent_and_interface_map = dict()
    for class_obj in json_data.values():
        class_name = f'{class_obj["package"]}.{class_obj["class_name"]}'
        if class_obj["extendz"]:
            add_child(parent_and_interface_map, class_obj["extendz"], class_name)
        for imp in class_obj["implementz"]:
            add_child(parent_and_interface_map, imp, class_name)
    print('\nparent_and_interface_map :', parent_and_interface_map)

    # Aggregate parent with children of children
    parent_aggregate_map = dict()
    for parent_name in parent_and_interface_map.keys():
        children = []
        get_children(parent_and_interface_map, parent_name, children)
        parent_aggregate_map[parent_name] = children
    print('\nparent_aggregate_map :', parent_aggregate_map)

    # Iterate over each classes and create graph, also mark parent calls
    for class_obj in json_data.values():
        class_name = f'{class_obj["package"]}.{class_obj["class_name"]}'

        if class_obj["extendz"]:
            create_relationship(g, class_name, 'extends', class_obj["extendz"])
        
        for imp in class_obj["implementz"]:
            create_relationship(g, class_name, 'implements', imp)

        # Create relationships for fields
        for field in class_obj["fields"]:
            field_name = f'{class_name}::{field["field_name"]}'
            create_relationship(g, class_name, 'member_field', field_name)
            create_relationship(g, field_name, 'type', field["field_type"])
        
        method_name_counts = dict()

        # Create relationships for methods
        for method in class_obj["methods"]:
            method_with_params = f'{method["method_name"]}_{len(method["formal_params"])}'
            count = method_name_counts.get(method_with_params)
            idx = count if count else 1
            method_name_counts[method_with_params] = idx + 1
            method_name = f'{class_name}::{method_with_params}_{idx}'
            # print('method_name :', method_name)
            create_relationship(g, class_name, 'member_method', method_name)
            create_relationship(g, method_name, 'return_type', f'{method["return_type"]}')
            
            # Create relationships for method parameters
            for param in method["formal_params"]:
                create_relationship(g, method_name, 'param', f'{param["param_type"]}')
            
            # Create relationships for method calls
            for method_call in method["methodCalls"]:
                if method_call["target_type"] and method_call["target_method_name"]:
                    target_method_name = f'{method_call["target_method_name"]}_{len(method_call["target_params"])}_1'
                    # create direct relationship
                    create_relationship(g, method_name, 'method_call', f'{method_call["target_type"]}::{method_call["target_method_name"]}_{len(method_call["target_params"])}_1')
                    # create child relationship
                    if parent_aggregate_map.get(method_call["target_type"]):
                        for child_name in parent_aggregate_map[method_call["target_type"]]:
                            create_relationship(g, method_name, 'method_call', f'{child_name}::{method_call["target_method_name"]}_{len(method_call["target_params"])}_1')
                            if child_name == "org.springframework.security.access.SecurityConfig":
                                print('call :', method_name, 'method_call', f'{child_name}::{method_call["target_method_name"]}_{len(method_call["target_params"])}_1')
                # else:
                    # print('skipping method call :', method_call["usage"])

    return g

# Function to create relationships between nodes
def create_relationship(g, node_a, relationship, node_b):
    g.put(node_a, relationship, node_b)
    
def add_child(parent_and_interface_map, parent_name, child_name):
    if parent_and_interface_map.get(parent_name) == None:
        parent_and_interface_map[parent_name] = {}
    parent_and_interface_map[parent_name][child_name] = {}


def get_children(parent_and_interface_map, parent_name, children_names):
    if parent_and_interface_map.get(parent_name):
        children = parent_and_interface_map[parent_name].keys()
        for child_name in children:
            children_names.append(child_name)
            get_children(parent_and_interface_map, child_name, children_names)
        
def main():
    # Output the graph data (it will represent nodes and their relationships)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, "../plantUML/spring-security-core.json")
    
    json_data = None
    with open(path, 'r') as f:
        json_data = json.loads(f.read())

    g = construct_graph(json_data) 
    print('\ncount :', g.v().count())
    print('\nscan :', g.scan())
    print('\nclass :', g.v("org.springframework.security.access.SecurityConfig").all())
    print('\nfields :', g.v("org.springframework.security.access.SecurityConfig").out("member_field").all())
    print('\nmethods :', g.v("org.springframework.security.access.SecurityConfig").out("member_method").all())
    print('\nmethod_calls :', g.v("org.springframework.security.access.SecurityConfig::createListFromCommaDelimitedString_1_1").out("method_call").all())
    print('\ncall chain:',g.v("org.springframework.security.access.SecurityConfig::getAttribute_0_1").inc("method_call").all())
    # g.v("org.springframework.security.access.SecurityConfig").tag("from").out().tag("to").view("test1").render()

    print('\ncall chain test', find_call_chain(g, "SecurityConfig::getAttribute"))
    g.close()

def find_call_chain(g, class_method_name):
    return g.v(func=lambda x: x.find(class_method_name) > 0).inc("method_call").all()

if __name__ == '__main__':
    main()