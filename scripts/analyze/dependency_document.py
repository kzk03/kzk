import os
import re
import xml.etree.ElementTree as ET
import json

# ---------- 依存情報抽出関数群 ----------

def extract_dependencies_from_pom(pom_file_path):
    """
    pom.xmlから<dependency>要素を解析し、"groupId:artifactId"形式の依存情報リストを返す
    """
    dependencies = []
    try:
        tree = ET.parse(pom_file_path)
        root = tree.getroot()
        # Maven POMでは名前空間が定義されているので注意
        ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
        for dep in root.findall(".//m:dependency", ns):
            group_id = dep.find("m:groupId", ns)
            artifact_id = dep.find("m:artifactId", ns)
            if group_id is not None and artifact_id is not None:
                token = f"{group_id.text}:{artifact_id.text}"
                dependencies.append(token)
    except Exception as e:
        print(f"Error parsing {pom_file_path}: {e}")
    return dependencies

def extract_dependencies_from_gradle(gradle_file_path):
    """
    Gradleファイル（build.gradleまたはbuild.gradle.kts）から、
    'group:artifact:version' のうち group:artifact 部分を正規表現で抽出する
    """
    dependencies = []
    pattern = re.compile(r"['\"]([^'\"]+:[^'\":]+):[^'\"]+['\"]")
    try:
        with open(gradle_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            matches = pattern.findall(content)
            dependencies.extend(matches)
    except Exception as e:
        print(f"Error reading {gradle_file_path}: {e}")
    return dependencies

def extract_dependencies_from_requirements(requirements_file_path):
    """
    requirements.txt からパッケージ名を抽出する
    (例："numpy==1.21.0" -> "numpy")
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
        print(f"Error reading {requirements_file_path}: {e}")
    return dependencies

def extract_dependencies_from_package_json(package_json_path):
    """
    package.jsonから、dependenciesおよびdevDependenciesのキーを抽出する
    """
    dependencies = []
    try:
        with open(package_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for dep_dict in [data.get("dependencies", {}), data.get("devDependencies", {})]:
                dependencies.extend(dep_dict.keys())
    except Exception as e:
        print(f"Error reading {package_json_path}: {e}")
    return dependencies

# ---------- 依存情報文書作成関数 ----------

def create_dependency_document(repo_dir):
    """
    指定されたリポジトリディレクトリ内にある各種依存関係ファイル（pom.xml, build.gradle, build.gradle.kts,
    requirements.txt, package.json）から依存情報を抽出し、重複を除いた上で統合し、
    空白区切りの1つの文字列（文書）として返す
    """
    all_dependencies = set()
    
    pom_path = os.path.join(repo_dir, "pom.xml")
    if os.path.exists(pom_path):
        deps = extract_dependencies_from_pom(pom_path)
        all_dependencies.update(deps)
    
    gradle_path = os.path.join(repo_dir, "build.gradle")
    if os.path.exists(gradle_path):
        deps = extract_dependencies_from_gradle(gradle_path)
        all_dependencies.update(deps)
    
    gradle_kts_path = os.path.join(repo_dir, "build.gradle.kts")
    if os.path.exists(gradle_kts_path):
        deps = extract_dependencies_from_gradle(gradle_kts_path)
        all_dependencies.update(deps)
    
    req_path = os.path.join(repo_dir, "requirements.txt")
    if os.path.exists(req_path):
        deps = extract_dependencies_from_requirements(req_path)
        all_dependencies.update(deps)
    
    package_json_path = os.path.join(repo_dir, "package.json")
    if os.path.exists(package_json_path):
        deps = extract_dependencies_from_package_json(package_json_path)
        all_dependencies.update(deps)
    
    # 依存情報のリストをソートして空白区切りの文字列に変換
    document = " ".join(sorted(all_dependencies))
    return document

# ---------- 例: 各リポジトリの依存情報文書を作成し、ファイルに保存する ----------

if __name__ == "__main__":
    # 各リポジトリの依存関係ファイルが保存されているディレクトリ（例）
    base_dir = "/Users/kazuki-h/newresearch/results/dependencies_files"
    
    # base_dir 内の各サブディレクトリごとに処理
    for repo_folder in os.listdir(base_dir):
        repo_path = os.path.join(base_dir, repo_folder)
        if os.path.isdir(repo_path):
            document = create_dependency_document(repo_path)
            # 結果を "dependency_document.txt" としてそのサブディレクトリに保存
            output_path = os.path.join(repo_path, "dependency_document.txt")
            with open(output_path, "w", encoding="utf-8") as out_f:
                out_f.write(document)
            print(f"Saved dependency document for {repo_folder} to {output_path}")
