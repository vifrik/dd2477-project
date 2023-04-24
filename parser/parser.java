import com.github.javaparser.ParseProblemException;
import com.github.javaparser.Range;
import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.PackageDeclaration;
import com.github.javaparser.ast.body.*;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.*;
import java.util.Optional;

public class Main {

    private static class JsonEntry extends VoidVisitorAdapter<Void> {

        JSONArray jsonArray = new JSONArray();

        public JSONArray getJson() {
            return jsonArray;
        }
    }

    private static JSONArray getPositionJson(Optional<Range> position) {
        if (position.isPresent()) {
            JSONArray positionJson = new JSONArray();
            positionJson.put(position.get().begin.line);
            positionJson.put(position.get().begin.column);
            positionJson.put(position.get().end.line);
            positionJson.put(position.get().end.column);
            return positionJson;
        }
        return null;
    }

    private static class ClassOrInterfaceVisitor extends JsonEntry {

        @Override
        public void visit(ClassOrInterfaceDeclaration classDeclaration, Void arg) {
            JSONObject jsonObject = new JSONObject();

            jsonObject.put("name", classDeclaration.getNameAsString());
            jsonObject.put("name_position", getPositionJson(classDeclaration.getName().getRange()));
            jsonObject.put("position", getPositionJson(classDeclaration.getRange()));

            JSONArray extends_list = new JSONArray();
            classDeclaration.getExtendedTypes().forEach(extended -> {
                JSONObject entry = new JSONObject();
                entry.put("name", extended.getName());
                entry.put("position", getPositionJson(extended.getRange()));
                extends_list.put(entry);
            });
            jsonObject.put("extends", extends_list);

            JSONArray modifiers = new JSONArray();
            classDeclaration.getModifiers().forEach(modifier -> {
                JSONObject entry = new JSONObject();
                entry.put("name", modifier.getKeyword());
                entry.put("position", getPositionJson(modifier.getRange()));
                modifiers.put(entry);
            });
            jsonObject.put("modifiers", modifiers);

            JSONArray annotations = new JSONArray();
            classDeclaration.getAnnotations().forEach(annotation -> {
                JSONObject entry = new JSONObject();
                entry.put("name", annotation.getNameAsString());
                entry.put("position", getPositionJson(annotation.getRange()));
                annotations.put(entry);
            });
            jsonObject.put("annotations", annotations);

            jsonArray.put(jsonObject);
        }
    }

    private static class MethodNameVisitor extends JsonEntry {

        @Override
        public void visit(MethodDeclaration methodDeclaration, Void arg) {
            JSONObject jsonObject = new JSONObject();

            jsonObject.put("name", methodDeclaration.getNameAsString());
            jsonObject.put("name_position",
                getPositionJson(methodDeclaration.getName().getRange()));
            jsonObject.put("return_type", methodDeclaration.getTypeAsString());
            jsonObject.put("return_type_position",
                getPositionJson(methodDeclaration.getType().getRange()));
            jsonObject.put("position", getPositionJson(methodDeclaration.getRange()));

            JSONArray modifiers = new JSONArray();
            methodDeclaration.getModifiers().forEach(modifier -> {
                JSONObject entry = new JSONObject();
                entry.put("name", modifier.getKeyword());
                entry.put("position", getPositionJson(modifier.getRange()));
                modifiers.put(entry);
            });
            jsonObject.put("modifiers", modifiers);

            JSONArray parameters = new JSONArray();
            methodDeclaration.getParameters().forEach(parameter -> {
                JSONObject entry = new JSONObject();
                entry.put("name", parameter.getNameAsString());
                entry.put("name_position",
                    getPositionJson(parameter.getName().getRange()));
                entry.put("type", parameter.getTypeAsString());
                entry.put("type_position",
                    getPositionJson(parameter.getType().getRange()));

                entry.put("position", getPositionJson(parameter.getRange()));
                parameters.put(entry);
            });
            jsonObject.put("parameters", parameters);

            JSONArray annotations = new JSONArray();
            methodDeclaration.getAnnotations().forEach(annotation -> {
                JSONObject entry = new JSONObject();
                entry.put("name", annotation.getNameAsString());
                entry.put("position", getPositionJson(annotation.getRange()));
                annotations.put(entry);
            });
            jsonObject.put("annotations", annotations);

            jsonArray.put(jsonObject);
        }
    }

    private static class FieldVisitorAdapter extends JsonEntry {

        @Override
        public void visit(FieldDeclaration fieldDeclaration, Void arg) {
            JSONObject jsonObject = new JSONObject();

            jsonObject.put("name", fieldDeclaration.getVariable(0).getNameAsString());
            jsonObject.put("name_position",
                getPositionJson(fieldDeclaration.getVariable(0).getRange()));
            jsonObject.put("type", fieldDeclaration.getVariable(0).getTypeAsString());
            jsonObject.put("type_position",
                getPositionJson(fieldDeclaration.getVariable(0).getType().getRange()));

            jsonObject.put("position", getPositionJson(fieldDeclaration.getRange()));

            JSONArray modifiers = new JSONArray();
            fieldDeclaration.getModifiers().forEach(modifier -> {
                JSONObject entry = new JSONObject();
                entry.put("name", modifier.getKeyword());
                entry.put("position", getPositionJson(modifier.getRange()));
                modifiers.put(entry);
            });
            jsonObject.put("modifiers", modifiers);

            jsonArray.put(jsonObject);
        }
    }

    private static class VariableNameVisitor extends JsonEntry {

        @Override
        public void visit(VariableDeclarator variableDeclarator, Void arg) {
            JSONObject jsonObject = new JSONObject();

            jsonObject.put("name", variableDeclarator.getNameAsString());
            jsonObject.put("name_position",
                getPositionJson(variableDeclarator.getName().getRange()));
            jsonObject.put("type", variableDeclarator.getTypeAsString());
            jsonObject.put("type_position",
                getPositionJson(variableDeclarator.getType().getRange()));

            jsonObject.put("position", getPositionJson(variableDeclarator.getRange()));

            jsonArray.put(jsonObject);
        }
    }

    private static JSONObject parseFile(String filepath) throws FileNotFoundException {
        CompilationUnit cu = StaticJavaParser.parse(new File(filepath));

        JSONObject metadata = new JSONObject();

        JSONArray imports = new JSONArray();
        cu.getImports().forEach(import_ -> {
            JSONObject entry = new JSONObject();
            entry.put("name", import_.getNameAsString());
            entry.put("name_position", getPositionJson(import_.getName().getRange()));
            entry.put("position", getPositionJson(import_.getRange()));
            imports.put(entry);
        });
        metadata.put("imports", imports);

        String package_string = "";
        JSONArray positionJson = new JSONArray();
        Optional<PackageDeclaration> pkg = cu.getPackageDeclaration();
        if (pkg.isPresent()) {
            package_string = pkg.get().getNameAsString();
            positionJson = getPositionJson(pkg.get().getRange());
        }
        metadata.put("package", package_string);
        metadata.put("package_position", positionJson);

        MethodNameVisitor methodNamesVisitor = new MethodNameVisitor();
        methodNamesVisitor.visit(cu, null);

        ClassOrInterfaceVisitor classOrInterfaceVisitor = new ClassOrInterfaceVisitor();
        classOrInterfaceVisitor.visit(cu, null);

        FieldVisitorAdapter fieldVisitorAdapter = new FieldVisitorAdapter();
        fieldVisitorAdapter.visit(cu, null);

        VariableNameVisitor variableNameVisitor = new VariableNameVisitor();
        variableNameVisitor.visit(cu, null);

        JSONObject result = new JSONObject();
        result.put("metadata", metadata);
        result.put("classes", classOrInterfaceVisitor.getJson());
        result.put("methods", methodNamesVisitor.getJson());
        result.put("fields", fieldVisitorAdapter.getJson());
        result.put("variables", variableNameVisitor.getJson());

        return result;
    }

    private static JSONArray parseFolder(String folderpath, String metadataPath)
        throws IOException {
        JSONArray result = new JSONArray();

        File metadata = new File(metadataPath);
        InputStream inputStream = new FileInputStream(metadata);
        String metadataContent = new String(inputStream.readAllBytes());
        JSONObject metadataJson = new JSONObject(metadataContent);

        File directory = new File(folderpath);
        File[] files = directory.listFiles();
        assert files != null;

        for (File file : files) {
            if (file.isFile()) {
                if (file.getName().endsWith(".java")) {
                    try {
                        JSONObject partialResult = parseFile(file.getAbsolutePath());
                        JSONObject fileContents = (JSONObject) metadataJson.get(file.getName());
                        JSONObject metadata_temp = (JSONObject) partialResult.get("metadata");
                        for (String key : JSONObject.getNames(fileContents)) {
                            metadata_temp.put(key, fileContents.get(key));
                        }
                        partialResult.put("metadata", metadata_temp);
                        result.put(partialResult);
                    } catch (FileNotFoundException e) {
                        System.err.printf("file: %s not found%n", file.getAbsolutePath());
                    } catch (ParseProblemException e) {
                        System.err.printf("file: %s failed to parse%n", file.getAbsolutePath());
                        System.err.println(e.getMessage());
                    }
                }
            }
        }
        return result;
    }

    public static void main(String[] args) throws IOException {
        if (args.length == 2) {
            JSONArray parsedFiles = parseFolder(args[0], args[1]);
            System.out.println(parsedFiles.toString(2));
        } else {
            System.err.printf("Expected 2 arguments, got %d%n", args.length);
        }
    }
}
