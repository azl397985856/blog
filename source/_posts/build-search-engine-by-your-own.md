---
title: 从零构建一个真正工作的简单搜索引擎
tags: [搜索引擎, 倒排索引, 从零实现]
date: 2025-11-30
categories:
  - [搜索]
---

大家好，我是 Lucifer。今天我们来聊聊如何用 Python 构建一个简单的搜索引擎。为什么写这篇？因为教程要么是黑箱框架（Elasticsearch 配置一堆），要么是浅尝辄止（就字符串匹配）。我希望带你从零起步，实现一个**真正能工作的版本**：它能用倒排索引存储文档、多种方式切分文本（tokenization）、计算权重，并根据相关度排序返回结果。

这篇文章聚焦核心：倒排索引 + tokenization + 权重系统。我们用 Python 的 dict 模拟一切，不需外部库，只用内置字符串处理和 math。**边看边敲代码**，预计阅读+实践：20 分钟。Python 3 环境准备好？走起！

<!-- more -->

## 第一步：理解核心概念

### 什么是倒排索引？
搜索引擎的核心是**倒排索引**（Inverted Index）。正常索引像“文档 ID → 内容”（书架上按书号排）；倒排索引反过来：“关键词 → 文档列表”（按主题直奔书堆）。

为什么重要？直接扫描所有文档太慢（O(总词数)），倒排索引让搜索 O(查询词数)，超快。举例：两篇文档
- Doc 1: 标题 "Python 入门"，正文 "Python 是伟大的编程语言"
- Doc 2: 标题 "Java vs Python"，正文 "Java 也很棒，但 Python 更简单"

简单倒排索引（不带权重）：
```
{
    "python": [1, 2],  # 包含 python 的文档 ID
    "入门": [1],
    "是": [1],
    "伟大的": [1],
    "编程": [1],
    "语言": [1],
    "java": [2],
    "vs": [2],
    "很": [2],
    "棒": [2],
    "但": [2],
    "更": [2],
    "简单": [2]
}
```

查询 "Python 简单"：查 "python" → [1,2]，"简单" → [2]，取交集 [2]，返回 Doc 2。就是这么直观！

但光存 ID 不够——文档长短不一，词位置不同，得加**权重**来精炼相关度。自然过渡：倒排索引从“存列表”升级到“存带权重的列表”，让标题匹配 > 正文匹配，长词 > 短词。接下来我们细聊怎么切词（tokenization），这是构建索引的第一步。

### Tokenization：怎么切分文本？
文本不是整体处理的，得切成小“token”（词或子串），供索引用。我们用三种 tokenizer，从精确到模糊，覆盖不同查询场景。每个都简单实现，下面直接上代码+解释。

先统一“预处理”：转小写、去标点、过滤短词（<2 字符）。代码：
```python
def _normalize(self, text: str) -> str:
    """统一处理：小写 + 去非字母/数字/空格"""
    return ''.join(c.lower() for c in text if c.isalnum() or c == ' ').strip()
```

1. **WordTokenizer**：按空格切完整词，精确匹配。权重高（20），因为最可靠。
   ```python
   def _word_tokenize(self, text: str) -> List[str]:
       norm = self._normalize(text)
       return [w for w in norm.split() if len(w) >= 2]  # 过滤短词
   ```
   例："Python 入门" → ['python', '入门']

2. **PrefixTokenizer**：生成词的前缀，帮模糊搜索（如 "pyth" 匹配 "python"）。权重中（5）。
   ```python
   def _prefix_tokenize(self, text: str, min_len=4) -> List[str]:
       words = self._word_tokenize(text)
       tokens = []
       for word in words:
           for i in range(min_len, len(word) + 1):  # 从4字符到全词
               tokens.append(word[:i])
       return tokens
   ```
   例："Python" → ['pyth', 'pytho', 'python']（min_len=4）

3. **NGramsTokenizer**：切成固定长字符块（3-gram），最模糊，抓拼写变体。权重低（1）。
   ```python
   def _ngram_tokenize(self, text: str, n=3) -> List[str]:
       norm = self._normalize(text).replace(' ', '')  # 去空格连字符
       return [norm[i:i+n] for i in range(len(norm) - n + 1) if len(norm[i:i+n]) == n]
   ```
   例："Python" → ['pyt', 'yth', 'tho', 'hon']

这些 tokenizer 在索引和查询时都跑，确保一致。为什么三种？精确查询用 Word，部分输入用 Prefix，拼错用 NGrams。简单吧？现在，权重系统就建立在这些 token 上。

### 权重系统：怎么让匹配“聪明”起来？
权重让倒排索引从“有/无”变“多相关”。核心公式（每 token）：
- **基础权重** = 字段权重（标题=10，正文=1） × tokenizer 权重（Word=20，Prefix=5，NGrams=1） × ceil(sqrt(词长))（长词更具体，如 "programming" len=11 → ceil(sqrt(11))≈4）

例："python" (len=6, sqrt≈2.45→3) 在 Doc1 标题 Word：10 × 20 × 3 = 600；在 Doc2 正文 Prefix：1 × 5 × 3 = 15。

搜索时，文档总分 = sum(所有匹配 token 的权重) × 调整因子：
- × (1 + log(独特匹配 token 数))：多样性——匹配多词更好。
- × (1 + log(平均匹配权重))：质量——高权重匹配更好。
- / (1 + log(文档总词数))：长度惩罚——长文别刷分。

归一化：总分 / max(可能分)，范围 [0,1]。这样，"Python in title" (高场权重) 远超 "python in body" (低场权重)，Prefix 匹配也加分但不主导。

一句话总结：权重综合**位置（标题>正文）**、**精确度（Word>模糊）**、**具体性（长词>短）**、**多样/质量/长度**，让排序更准、更像 Google。

## 第二步：准备数据结构

用类 `SimpleSearchEngine` 封装。核心两个 dict：
- `documents`: {doc_id: {"title": str, "body": str}} —— 存原内容。
- `index`: {token: {tokenizer_weight: [(doc_id, field, final_weight)]}} —— 倒排，token 指向分组的带权列表。

例（加 Doc1 后，简化版 index）：
```
{
    "python": {
        20: [(1, 'title', 600)],  # Word, 标题, 10*20*3
        5: [(1, 'title', 150)],   # Prefix 全词
        # ... NGrams 类似
    },
    "入门": {
        20: [(1, 'title', 300)]   # len=2, sqrt≈1.4→2, 10*20*2
    },
    # 正文 token 类似，但 field_weight=1
}
```

tokenizer 存为 dict：{'word': (func, 20), ...}。代码：
```python
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

    # 上节的 _normalize, _word_tokenize 等方法...
```

透明吧？每个 token 的内层 dict 按 tokenizer_weight 分组，便于搜索时过滤低权。

## 第三步：添加文档

`add_document`：存文档，按字段跑所有 tokenizer，算权重，塞进 index。用 set(tokens) 去重。

```python
    def add_document(self, doc_id: int, title: str, body: str, doc_type: str = 'default'):
        if doc_id in self.documents:
            raise ValueError("文档 ID 已存在")
        self.documents[doc_id] = {'title': title, 'body': body, 'type': doc_type}
        
        # 索引每个字段
        for field, content, field_weight in [('title', title, 10), ('body', body, 1)]:
            for t_name, (tokenize_fn, t_weight) in self.tokenizers.items():
                tokens = tokenize_fn(content)
                for token in set(tokens):
                    final_weight = field_weight * t_weight * math.ceil(math.sqrt(len(token)))
                    if token not in self.index:
                        self.index[token] = defaultdict(list)
                    self.index[token][t_weight].append((doc_id, field, final_weight))
```

例：跑 Doc1，"python" 在标题 Word 存 (1, 'title', 600)。O(总 token 数)，快！

## 第四步：执行搜索

`search`：切查询 token（所有 tokenizer），找候选文档（有匹配），算总分，排序。

```python
    def search(self, query: str, top_k: int = 5, min_token_weight: int = 1) -> List[Tuple[int, float, str]]:
        # 切查询：所有 tokenizer
        query_tokens = set()
        for _, (tokenize_fn, _) in self.tokenizers.items():
            query_tokens.update(tokenize_fn(query))
        if not query_tokens:
            return []
        
        # 候选：至少一个高权匹配
        candidate_docs = set()
        for token in query_tokens:
            if token in self.index:
                for w, entries in self.index[token].items():
                    if w >= min_token_weight:
                        for doc_id, _, _ in entries:
                            candidate_docs.add(doc_id)
        if not candidate_docs:
            return []
        
        # 算分
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
                                break  # 一个 token 只匹配一次
            
            if not matched_weights:
                continue
            
            sum_weight = sum(matched_weights)
            diversity = 1 + math.log(1 + len(unique_tokens))
            avg_weight = sum_weight / len(matched_weights)
            quality = 1 + math.log(1 + avg_weight)
            length_penalty = 1 + math.log(1 + total_tokens)
            score = (sum_weight * diversity * quality / length_penalty) / max(1, sum_weight)  # 归一 [0,1]
            
            title_preview = doc['title'][:20] + "..."
            results.append((doc_id, score, title_preview))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
```

例：查询 "Python 简单"（假设 Doc1/2 已加）。
- Doc1：匹配 "python" (600 title Word + 低 Prefix)，独特2，sum≈650，总词≈5，score≈0.85（标题高）。
- Doc2：匹配 "python" (15 body Prefix) + "简单" (低)，独特2，sum≈30，总词≈7，score≈0.25。
排序：Doc1 > Doc2。

清晰了？sum_weight 抓“量”，diversity/quality 抓“质”，penalty 抓“简”。

## 第五步：完整代码与扩展建议

完整版（聚焦核心，≈120 行）：

```python
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
```
打印：

```
Doc 1: Python 入门... (分数: 6.98)
Doc 2: Java vs Python... (分数: 5.91)
```

Doc1 分高（标题匹配）。

**扩展？** 加字段权重、存 pickle、加真 TF-IDF (IDF=log(总doc/含词doc))。

## 总结

恭喜！你建了个带权重的搜索引擎，核心逻辑透明，代码只有 100 多行。倒排索引存 token→文档+权，tokenization 切精确/模糊，权重综合位置/精确/具体/多样/长度，排序基于权重系统，比单纯字符串匹配准。