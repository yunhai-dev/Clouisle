# Clouisle: Next-Generation Enterprise-Grade Evolving Intelligent Knowledge Platform

[![CI Check](https://github.com/yunhai-dev/Clouisle/actions/workflows/ci.yml/badge.svg)](https://github.com/yunhai-dev/Clouisle/actions/workflows/ci.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org/)
[![Bun](https://img.shields.io/badge/Bun-1.0-orange)](https://bun.sh/)

[中文文档](docs/README_zh-CN.md)

## Introduction

Clouisle is an enterprise-grade knowledge base and AI Agent platform built on a distributed architecture. It is dedicated to transforming scattered, heterogeneous data into actionable knowledge and driving business decisions and automation through intelligent agents.

## Project Overview

In the era of information overload, enterprise knowledge is often scattered across documents, conversations, and systems, forming "data silos." Clouisle addresses this core pain point directly. It is not just a centralized knowledge base, but an intelligent platform capable of autonomous understanding, analysis, and execution. By integrating distributed systems, artificial intelligence, and workflow engines, Clouisle achieves a full-link closed loop from multi-source data collection and intelligent processing to knowledge application and automated response, allowing knowledge to truly flow and create value.

## Core Architecture & Features

### Distributed Loosely Coupled Architecture
The platform adopts a microservices design, where core components (such as collection, vectorization, and Agent engine) can be independently deployed and elastically scaled. This not only ensures high performance and high availability for processing massive data but also gives the platform excellent scalability, flexibly adapting to different needs from small teams to large organizations.

### "Data-Knowledge-Intelligence" Three-Layer Engine

1.  **Intelligent Collection & Governance Layer**: Seamlessly integrates with files, databases, APIs, web pages, and even daily communication tools (such as WeCom, DingTalk) to achieve automated data synchronization and structured extraction.
2.  **Knowledge Fusion & Computing Layer**: The core is a distributed vector database and knowledge graph engine. It transforms unstructured data into high-dimensional vectors through embedding models and builds relationships to achieve deep semantic understanding and precise cross-document retrieval.
3.  **Agent & Application Layer**: Based on the knowledge base, various specialized AI Agents are deployed (such as intelligent Q&A assistants, process automation Agents, analysis and decision Agents). They can understand natural language instructions, actively call knowledge or tools, and complete complex tasks.

## Core Functions & Workflow

-   **Full-Link Data Processing**: Supports collection from a wide range of data sources, parsing, cleaning, and vectorizing unstructured data, followed by semantic-based intelligent analysis and association mining, ultimately achieving millisecond-level retrieval through natural language.
-   **Multi-Modal Knowledge Management**: Unified management of multi-modal knowledge such as documents, tables, images, audio, and video, providing powerful version control, permission management, and collaborative editing capabilities.
-   **Out-of-the-Box Agents**: Provides general Agents for Q&A, summarization, creation, and insight analysis, and supports low-code customization of specialized Agents for specific business scenarios (such as customer service, R&D, risk control).
-   **Security & Compliance**: Provides private deployment, data encryption, and complete access audit logs to ensure the security and compliant use of core enterprise knowledge assets.

## Scenarios & Value

-   **Intelligent Q&A & Customer Service**: Provide 7x24 hour, precise knowledge-based instant Q&A for internal or external customers.
-   **R&D & Knowledge Collaboration**: Act as the team's "super brain," quickly indexing project documents, code repositories, and technical discussions to accelerate problem-solving.
-   **Business Process Automation**: Inject knowledge into business processes. For example, an Agent can automatically review new contracts based on a contract clause library or generate marketing content based on product documents.
-   **Data Analysis & Decision Support**: Quickly analyze market reports and internal data to generate competitive insights and decision recommendation briefs.

## Technical Features & Advantages

-   **True Full-Process Closed Loop**: Not a patchwork of tools, but an end-to-end solution from "data import" to "intelligent export."
-   **Intelligence-Driven, Not Just Retrieval**: Beyond keyword matching, Agents understand user intent, actively plan, call tools, and provide answers or execute actions.
-   **Enterprise-Grade Robustness**: Distributed architecture ensures service stability, data reliability, and scalability to cope with business growth.

---

## 🛠 Technical Architecture & Quick Start

### Project Structure

-   **backend/**: Python FastAPI application managed with `uv`.
-   **frontend/**: Next.js application.
-   **deploy/docker-compose.yml**: Infrastructure (PostgreSQL + Redis).

### Getting Started

#### Backend

1.  Navigate to `backend/`.
2.  Install dependencies: `uv sync` (or `pip install -r requirements.txt` if you export it).
3.  Run server: `uvicorn app.main:app --reload`.

#### Frontend

1.  Navigate to `frontend/`.
2.  Install dependencies: `bun install`.
3.  Run dev server: `bun dev`.

#### Infrastructure

Run `docker-compose -f deploy/docker-compose.yml up -d` to start PostgreSQL and Redis.
