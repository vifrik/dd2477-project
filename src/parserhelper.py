import json
import subprocess


class ParserHelper:
    class Utils:
        # https://stackoverflow.com/questions/8230315/how-to-json-serialize-sets
        def serialize_sets(obj):
            if isinstance(obj, set):
                return list(obj)

    def __init__(self, parser_path, folder_path, metadata_path):
        self.parser_path = parser_path
        self.folder_path = folder_path
        self.metadata_path = metadata_path

    def parse_folder(self):
        result = subprocess.run(["java", "-jar", self.parser_path, self.folder_path, self.metadata_path], capture_output=True, text=True)
        if result.stderr:
            print(result.stderr)
        return json.loads(result.stdout)


if __name__ == "__main__":
    parser = ParserHelper("../parser/bin/parser.jar", "data/java", "data/java/metadata.json")
    json_obj = parser.parse_folder()
    print(json_obj)
