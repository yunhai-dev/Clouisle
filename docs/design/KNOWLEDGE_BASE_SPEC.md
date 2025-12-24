# Clouisle 知识库规范

## 1. 概述

本文档定义了 Clouisle 项目中知识库（Knowledge Base）功能的设计规范，用于实现 RAG（Retrieval-Augmented Generation）能力。

### 1.1 设计目标

- **团队隔离**：知识库归属于团队，实现数据隔离
- **格式丰富**：支持多种文档格式
- **智能处理**：自动文本提取、分块和向量化
- **高效检索**：基于向量的语义搜索

### 1.2 技术选型

| 功能 | 技术方案 | 说明 |
|------|----------|------|
| 文档解析 | MarkItDown | 微软开源，统一转换为 Markdown |
| 文本分块 | 自研 TextChunker | 语义感知分块 |
| 向量存储 | pgvector | PostgreSQL 扩展 |
| 向量生成 | LangChain Embeddings | 复用 LLM 模块 |
| 异步处理 | Celery | 大文档异步处理 |

---

## 2. 支持的文档格式

### 2.1 MarkItDown 处理的格式

| 格式 | 扩展名 | MIME Type | 说明 |
|------|--------|-----------|------|
| PDF | `.pdf` | `application/pdf` | 需要 `markitdown[pdf]` |
| Word | `.docx`, `.doc` | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | 内置支持 |
| PowerPoint | `.pptx` | `application/vnd.openxmlformats-officedocument.presentationml.presentation` | 内置支持 |
| Excel | `.xlsx` | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | 需要 `markitdown[xlsx]` |
| Excel (旧版) | `.xls` | `application/vnd.ms-excel` | 需要 `markitdown[xls]` |
| HTML | `.html`, `.htm` | `text/html` | 内置支持 |
| URL | - | - | 支持网页和 YouTube |

### 2.2 标准库处理的格式

| 格式 | 扩展名 | MIME Type | 说明 |
|------|--------|-----------|------|
| 纯文本 | `.txt` | `text/plain` | 直接读取 |
| Markdown | `.md`, `.markdown` | `text/markdown` | 直接读取 |
| CSV | `.csv` | `text/csv` | Python csv 模块 |
| JSON | `.json` | `application/json` | Python json 模块 |

### 2.3 MarkItDown 可选依赖

```bash
# 安装所有可选依赖
pip install 'markitdown[all]'

# 或按需安装
pip install 'markitdown[pdf]'       # PDF 支持
pip install 'markitdown[docx]'      # Word 支持 (可选增强)
pip install 'markitdown[pptx]'      # PowerPoint 支持 (可选增强)
pip install 'markitdown[xlsx]'      # Excel 支持
pip install 'markitdown[xls]'       # 旧版 Excel 支持
pip install 'markitdown[outlook]'   # Outlook 邮件
pip install 'markitdown[audio-transcription]'    # 音频转录
pip install 'markitdown[youtube-transcription]'  # YouTube 字幕
```

---

## 3. 数据模型

### 3.1 知识库 (KnowledgeBase)

```python
class KnowledgeBase(Model):
    id: UUID
    team_id: UUID              # 所属团队
    name: str                  # 知识库名称
    description: str           # 描述
    embedding_model_id: UUID   # 使用的向量模型
    chunk_size: int = 500      # 分块大小 (tokens)
    chunk_overlap: int = 50    # 分块重叠
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
```

### 3.2 文档 (Document)

```python
class DocumentStatus(str, Enum):
    PENDING = "pending"        # 待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"    # 完成
    FAILED = "failed"          # 失败

class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    TXT = "txt"
    MD = "md"
    HTML = "html"
    CSV = "csv"
    XLSX = "xlsx"
    XLS = "xls"
    JSON = "json"
    URL = "url"

class Document(Model):
    id: UUID
    knowledge_base_id: UUID
    name: str                  # 文档名称
    file_path: str             # 存储路径
    file_size: int             # 文件大小
    doc_type: DocumentType
    status: DocumentStatus
    chunk_count: int = 0       # 分块数量
    error_message: str         # 错误信息
    metadata: dict             # 元数据
    created_at: datetime
    updated_at: datetime
```

### 3.3 文档分块 (DocumentChunk)

```python
class DocumentChunk(Model):
    id: UUID
    document_id: UUID
    content: str               # 文本内容
    chunk_index: int           # 分块序号
    token_count: int           # Token 数量
    embedding: list[float]     # 向量 (pgvector)
    metadata: dict             # 元数据
    created_at: datetime
```

---

## 4. API 接口

### 4.1 知识库管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/knowledge-bases` | 列表 |
| POST | `/api/v1/knowledge-bases` | 创建 |
| GET | `/api/v1/knowledge-bases/{id}` | 详情 |
| PUT | `/api/v1/knowledge-bases/{id}` | 更新 |
| DELETE | `/api/v1/knowledge-bases/{id}` | 删除 |
| GET | `/api/v1/knowledge-bases/{id}/stats` | 统计 |
| POST | `/api/v1/knowledge-bases/{id}/search` | 搜索 |

### 4.2 文档管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/knowledge-bases/{kb_id}/documents` | 文档列表 |
| POST | `/api/v1/knowledge-bases/{kb_id}/documents/upload` | 上传文档 |
| POST | `/api/v1/knowledge-bases/{kb_id}/documents/url` | 导入 URL |
| GET | `/api/v1/knowledge-bases/{kb_id}/documents/{id}` | 文档详情 |
| DELETE | `/api/v1/knowledge-bases/{kb_id}/documents/{id}` | 删除文档 |
| POST | `/api/v1/knowledge-bases/{kb_id}/documents/{id}/reprocess` | 重新处理 |
| GET | `/api/v1/knowledge-bases/{kb_id}/documents/{id}/chunks` | 查看分块 |

---

## 5. 处理流程

### 5.1 文档上传流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   上传文件   │────▶│   保存文件   │────▶│  创建记录   │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   完成入库   │◀────│  生成向量   │◀────│  文本分块   │
└─────────────┘     └─────────────┘     └─────────────┘
                                               ▲
                                               │
                                        ┌─────────────┐
                                        │  提取文本   │
                                        │ (MarkItDown)│
                                        └─────────────┘
```

### 5.2 文本提取

```python
# MarkItDown 统一处理
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert(file_path)  # 或 URL

text = result.text_content      # Markdown 格式文本
title = result.title            # 标题 (如有)
```

### 5.3 文本分块

```python
# 语义感知分块
chunker = TextChunker(
    chunk_size=500,      # tokens
    chunk_overlap=50,    # overlap tokens
)

chunks = chunker.chunk_text(text)
# [
#     {"content": "...", "chunk_index": 0, "token_count": 480},
#     {"content": "...", "chunk_index": 1, "token_count": 495},
#     ...
# ]
```

### 5.4 向量生成与存储

```python
from app.llm import model_manager

# 生成向量
embeddings = await model_manager.embed(
    texts=[chunk["content"] for chunk in chunks],
    model_id=kb.embedding_model_id,
)

# 存储到 pgvector
for chunk, embedding in zip(chunks, embeddings):
    await DocumentChunk.create(
        document_id=doc.id,
        content=chunk["content"],
        chunk_index=chunk["chunk_index"],
        token_count=chunk["token_count"],
        embedding=embedding,
    )
```

---

## 6. 搜索功能

### 6.1 语义搜索

```python
async def search(
    kb_id: UUID,
    query: str,
    top_k: int = 10,
    threshold: float = 0.7,
) -> list[SearchResult]:
    # 1. 生成查询向量
    query_embedding = await model_manager.embed([query])
    
    # 2. 向量检索 (pgvector)
    results = await DocumentChunk.filter(
        document__knowledge_base_id=kb_id
    ).annotate(
        similarity=CosineDistance("embedding", query_embedding[0])
    ).filter(
        similarity__gte=threshold
    ).order_by(
        "-similarity"
    ).limit(top_k)
    
    return results
```

### 6.2 混合搜索 (规划中)

- 向量搜索 + 关键词搜索
- BM25 + Cosine Similarity
- Reciprocal Rank Fusion (RRF)

---

## 7. 文件结构

```
backend/app/
├── models/
│   └── knowledge_base.py      # 数据模型
├── schemas/
│   └── knowledge_base.py      # Pydantic schemas
├── api/v1/endpoints/
│   └── knowledge_bases.py     # API 端点
├── services/
│   ├── document_processor.py  # 文档处理 + 分块
│   └── vector_store.py        # 向量存储服务
└── tasks/
    └── knowledge_base.py      # Celery 异步任务
```

---

## 8. 依赖配置

```toml
# pyproject.toml
[project]
dependencies = [
    # Document processing
    "markitdown[pdf,xlsx,xls]>=0.0.1a3",
]
```

---

## 9. 实现状态

| 功能 | 状态 |
|------|------|
| 数据模型 | ✅ 完成 |
| API 端点 | ✅ 完成 |
| 文档上传 | ✅ 完成 |
| URL 导入 | ✅ 完成 |
| 文本提取 (MarkItDown) | ✅ 完成 |
| 文本分块 | ✅ 完成 |
| Celery 异步任务 | ✅ 完成 |
| 向量生成 | ✅ 完成 |
| pgvector 存储 | 🔲 待实现 |
| 语义搜索 | 🔲 待实现 |
| 混合搜索 | 🔲 规划中 |
| 前端 UI | 🔲 待实现 |
