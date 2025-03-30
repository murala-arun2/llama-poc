from antlr4 import *
from JavaLexer import JavaLexer
from JavaParser import JavaParser
from JavaParserListener import JavaParserListener
import os
from json import dumps
import re

commonImports = [
    "java.lang.String",
    "java.lang.Integer",
    "java.lang.Long",
    "java.lang.Double",
    "java.lang.Float",
    "java.lang.Integer",
    "java.lang.Class",
    "java.lang.Throwable",
    "java.lang.Object",
    "java.lang.Exception"
]

data_types = [
    "int",
    "long",
    "boolean",
    "float",
    "double"
]

class JavaASTListener(JavaParserListener):
    def __init__(self):
        # self.classMap = {}
        self.classes = []
        self.packageName = None
        self.callStack = []
        self.pendingImports = []

    def enterPackageDeclaration(self, ctx):
        self.packageName = ctx.qualifiedName().getText()
        print('package name: ', self.packageName)
        # return super().enterPackageDeclaration(ctx)

    def enterImportDeclaration(self, ctx):
        self.pendingImports.append(ctx.qualifiedName().getText())
        # return super().enterImportDeclaration(ctx)
    
    def enterInterfaceDeclaration(self, ctx):
        interface_name = ctx.identifier().getText()
        print('interface name: ', interface_name)
        class_info = {
            "type": "interface",
            "class_name": interface_name,
            "class_type": "interface",
            "package": self.packageName,
            "implementz": [],
            "extendz": None,
            "fields": [],
            "methods": [],
            "methodCalls": [],
            "imports": [importt for importt in self.pendingImports]
        }
        self.pendingImports = []
        self.classes.append(class_info)
        self.callStack.append(class_info)
        # return super().enterInterfaceDeclaration(ctx)

    def exitInterfaceCreator(self, ctx):
        print('exit interface creator')
        self.callStack.pop()
        # return super().exitInnerCreator(ctx)

    def enterInterfaceBody(self, ctx):
        print('ctx interface body text: ')
        return super().enterInterfaceBody(ctx)
    
    def enterInterfaceCommonMemberDeclaration(self, ctx):
        print('ctx interface common member text: ')
        # return super().enterInterfaceCommonMemberDeclaration(ctx)
    
    def enterGenericInterfaceMethodDeclaration(self, ctx):
        print('ctx generic interface method text: ', ctx.getText(), dir(ctx.interfaceCommonBodyDeclaration()))
        method_name = ctx.interfaceCommonBodyDeclaration().identifier().getText()
        return_type = ctx.interfaceCommonBodyDeclaration().typeTypeOrVoid().getText()
        formal_params = [{
            "param_name":param.variableDeclaratorId().getText(), 
            "param_type": param.typeType().getText()
            } for param in ctx.interfaceCommonBodyDeclaration().formalParameters().formalParameterList().formalParameter()] if ctx.interfaceCommonBodyDeclaration().formalParameters().formalParameterList() else []
        method_info = {
            "type": 'method',
            "method_name": method_name,
            "return_type": return_type,
            "formal_params": formal_params,
            "methodCalls": []
        }
        print('method_info :', method_info)
        if self.classes:
            self.classes[-1]["methods"].append(method_info)
            # print('self.classes[-1]: ', self.classes[-1])
        self.callStack.append(method_info)

    def exitGenericInterfaceMethodDeclaration(self, ctx):
        print('exit generic method declaration')
        self.callStack.pop()
        # return super().exitGenericMethodDeclaration(ctx)

    def enterInterfaceMethodDeclaration(self, ctx):
        print('ctx interface method text: ', ctx.getText(), dir(ctx.interfaceCommonBodyDeclaration()))
        method_name = ctx.interfaceCommonBodyDeclaration().identifier().getText()
        return_type = ctx.interfaceCommonBodyDeclaration().typeTypeOrVoid().getText()
        formal_params = [{"param_name":param.variableDeclaratorId().getText(), "param_type":param.typeType().getText()} for param in ctx.interfaceCommonBodyDeclaration().formalParameters().formalParameterList().formalParameter()] if ctx.interfaceCommonBodyDeclaration().formalParameters().formalParameterList() else []
        method_info = {
            "type": 'method',
            "method_name": method_name,
            "return_type": return_type,
            "formal_params": formal_params,
            "methodCalls": []
        }
        print('method_info :', method_info)
        if self.classes:
            self.classes[-1]["methods"].append(method_info)
        self.callStack.append(method_info)
        # return super().enterInterfaceMethodDeclaration(ctx)
    
    def exitInterfaceMethodDeclaration(self, ctx):
        print('exit interface method declaration')
        self.callStack.pop()
        # return super().exitInterfaceMethodDeclaration(ctx)
    
    def enterClassDeclaration(self, ctx:JavaParser.ClassDeclarationContext):
        # Extract class name
        print('ctx class text: ', ctx.identifier().getText())
        class_name = ctx.identifier().getText()
        implementz = [implement.getText() for implement in ctx.typeList()] if ctx.typeList() else []
        print('implements:', implementz)
        extendz = ctx.typeType().getText() if ctx.typeType() else None
        print('extends:', extendz)
        class_info = {
            'type': 'class',
            'class_name': class_name,
            'class_type': 'class',
            'package': self.packageName,
            'implementz': implementz,
            'extendz': extendz,
            'fields': [],
            'methods': [],
            'methodCalls': [],
            'imports': [importt for importt in self.pendingImports]
        }
        self.pendingImports = []
        self.classes.append(class_info)
        self.callStack.append(class_info)

    def exitClassDeclaration(self, ctx):
        print('exit class declaration')
        self.callStack.pop()
        # return super().exitClassDeclaration(ctx)

    def enterFieldDeclaration(self, ctx:JavaParser.FieldDeclarationContext):
        # Extract field names (attributes)
        print('ctx field text: ', ctx.getText())
        # print('ctx.variableDeclarators().variableDeclarator() : ', ctx.variableDeclarators().variableDeclarator())
        # [print('variable declarator', ctx.typeType().getText(), declarator.variableDeclaratorId().identifier().getText(), dir(declarator.variableDeclaratorId())) for declarator in ctx.variableDeclarators().variableDeclarator()]
        # [print(, declarator.get) for declarator in ctx.variableDeclarators().variableDeclarator()]
        fields = [[declarator.variableDeclaratorId().identifier().getText(), ctx.typeType().getText()] for declarator in ctx.variableDeclarators().variableDeclarator()]
        for field in fields:
            field_info = {
                "type": "field",
                "field_name": field[0],
                "field_type": field[1],
                "methodCalls": []
            }
            if self.classes:
                print('self.classes[-1][\"fields\"]: ', self.classes[-1]["fields"])
                self.classes[-1]["fields"].append(field_info)
                print('self.classes[-1][\"fields\"]: ', self.classes[-1]["fields"])
            # self.callStack.append(field_info)

    def exitFieldDeclaration(self, ctx):
        print('exit field declaration')
        # self.callStack.pop()
        # return super().exitFieldDeclaration(ctx)

    def enterMethodDeclaration(self, ctx:JavaParser.MethodDeclarationContext):
        # Extract method names
        print('ctx method text: ', ctx.identifier().getText())
        method_name = ctx.identifier().getText()
        return_type = ctx.typeTypeOrVoid().getText()
        formal_params = [{"param_name": param.variableDeclaratorId().getText(), "param_type": param.typeType().getText()} for param in ctx.formalParameters().formalParameterList().formalParameter()] if ctx.formalParameters().formalParameterList() else []
        method_info = {
            'type': 'method',
            'method_name': method_name,
            'return_type': return_type,
            'formal_params': formal_params,
            'methodCalls': []
        }
        # print('method_info :', method_info)
        if self.classes:
            self.classes[-1]["methods"].append(method_info)
        self.callStack.append(method_info)

    def exitMethodDeclaration(self, ctx):
        print('exit method declaration')
        self.callStack.pop()
        # return super().exitMethodDeclaration(ctx)

    # def enterMethodCallExpression(self, ctx):
    #     print('ctx method call expression text: ', ctx.getText())
    #     # return super().enterMethodCallExpression(ctx)

    def enterMemberReferenceExpression(self, ctx):
        print('ctx member reference expression text: ', ctx.getText())
        if len(self.callStack) > 0: # todo on Class level annotation references like Scope.SINGLETON
            self.callStack[-1]["methodCalls"].append(ctx.getText())
        # return super().enterMemberReferenceExpression(ctx)

    # def enterMethodReferenceExpression(self, ctx):
    #     print('ctx method reference expression text: ', ctx.getText())
    #     # return super().enterMethodReferenceExpression(ctx)

    # def enterMethodCall(self, ctx):
    #     print('ctx method call text: ', ctx.getText())
    #     print('callStack len: ', len(self.callStack))
    #     self.callStack[-1]["methodCalls"].append(ctx.getText())
    #     # return super().enterMethodCall(ctx)

    def enterConstructorDeclaration(self, ctx):
        print('ctx constructor text: ', ctx.getText())
        params = [{"param_name": param.variableDeclaratorId().getText(), "param_type": param.typeType().getText()} for param in ctx.formalParameters().formalParameterList().formalParameter()] if ctx.formalParameters().formalParameterList() else []
        params_info = {
            'type': 'constructor',
            'method_name': ctx.identifier().getText(),
            'return_type': None,
            'formal_params': params,
            'methodCalls': []
        }
        # print('params_info:', params_info)
        if self.classes:
            self.classes[-1]["methods"].append(params_info)
        self.callStack.append(params_info)

    def exitConstructorDeclaration(self, ctx):
        self.callStack.pop()
        
    def enterVariableDeclarator(self, ctx):
        print('variable decleartor :', ctx.getText())
        return super().enterVariableDeclarator(ctx)

def parse_java_file(file_path):
    input_stream = FileStream(file_path, encoding='utf-8')
    lexer = JavaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = JavaParser(stream)
    tree = parser.compilationUnit()

    # Create a listener to extract classes, methods, and fields
    listener = JavaASTListener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)

    return listener.classes

def find_var_type(vars, var_name):
    match_vars = list(vars.filter(lambda varr: varr["name"] == var_name))
    return match_vars[0]["type"] if len(match_vars) > 0 else None

def generate_definition(map):
    plantuml_code = ''
    for item in map.items():
        key, value = item
        print('key :', key, 'value :', value)
        if key == "classes":
            continue
        plantuml_code += f'package {key} {{\n'
        plantuml_code += generate_definition(value)
        plantuml_code += '}\n'
    classes = map.get("classes") if map.get("classes") else []
    for class_info in classes:
        # print('class_info:', class_info)
        member_methods_and_calls = []
        # Define the class
        plantuml_code += f'{class_info["class_type"]} {class_info["class_name"]} {'extends '+class_info["extendz"] if class_info["extendz"] else ''} {'implements '+(','.join(class_info["implementz"])) if len(class_info["implementz"]) > 0 else ''}  {{\n'

        # Add fields
        for field_info in class_info["fields"]:
            # print("field_info:', field_info)
            plantuml_code += f'  {field_info["field_name"]} : {field_info["field_type"]}\n'  # Defaulting type to String for simplicity

        # Add methods
        for method_info in class_info["methods"]:
            plantuml_code += f'  {method_info["method_name"]}({", ".join([param["param_name"]+" : "+param["param_type"] for param in method_info["formal_params"]])}) : {method_info["return_type"]}\n'  # Defaulting to void for simplicity
            member_methods_and_calls.append({
                "method_name": method_info["method_name"],
                "methodCalls": method_info["methodCalls"]
            })
        plantuml_code += '}\n'

        # Add method calls
        for member_method_and_calls in member_methods_and_calls:
            for methodCall in member_method_and_calls["methodCalls"]:
                if methodCall["target_type"] == 'this': 
                    plantuml_code += f'{class_info["package"]}.{class_info["class_name"]}::{member_method_and_calls["method_name"]} -- {class_info["package"]}.{class_info["class_name"]}::{methodCall["target_method_name"]} : {methodCall} \n'
                elif  methodCall["target_type"] != None:
                    plantuml_code += f'{class_info["package"]}.{class_info["class_name"]}::{member_method_and_calls["method_name"]} -- {methodCall["target_type"]}::{methodCall["target_method_name"]} : {methodCall["usage"]} \n'
                # vars = [{"name": field["field_name"], "type": field["field_type"]} for field in class_info["fields"]]
                # vars.extend([{"name": param["param_name"], "type": param["param_type"]} for param in method_info["formal_params"]])
                # varr = [param for param in vars if param["name"] == methodCall_on_object]
                # if len(varr) > 0:
                #     typee = varr[0]["type"]
                #     full_varr = [importt for importt in class_info["imports"] if importt.endswith(f'.{typee}')]
                #     if len(full_varr) > 0:
                #         if(full_varr[0].endswith('.Log') or full_varr[0].endswith('.Logger')):
                #             continue
                #         function_name = methodCall.split('.')[1].split('(')[0]
                #         plantuml_code += f'{class_info["class_name"]}::{methodCall_info["method_name"]} -- {full_varr[0]}::{function_name} : {methodCall} \n'
    return plantuml_code

def find_import(imports, class_name, package_name):
    if len(list(filter(lambda v: v == class_name, data_types))) > 0:
        return class_name
    class_name = class_name.split('<')[0]
    importss = []
    importss.extend(commonImports)
    importss.extend(imports)
    types = [imp for imp in importss if imp.endswith(f'.{class_name}')]
    if len(types) > 0:
        return types[0]
    return f'{package_name}.{class_name}'

def update_method_calls(imports, varss, methodCalls, package_name, class_name):
    method_calls = []
    for call_info in methodCalls:
        target = call_info.replace('this.','')
        dot_index = target.find('.')
        method_call_index = target.find('(')
        is_var_method_call = method_call_index > dot_index
        if is_var_method_call == False and target.find('(') > 0:
            splits = target.split('(')
            params = splits[1].replace(')', '').split(',')
            method_calls.append({
                "target_type": f'{package_name}.{class_name}',
                "target_name": "this",
                "target_method_name": splits[0],
                "target_params": params, # TODO
                "usage": call_info
            })
        elif re.match("^[A-Z]", target): # static method invocation 
            target_name, method_call = target.split('.')[:2]
            if method_call.find('(') > 0:
                method_name, params = method_call.split('(')[:2]
                params = params.strip().split(')')[0].split(',') if len(params.strip()) > 1 else []
                method_calls.append({
                    "target_type": find_import(imports, target_name, package_name),
                    "target_name": target_name,
                    "target_method_name": method_name,
                    "target_params": params, # TODO
                    "usage": call_info
                })
        elif target.find('.') > 0 and target.find('(') > target.find('.'):
                target_name, method_call = target.split('.')[:2] # TODO fix this issue
                match_types = list(filter(lambda x: x["name"] == target_name, varss))
                target_type = match_types[0]["type"] if len(match_types) > 0 else None
                if method_call.find('(') > 0:
                    target_method_name, params = method_call.split('(')[:2]
                    params = params.strip().split(')')[0].split(',') if len(params.strip()) > 1 else []
                    method_calls.append({
                        "target_type": target_type, # TODO
                        "target_name": target_name,
                        "target_method_name": target_method_name,
                        "target_params": params, # TODO
                        "usage": call_info
                    })
        else:
             method_calls.append({
                "target_type": None, # TODO
                "target_name": None,
                "target_method_name": None,
                "target_params": None, # TODO
                "usage": call_info
            })
    return method_calls

def update_class_references_with_package_names(classes):
    for class_info in classes:
        
        class_info["extendz"] = find_import(class_info["imports"], class_info["extendz"], class_info["package"]) if class_info["extendz"] else None
        class_info["implementz"] = [find_import(class_info["imports"], impp, class_info["package"]) for impp in class_info["implementz"]]
        
        for field in class_info["fields"]:
            field["field_type"] = find_import(class_info["imports"], field["field_type"], class_info["package"])
            field["methodCalls"] = update_method_calls(class_info["imports"], [], field["methodCalls"], class_info["package"], class_info["class_name"])
                    
        for member_info in class_info["methods"]:
            if member_info["return_type"] != None and member_info["return_type"] != "void":
                member_info["return_type"] = find_import(class_info["imports"], member_info["return_type"], class_info["package"])

            ## arguments
            for param in member_info["formal_params"]:
                param["param_type"] = find_import(class_info["imports"], param["param_type"], class_info["package"])

            varss = []
            varss.extend([{
                "name": field["field_name"],
                "type": field["field_type"]
            } for field in class_info["fields"]])
            varss.extend([{
                "name": param["param_name"],
                "type": param["param_type"]
            } for param in member_info["formal_params"]])
            member_info["methodCalls"] = update_method_calls(class_info["imports"], varss, member_info["methodCalls"], class_info["package"], class_info["class_name"])

def generate_plantuml(classes):
    classPackageMap = {}
    for class_info in classes:
        package = class_info["package"]
        packageSplit = package.split(".")
        currentPackage = classPackageMap
        for name in packageSplit:
            if not currentPackage.get(name):
                currentPackage[name] = {}
            currentPackage = currentPackage[name]
        if not currentPackage.get("classes"):
            currentPackage["classes"] = []
        currentPackage["classes"].append(class_info)

    print('classPackageMap :', classPackageMap)
    
    plantuml_code = '@startuml\n'
    plantuml_code += generate_definition(classPackageMap)
    plantuml_code += '@enduml\n'
    
    return [plantuml_code, classPackageMap]

def parse_java_files_in_directory(directory_path):
    """
    Parse all Java files in a directory and return a list of their ASTs.
    """
    java_files = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".java"):
                java_files.append(os.path.join(root, file))
    return java_files

def main():
    # Directory containing Java source files
    directory_path = 'E:\\code\\spring-security-main\\spring-security-main\\core\\src\\main\\java'
    
    # Parse all Java files
    java_files = parse_java_files_in_directory(directory_path)
    
    # Parse each Java file into an AST and extract class information
    all_classes = []
    for java_file in java_files:
        print(f'Parsing {java_file}')
        classes = parse_java_file(java_file)
        all_classes.extend(classes)
    
    update_class_references_with_package_names(all_classes)
    # Generate PlantUML class diagram
    plantuml_code, classPackageMap = generate_plantuml(all_classes)

    
    # Print or save the PlantUML code
    # print(plantuml_code)
    # print('classes :', classes)
    with open("spring-security-core.puml", "w") as file:
        file.write(plantuml_code)

    classMap = {}
    for class_info in all_classes:
        classMap[f'{class_info["package"]}.{class_info["class_name"]}'] = class_info
    with open("spring-security-core.json", "w") as file:
        file.write(dumps(classMap))
    
if __name__ == '__main__':
    main()
