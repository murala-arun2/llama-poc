from json import loads
def get_file_contents(file_name):
    file_contents = None
    with open(file_name, 'r') as f:
        file_contents = f.read()
    return file_contents