from collections import defaultdict
import math
from typing import Dict, List, Tuple, Any

class SimpleSearchEngine:
    def __init__(self):
        self.documents: Dict[int, Dict[str, Any]] = {}
        self.index: Dict[str, Dict[int, List[Tuple[int, str, int]]]] = {}
        self.tokenizers = {
            'word': (self._word_tokenize, 20),
            'prefix': (self._prefix_tokenize, 5),
            'ngram': (self._ngram_tokenize, 1)
        }

    def _normalize(self, text: str) -> str:
        return ''.join(c.lower() for c in text if c.isalnum() or c == ' ').strip()

    def _word_tokenize(self, text: str) -> List[str]:
        norm = self._normalize(text)
        return [w for w in norm.split() if len(w) >= 2]

    def _prefix_tokenize(self, text: str, min_len=4) -> List[str]:
        words = self._word_tokenize(text)
        tokens = []
        for word in words:
            for i in range(min_len, len(word) + 1):
                tokens.append(word[:i])
        return tokens

    def _ngram_tokenize(self, text: str, n=3) -> List[str]:
        norm = self._normalize(text).replace(' ', '')
        return [norm[i:i+n] for i in range(len(norm) - n + 1) if len(norm[i:i+n]) == n]

    def add_document(self, doc_id: int, title: str, body: str, doc_type: str = 'default'):
        if doc_id in self.documents:
            raise ValueError("文档 ID 已存在")
        self.documents[doc_id] = {'title': title, 'body': body, 'type': doc_type}
        for field, content, field_weight in [('title', title, 10), ('body', body, 1)]:
            for t_name, (tokenize_fn, t_weight) in self.tokenizers.items():
                tokens = tokenize_fn(content)
                for token in set(tokens):
                    final_weight = field_weight * t_weight * math.ceil(math.sqrt(len(token)))
                    if token not in self.index:
                        self.index[token] = defaultdict(list)
                    self.index[token][t_weight].append((doc_id, field, final_weight))

    def search(self, query: str, top_k: int = 5, min_token_weight: int = 1) -> List[Tuple[int, float, str]]:
        query_tokens = set()
        for _, (tokenize_fn, _) in self.tokenizers.items():
            query_tokens.update(tokenize_fn(query))
        if not query_tokens:
            return []
        candidate_docs = set()
        for token in query_tokens:
            if token in self.index:
                for w, entries in self.index[token].items():
                    if w >= min_token_weight:
                        for doc_id, _, _ in entries:
                            candidate_docs.add(doc_id)
        if not candidate_docs:
            return []
        results = []
        for doc_id in candidate_docs:
            doc = self.documents[doc_id]
            total_tokens = len(self._word_tokenize(doc['title'] + ' ' + doc['body']))
            matched_weights = []
            unique_tokens = set()
            for token in query_tokens:
                if token in self.index:
                    for w, entries in self.index[token].items():
                        for d_id, _, weight in entries:
                            if d_id == doc_id:
                                matched_weights.append(weight)
                                unique_tokens.add(token)
                                break
            if not matched_weights:
                continue
            sum_weight = sum(matched_weights)
            diversity = 1 + math.log(1 + len(unique_tokens))
            avg_weight = sum_weight / len(matched_weights)
            quality = 1 + math.log(1 + avg_weight)
            length_penalty = 1 + math.log(1 + total_tokens)
            score = (sum_weight * diversity * quality / length_penalty) / max(1, sum_weight)
            title_preview = doc['title'][:20] + "..."
            results.append((doc_id, score, title_preview))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

# 测试
if __name__ == "__main__":
    engine = SimpleSearchEngine()
    engine.add_document(1, "Python 入门", "Python 是伟大的编程语言", 'article')
    engine.add_document(2, "Java vs Python", "Java 也很棒，但 Python 更简单", 'article')
    results = engine.search("Python 简单")
    for doc_id, score, title in results:
        print(f"Doc {doc_id}: {title} (分数: {score:.2f})")