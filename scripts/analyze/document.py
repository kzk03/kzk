import os
import re
import json
import xml.etree.ElementTree as ET

def parse_go_mod(go_mod_path):
    """
    go.mod から require 行を抽出し、依存パッケージ名のリストを返す。
    簡易実装のため、replace や exclude は未対応。
    """
    import re
    deps = []
    require_pattern = re.compile(r'^\s*require\s+([^\s]+)\s+[\w\d\.-]+')
    block_pattern_start = re.compile(r'^\s*require\s*\(')
    block_pattern_end = re.compile(r'^\s*\)')
    line_pattern = re.compile(r'^\s*([^\s]+)\s+([\w\d\.-]+)')  # "pkg version"

    block_mode = False
    try:
        with open(go_mod_path, 'r', encoding='utf-8') as f:
            for line in f:
                line_stripped = line.strip()
                # 単一行: require github.com/foo/bar v1.2.3
                single_match = require_pattern.search(line_stripped)
                if single_match:
                    deps.append(single_match.group(1))
                    continue

                # ブロック開始: require (
                if block_pattern_start.search(line_stripped):
                    block_mode = True
                    continue
                # ブロック終了: )
                if block_mode and block_pattern_end.search(line_stripped):
                    block_mode = False
                    continue

                # ブロック内
                if block_mode:
                    m = line_pattern.search(line_stripped)
                    if m:
                        pkg_name = m.group(1)
                        deps.append(pkg_name)
    except Exception as e:
        print(f"[WARN] Error reading go.mod: {go_mod_path} => {e}")
    return list(set(deps))

def parse_go_sum(go_sum_path):
    """
    go.sum からパッケージ名を抽出し、リストを返す。
    例:
        github.com/pkg/errors v0.9.1 h1:xxxx
        github.com/pkg/errors v0.9.1/go.mod h1:xxxx
    最初のトークンが "github.com/pkg/errors" or "github.com/pkg/errors v0.9.1/go.mod"...
    "/go.mod" を削除して同一パッケージ扱いとする。
    """
    deps = []
    try:
        with open(go_sum_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) >= 1:
                    pkg = parts[0]
                    pkg = pkg.replace("/go.mod", "")  # "/go.mod"を削除
                    deps.append(pkg)
    except Exception as e:
        print(f"[WARN] Error reading go.sum: {go_sum_path} => {e}")
    return list(set(deps))

def extract_dependencies_from_pom(pom_file_path):
    """
    pom.xml から <dependency>要素を解析し、"groupId:artifactId"形式の依存情報を返す
    """
    dependencies = []
    try:
        tree = ET.parse(pom_file_path)
        root = tree.getroot()
        ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
        for dep in root.findall(".//m:dependency", ns):
            group_id = dep.find("m:groupId", ns)
            artifact_id = dep.find("m:artifactId", ns)
            if group_id is not None and artifact_id is not None:
                token = f"{group_id.text}:{artifact_id.text}"
                dependencies.append(token)
    except Exception as e:
        print(f"[WARN] Error parsing pom.xml: {pom_file_path} => {e}")
    return dependencies

def extract_dependencies_from_gradle(gradle_file_path):
    """
    build.gradle や build.gradle.kts から 'group:artifact:version' のうち group:artifact を抽出
    """
    import re
    dependencies = []
    pattern = re.compile(r"['\"]([^'\"]+:[^'\":]+):[^'\"]+['\"]")
    try:
        with open(gradle_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            matches = pattern.findall(content)
            dependencies.extend(matches)
    except Exception as e:
        print(f"[WARN] Error reading gradle file: {gradle_file_path} => {e}")
    return dependencies

def extract_dependencies_from_requirements(requirements_file_path):
    """
    requirements.txt から "numpy==1.21.0" のような行を "numpy" だけ抽出する
    """
    dependencies = []
    try:
        with open(requirements_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    pkg = line.split("==")[0]
                    dependencies.append(pkg)
    except Exception as e:
        print(f"[WARN] Error reading requirements.txt: {requirements_file_path} => {e}")
    return dependencies

def extract_dependencies_from_package_json(package_json_path):
    """
    package.json から dependencies, devDependencies のキーを抽出
    """
    dependencies = []
    try:
        import json
        with open(package_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for dep_dict in [data.get("dependencies", {}), data.get("devDependencies", {})]:
                dependencies.extend(dep_dict.keys())
    except Exception as e:
        print(f"[WARN] Error reading package.json: {package_json_path} => {e}")
    return dependencies

def create_dependency_document(repo_dir):
    """
    リポジトリディレクトリ内にある go.mod, go.sum, pom.xml, build.gradle, build.gradle.kts,
    requirements.txt, package.json を解析し、依存関係を重複排除した上で
    空白区切り文字列として返す
    """
    all_deps = set()

    # Go: go.mod
    go_mod_path = os.path.join(repo_dir, "go.mod")
    if os.path.exists(go_mod_path):
        all_deps.update(parse_go_mod(go_mod_path))

    # Go: go.sum
    go_sum_path = os.path.join(repo_dir, "go.sum")
    if os.path.exists(go_sum_path):
        all_deps.update(parse_go_sum(go_sum_path))

    # Maven: pom.xml
    pom_path = os.path.join(repo_dir, "pom.xml")
    if os.path.exists(pom_path):
        all_deps.update(extract_dependencies_from_pom(pom_path))

    # Gradle: build.gradle / build.gradle.kts
    gradle_path = os.path.join(repo_dir, "build.gradle")
    if os.path.exists(gradle_path):
        all_deps.update(extract_dependencies_from_gradle(gradle_path))

    gradle_kts_path = os.path.join(repo_dir, "build.gradle.kts")
    if os.path.exists(gradle_kts_path):
        all_deps.update(extract_dependencies_from_gradle(gradle_kts_path))

    # Python: requirements.txt
    req_path = os.path.join(repo_dir, "requirements.txt")
    if os.path.exists(req_path):
        all_deps.update(extract_dependencies_from_requirements(req_path))

    # Node.js: package.json
    package_json_path = os.path.join(repo_dir, "package.json")
    if os.path.exists(package_json_path):
        all_deps.update(extract_dependencies_from_package_json(package_json_path))

    # ソートして空白区切りに
    doc_str = " ".join(sorted(all_deps))
    return doc_str

def main():
    """
    go.mod, go.sum を含む各種ビルドファイルを解析し、
    依存関係ドキュメント "dependency_document.txt" をリポジトリごとに保存する
    """
    # リポジトリが格納されたベースディレクトリ
    base_dir = "/Users/kazuki-h/newresearch/results/dependencies_files"  # ★適宜変更してください

    # base_dir 内のサブフォルダをリポジトリとみなす
    for repo_folder in os.listdir(base_dir):
        repo_path = os.path.join(base_dir, repo_folder)
        if os.path.isdir(repo_path):
            # 依存関係抽出
            dep_doc = create_dependency_document(repo_path)

            # テキストが空でなければファイル保存
            if dep_doc.strip():
                output_path = os.path.join(repo_path, "dependency_document.txt")
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(dep_doc)
                print(f"[INFO] Saved dependency_document.txt for '{repo_folder}' -> {output_path}")
            else:
                print(f"[INFO] No dependencies found for '{repo_folder}'")

if __name__ == "__main__":
    main()
