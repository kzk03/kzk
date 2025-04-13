import os
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity
import csv

def main():
    # 1. リポジトリが格納されたベースディレクトリ
    #    各サブフォルダ(=リポジトリ) に "dependency_document.txt" がある想定
    base_dir = "/Users/kazuki-h/newresearch/results/dependencies_files"

    # 比較したい2つのリポジトリフォルダ名
    repoA = "apache_zookeeper"
    repoB = "brianfrankcooper_YCSB"

    documents = []
    repo_tags = []

    # 2. dependency_document.txt を読み込んで TaggedDocument を作成
    for repo_folder in tqdm(os.listdir(base_dir), desc="Loading dependency documents"):
        repo_path = os.path.join(base_dir, repo_folder)
        if not os.path.isdir(repo_path):
            continue

        doc_path = os.path.join(repo_path, "dependency_document.txt")
        if not os.path.exists(doc_path):
            # dependency_document.txt が無ければスキップ
            continue

        # 依存関係の文字列を読み込み
        with open(doc_path, "r", encoding="utf-8") as f:
            dep_str = f.read().strip()

        tokens = dep_str.split()
        if tokens:
            # Doc2Vec 用に TaggedDocument を作る
            documents.append(TaggedDocument(words=tokens, tags=[repo_folder]))
            repo_tags.append(repo_folder)

    print(f"Total repositories processed: {len(documents)}")

    # 3. Doc2Vec モデルを学習
    model = Doc2Vec(vector_size=100, window=5, min_count=1, workers=4, epochs=40)
    model.build_vocab(documents)
    print("Vocabulary built.")
    model.train(documents, total_examples=model.corpus_count, epochs=model.epochs)
    print("Doc2Vec model trained.")

    # 4. リポジトリのベクトルを取得
    repo_vectors = { tag: model.dv[tag] for tag in repo_tags }

    # 5. repoA, repoB が存在するかチェック
    if repoA not in repo_vectors:
        print(f"[ERROR] Repository '{repoA}' not found in doc list.")
        return
    if repoB not in repo_vectors:
        print(f"[ERROR] Repository '{repoB}' not found in doc list.")
        return

    vecA = repo_vectors[repoA].reshape(1, -1)
    vecB = repo_vectors[repoB].reshape(1, -1)

    # 6. コサイン類似度を計算
    similarity = cosine_similarity(vecA, vecB)[0][0]
    print(f"Cosine similarity between {repoA} and {repoB}: {similarity:.4f}")

    # 7. CSVに書き出し（1行だけ）
    output_csv = "similarity_two_repos.csv"
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["RepositoryA", "RepositoryB", "Cosine Similarity"])
        writer.writerow([repoA, repoB, f"{similarity:.4f}"])

    print(f"Result saved to {output_csv}")

if __name__ == "__main__":
    main()
