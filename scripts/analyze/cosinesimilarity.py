import os
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity
import csv

def main():
    # 各リポジトリのディレクトリが格納されているパス
    dependency_dir = "/Users/kazuki-h/newresearch/results/dependencies_files"
    
    documents = []
    repo_tags = []
    
    # 各リポジトリディレクトリ内の "dependency_document.txt" を読み込み、TaggedDocument に変換
    for repo_folder in tqdm(os.listdir(dependency_dir), desc="Processing repos for doc creation"):
        repo_path = os.path.join(dependency_dir, repo_folder)
        if os.path.isdir(repo_path):
            doc_file = os.path.join(repo_path, "dependency_document.txt")
            if os.path.exists(doc_file):
                with open(doc_file, "r", encoding="utf-8") as f:
                    doc = f.read()
                tokens = doc.split()  # 単純なトークン化
                if tokens:
                    documents.append(TaggedDocument(words=tokens, tags=[repo_folder]))
                    repo_tags.append(repo_folder)
            else:
                print(f"{doc_file} が見つかりませんでした。")
    
    print(f"Total repositories processed: {len(documents)}")
    
    # Doc2Vec モデルの学習
    model = Doc2Vec(vector_size=100, window=5, min_count=1, workers=4, epochs=40)
    model.build_vocab(documents)
    print("Vocabulary built.")
    model.train(documents, total_examples=model.corpus_count, epochs=model.epochs)
    print("Doc2Vec model trained.")
    
    # 各リポジトリのベクトルを取得
    repo_vectors = { tag: model.dv[tag] for tag in repo_tags }
    
    # 固定するリポジトリタグを指定（実際のディレクトリ名に合わせる）
    fixed_tag = "apache_zookeeper"
    if fixed_tag not in repo_vectors:
        print(f"固定リポジトリタグ '{fixed_tag}' が見つかりませんでした。")
        return

    fixed_vector = repo_vectors[fixed_tag].reshape(1, -1)
    
    # 結果保存用のCSVファイルを用意
    output_csv = "similarity_results_final.csv"
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Fixed Repository", "Compared Repository", "Cosine Similarity"])
        
        print(f"\n固定リポジトリ '{fixed_tag}' と全リポジトリの類似度を計算します:")
        for tag, vector in tqdm(repo_vectors.items(), desc="Computing similarities", unit="repo"):
            if tag == fixed_tag:
                continue
            vec = vector.reshape(1, -1)
            similarity = cosine_similarity(fixed_vector, vec)[0][0]
            writer.writerow([fixed_tag, tag, f"{similarity:.4f}"])
            print(f"{fixed_tag} と {tag} のコサイン類似度: {similarity:.4f}")
    
    print(f"\n類似度結果が {output_csv} に保存されました。")

if __name__ == "__main__":
    main()