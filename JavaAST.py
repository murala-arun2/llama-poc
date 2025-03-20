from antlr4 import *
from JavaLexer import JavaLexer
from JavaParser import JavaParser
from JavaParserListener import JavaParserListener
import os

class JavaASTListener(JavaParserListener):
    def __init__(self):
        self.classMap = {}
        self.classes = []
        self.packageName = None

    def enterPackageDeclaration(self, ctx):
        self.packageName = ctx.qualifiedName().getText()
        print('package name: ', self.packageName)
        # return super().enterPackageDeclaration(ctx)
    
    def enterInterfaceDeclaration(self, ctx):
        interface_name = ctx.identifier().getText()
        print('interface name: ', interface_name)
        class_info = {
            'class_name': interface_name,
            'class_type': 'interface',
            'package': self.packageName,
            'implementz': [],
            'extendz': None,
            'fields': [],
            'methods': []
        }
        self.classes.append(class_info)
        # return super().enterInterfaceDeclaration(ctx)

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
        formal_params = [[param.variableDeclaratorId().getText(), param.typeType().getText()] for param in ctx.interfaceCommonBodyDeclaration().formalParameters().formalParameterList().formalParameter()] if ctx.interfaceCommonBodyDeclaration().formalParameters().formalParameterList() else []
        print(method_name, return_type, formal_params)
        if self.classes:
            self.classes[-1]['methods'].append([method_name, return_type, formal_params])
            # print('self.classes[-1]: ', self.classes[-1])

    def enterInterfaceMethodDeclaration(self, ctx):
        print('ctx interface method text: ', ctx.getText(), dir(ctx.interfaceCommonBodyDeclaration()))
        method_name = ctx.interfaceCommonBodyDeclaration().identifier().getText()
        return_type = ctx.interfaceCommonBodyDeclaration().typeTypeOrVoid().getText()
        formal_params = [[param.variableDeclaratorId().getText(), param.typeType().getText()] for param in ctx.interfaceCommonBodyDeclaration().formalParameters().formalParameterList().formalParameter()] if ctx.interfaceCommonBodyDeclaration().formalParameters().formalParameterList() else []
        print(method_name, return_type, formal_params)
        if self.classes:
            self.classes[-1]['methods'].append([method_name, return_type, formal_params])
        # return super().enterInterfaceMethodDeclaration(ctx)
    

    def enterClassDeclaration(self, ctx:JavaParser.ClassDeclarationContext):
        # Extract class name
        print('ctx class text: ', ctx.identifier().getText())
        class_name = ctx.identifier().getText()
        implementz = [implement.getText() for implement in ctx.typeList()] if ctx.typeList() else []
        print('implements:', implementz)
        extendz = ctx.typeType().getText() if ctx.typeType() else None
        print('extends:', extendz)
        class_info = {
            'class_name': class_name,
            'class_type': 'class',
            'package': self.packageName,
            'implementz': implementz,
            'extendz': extendz,
            'fields': [],
            'methods': []
        }
        self.classes.append(class_info)

    def enterFieldDeclaration(self, ctx:JavaParser.FieldDeclarationContext):
        # Extract field names (attributes)
        print('ctx field text: ', ctx.getText())
        # print('ctx.variableDeclarators().variableDeclarator() : ', ctx.variableDeclarators().variableDeclarator())
        # [print('variable declarator', ctx.typeType().getText(), declarator.variableDeclaratorId().identifier().getText(), dir(declarator.variableDeclaratorId())) for declarator in ctx.variableDeclarators().variableDeclarator()]
        # [print(, declarator.get) for declarator in ctx.variableDeclarators().variableDeclarator()]
        fields = [[declarator.variableDeclaratorId().identifier().getText(), ctx.typeType().getText()] for declarator in ctx.variableDeclarators().variableDeclarator()]
        if self.classes:
            self.classes[-1]['fields'].extend(fields)

    def enterMethodDeclaration(self, ctx:JavaParser.MethodDeclarationContext):
        # Extract method names
        print('ctx method text: ', ctx.identifier().getText())
        method_name = ctx.identifier().getText()
        return_type = ctx.typeTypeOrVoid().getText()
        formal_params = [[param.variableDeclaratorId().getText(), param.typeType().getText()] for param in ctx.formalParameters().formalParameterList().formalParameter()] if ctx.formalParameters().formalParameterList() else []
        print(method_name, return_type, formal_params)
        if self.classes:
            self.classes[-1]['methods'].append([method_name, return_type, formal_params])

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

def generate_plantuml(classes):
    plantuml_code = '@startuml\n'

    for class_info in classes:
        # Define the class
        plantuml_code += f'{class_info["class_type"]} {class_info['package']}.{class_info["class_name"]} {'extends '+class_info['extendz'] if class_info['extendz'] else ''} {'implements '+(','.join(class_info['implementz'])) if len(class_info['implementz']) > 0 else ''}  {{\n'

        # Add fields
        for field in class_info['fields']:
            plantuml_code += f'  {field[0]} : {field[1]}\n'  # Defaulting type to String for simplicity

        # Add methods
        for method in class_info['methods']:
            plantuml_code += f'  {method[0]}({", ".join([param[1]+" "+param[0] for param in method[2]])}) : {method[1]}\n'  # Defaulting to void for simplicity

        plantuml_code += '}\n'

    plantuml_code += '@enduml\n'
    
    return plantuml_code

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
    
    # Generate PlantUML class diagram
    plantuml_code = generate_plantuml(all_classes)
    
    # Print or save the PlantUML code
    # print(plantuml_code)
    print('classes :', classes)
    with open("output.puml", "w") as file:
        file.write(plantuml_code)

if __name__ == '__main__':
    main()
