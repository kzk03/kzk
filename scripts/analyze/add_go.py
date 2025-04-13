import os
import re
import json
import xml.etree.ElementTree as ET
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity
import csv

# ---------- Go: go.mod 解析 ----------

def parse_go_mod(go_mod_path):
    """
    go.mod から require 行を抽出し、依存パッケージ名のリストを返す。
    簡易実装のため、'replace' 等は未考慮。
    """
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
        print(f"[WARN] Error reading {go_mod_path}: {e}")
    return list(set(deps))

# ---------- Go: go.sum 解析 ----------

def parse_go_sum(go_sum_path):
    """
    go.sum からパッケージ名を抽出し、リストを返す。
    例:
        github.com/pkg/errors v0.9.1 h1:xxxx
        github.com/pkg/errors v0.9.1/go.mod h1:xxxx
    最初のトークンが "github.com/pkg/errors" or "github.com/pkg/errors v0.9.1/go.mod" などになるので、
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
                    # parts[0] 例: "github.com/pkg/errors", "github.com/pkg/errors v0.9.1/go.mod"...
                    pkg = parts[0]
                    # "/go.mod" が含まれていれば除去
                    pkg = pkg.replace("/go.mod", "")
                    deps.append(pkg)
    except Exception as e:
        print(f"[WARN] Error reading {go_sum_path}: {e}")
    return list(set(deps))

# ---------- Maven/Gradle/Python/npm 解析 ----------

def extract_dependencies_from_pom(pom_file_path):
    """
    pom.xmlから<dependency>要素を解析し、"groupId:artifactId"形式の依存情報をリストで返す
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
        print(f"[WARN] Error parsing {pom_file_path}: {e}")
    return dependencies

def extract_dependencies_from_gradle(gradle_file_path):
    """
    Gradleファイル（build.gradleまたはbuild.gradle.kts）から
    'group:artifact:version' のうち group:artifact 部分を正規表現で抽出
    """
    dependencies = []
    pattern = re.compile(r"['\"]([^'\"]+:[^'\":]+):[^'\"]+['\"]")
    try:
        with open(gradle_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            matches = pattern.findall(content)
            dependencies.extend(matches)
    except Exception as e:
        print(f"[WARN] Error reading {gradle_file_path}: {e}")
    return dependencies

def extract_dependencies_from_requirements(requirements_file_path):
    """
    requirements.txt からパッケージ名を抽出する (例: "numpy==1.21.0" -> "numpy")
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
        print(f"[WARN] Error reading {requirements_file_path}: {e}")
    return dependencies

def extract_dependencies_from_package_json(package_json_path):
    """
    package.jsonから、dependencies および devDependencies のキーを抽出
    """
    dependencies = []
    try:
        with open(package_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for dep_dict in [data.get("dependencies", {}), data.get("devDependencies", {})]:
                dependencies.extend(dep_dict.keys())
    except Exception as e:
        print(f"[WARN] Error reading {package_json_path}: {e}")
    return dependencies

# ---------- 依存関係ドキュメント作成 ----------

def create_dependency_document(repo_dir):
    """
    go.mod, go.sum, pom.xml, build.gradle, requirements.txt, package.json などを解析し、
    依存パッケージの重複を除いて空白区切り文字列として返す
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

    # Gradle: build.gradle, build.gradle.kts
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

    # 重複除外 & ソート & スペース区切り
    return " ".join(sorted(all_deps))

def main():
    """
    go.mod, go.sum を含むビルドファイルからの依存情報をDoc2Vecでベクトル化し、
    指定したリポジトリとのコサイン類似度を出力するメインフロー
    """
    from gensim.models.doc2vec import TaggedDocument, Doc2Vec
    from tqdm import tqdm
    from sklearn.metrics.pairwise import cosine_similarity

    # 1. リポジトリが格納されたディレクトリを指定
    base_dir = "/Users/kazuki-h/newresearch/results/dependencies_files"  # ★適宜変更してください

    # 2. リポジトリ一覧を取得
    repo_folders = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]

    # 3. 依存情報ドキュメントを作成
    documents = []
    repo_tags = []
    for repo_folder in tqdm(repo_folders, desc="Creating dependency documents"):
        repo_path = os.path.join(base_dir, repo_folder)
        dep_doc = create_dependency_document(repo_path)  # go.mod, go.sum などを含む
        tokens = dep_doc.split()
        if tokens:  # 依存情報が空でなければ
            documents.append(TaggedDocument(words=tokens, tags=[repo_folder]))
            repo_tags.append(repo_folder)

    print(f"Total repositories processed: {len(documents)}")

    # 4. Doc2Vec モデルを学習
    model = Doc2Vec(vector_size=100, window=5, min_count=1, workers=4, epochs=40)
    model.build_vocab(documents)
    print("Vocabulary built.")
    model.train(documents, total_examples=model.corpus_count, epochs=model.epochs)
    print("Doc2Vec model trained.")

    # 5. 特定リポジトリを固定してコサイン類似度を出す
    repo_vectors = { tag: model.dv[tag] for tag in repo_tags }

    fixed_tag = "apache_zookeeper"  # 例: ここに比較基準としたいリポジトリフォルダ名を設定
    if fixed_tag not in repo_vectors:
        print(f"[ERROR] Fixed repository '{fixed_tag}' not found in processed repos.")
        return

    fixed_vector = repo_vectors[fixed_tag].reshape(1, -1)

    # 6. 結果をCSVに書き出し
    output_csv = "similarity_results_all2.csv"
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Fixed Repository", "Compared Repository", "Cosine Similarity"])

        for tag, vec in repo_vectors.items():
            if tag == fixed_tag:
                continue
            similarity = cosine_similarity(fixed_vector, vec.reshape(1, -1))[0][0]
            writer.writerow([fixed_tag, tag, f"{similarity:.4f}"])
            print(f"Cosine similarity between {fixed_tag} and {tag}: {similarity:.4f}")

    print(f"\nSimilarity results saved to {output_csv}")

if __name__ == "__main__":
    main()
