# 云屿 (Clouisle)：下一代企业级分布式智能知识平台

[![CI Check](https://github.com/yunhai-dev/Clouisle/actions/workflows/ci.yml/badge.svg)](https://github.com/yunhai-dev/Clouisle/actions/workflows/ci.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org/)
[![Bun](https://img.shields.io/badge/Bun-1.0-orange)](https://bun.sh/)

[English Documentation](../README.md)

## 简介

云屿是一款基于分布式架构构建的企业级知识库与 AI Agent 智能平台，致力于将分散、异构的数据转化为可行动的知识，并通过智能体驱动业务决策与自动化。

## 项目概述

在信息过载的时代，企业知识往往散落在文档、对话与系统中，形成“数据孤岛”。云屿直面这一核心痛点，它不仅是一个集中化的知识库，更是一个具备自主理解、分析与执行能力的智能平台。通过融合分布式系统、人工智能与工作流引擎，云屿实现了从多源数据采集、智能处理到知识应用与自动化响应的全链路闭环，让知识真正流动并创造价值。

## 核心架构与特点

### 分布式松耦合架构
平台采用微服务化设计，各核心组件（如采集、向量化、Agent 引擎）可独立部署与弹性伸缩。这不仅保障了系统处理海量数据的高性能与高可用性，也赋予了平台卓越的可扩展性，能灵活适配从小型团队到大型组织的不同需求。

### “数据-知识-智能”三层引擎

1.  **智能采集与治理层**：无缝接入文件、数据库、API、网页乃至日常沟通工具（如企微、钉钉），实现自动化的数据同步与结构化提取。
2.  **知识融合与计算层**：核心是分布式向量数据库与知识图谱引擎。它通过嵌入模型将非结构化数据转化为高维向量，并构建关联关系，实现深度的语义理解与跨文档的精准检索。
3.  **智能体与应用层**：基于知识库，部署多种专用 AI Agent（如智能问答助手、流程自动化 Agent、分析决策 Agent）。它们能理解自然语言指令，主动调用知识或工具，完成复杂的任务。

## 核心功能与工作流程

-   **全链路数据处理**：支持从广泛数据源的采集，到非结构化数据的解析、清洗与向量化入库，再到基于语义的智能分析与关联挖掘，最终通过自然语言实现毫秒级检索。
-   **多模态知识管理**：统一管理文档、表格、图片、音视频等多模态知识，提供强大的版本控制、权限管理与协作编辑能力。
-   **开箱即用的智能体**：提供问答、总结、创作、洞察分析等通用 Agent，并支持低代码方式定制面向特定业务场景（如客服、研发、风控）的专用智能体。
-   **安全与合规**：提供私有化部署、数据加密、完整的访问审计日志，确保企业核心知识资产的安全与合规使用。

## 应用场景与价值

-   **智能问答与客服**：为企业内部或外部客户提供 7x24 小时、基于精准知识的即时问答。
-   **研发与知识协同**：充当团队的“超级大脑”，快速索引项目文档、代码库与技术讨论，加速问题解决。
-   **业务流程自动化**：将知识注入业务流程，例如，Agent 可自动根据合同条款库审核新合同，或根据产品文档生成营销内容。
-   **数据分析与决策支持**：快速分析市场报告、内部数据，生成竞争洞察与决策建议简报。

## 技术特色与优势

-   **真正全流程闭环**：非工具拼凑，提供从“数据进口”到“智能出口”的端到端解决方案。
-   **智能驱动，而非简单检索**：超越关键词匹配，通过 Agent 理解用户意图，主动规划、调用工具并给出答案或执行动作。
-   **企业级健壮性**：分布式架构保障了服务的稳定性、数据的可靠性，以及应对业务增长的可扩展性。

---

## 🛠 技术架构与快速开始

### 项目结构

-   **backend/**: Python FastAPI 应用，使用 `uv` 管理。
-   **frontend/**: Next.js 应用。
-   **deploy/docker-compose.yml**: 基础设施 (PostgreSQL + Redis)。

### 快速开始

#### 后端 (Backend)

1.  进入 `backend/` 目录。
2.  安装依赖：`uv sync` (或 `pip install -r requirements.txt` 如果已导出)。
3.  运行服务器：`uvicorn app.main:app --reload`。

#### 前端 (Frontend)

1.  进入 `frontend/` 目录。
2.  安装依赖：`bun install`。
3.  运行开发服务器：`bun dev`。

#### 基础设施 (Infrastructure)

运行 `docker-compose -f deploy/docker-compose.yml up -d` 启动 PostgreSQL 和 Redis。
