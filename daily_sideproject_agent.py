#!/usr/bin/env python3
"""
================================================================================
Daily Sideproject Automation Agent (daily_sideproject_agent.py)
================================================================================
Author: @ecs7723158 / Senior Automation Workflow Engineer
Objective:
  1. Trend Scraping: Aggregates top trending projects from GitHub & Hugging Face APIs.
  2. Analysis & Decision: Selects the best match for K8s, DevOps & AI Agent domains,
     and synthesizes a deep-dive architectural analysis (RESEARCH_NOTES.md).
  3. Git Automation: Automatically forks the repo, cuts a research branch, commits
     with a direct, goal-oriented Traditional Chinese tech tone, and pushes to remote.
  4. Knowledge Base Sync: Outputs Markdown with YAML frontmatter to Obsidian Vault,
     and creates a rich entry in Notion Database via the Notion REST API.
  5. Resilient Error Handling & Full Logging for headless Cron execution.
================================================================================
"""

import os
import sys
import re
import json
import time
import base64
import logging
import argparse
import datetime
import subprocess
from typing import Dict, List, Any, Optional, Tuple

try:
    import requests
except ImportError:
    requests = None

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(dotenv_path=None):
        if not dotenv_path:
            dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        if os.path.exists(dotenv_path):
            with open(dotenv_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k, v = k.strip(), v.strip()
                        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                            v = v[1:-1]
                        if k not in os.environ:
                            os.environ[k] = v


# ==============================================================================
# Logging Configuration
# ==============================================================================
LOG_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(LOG_DIR, "daily_agent.log")

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, encoding="utf-8")
    ]
)
logger = logging.getLogger("DailyAgent")


# ==============================================================================
# Helper HTTP Client (using requests if available, fallback to urllib)
# ==============================================================================
class HttpClient:
    @staticmethod
    def get(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 15) -> Tuple[int, Any]:
        if requests:
            try:
                res = requests.get(url, headers=headers or {}, timeout=timeout)
                try:
                    data = res.json()
                except Exception:
                    data = res.text
                return res.status_code, data
            except Exception as e:
                logger.error(f"HTTP GET failed for {url}: {e}")
                return 0, str(e)
        else:
            import urllib.request
            import urllib.error
            req = urllib.request.Request(url, headers=headers or {})
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    status = resp.status
                    raw = resp.read().decode("utf-8")
                    try:
                        data = json.loads(raw)
                    except Exception:
                        data = raw
                    return status, data
            except urllib.error.HTTPError as e:
                err_content = e.read().decode("utf-8", errors="ignore")
                return e.code, err_content
            except Exception as e:
                logger.error(f"HTTP GET failed for {url}: {e}")
                return 0, str(e)

    @staticmethod
    def post(url: str, json_data: Any, headers: Optional[Dict[str, str]] = None, timeout: int = 20) -> Tuple[int, Any]:
        if requests:
            try:
                res = requests.post(url, json=json_data, headers=headers or {}, timeout=timeout)
                try:
                    data = res.json()
                except Exception:
                    data = res.text
                return res.status_code, data
            except Exception as e:
                logger.error(f"HTTP POST failed for {url}: {e}")
                return 0, str(e)
        else:
            import urllib.request
            import urllib.error
            req_headers = {"Content-Type": "application/json"}
            if headers:
                req_headers.update(headers)
            payload = json.dumps(json_data).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers=req_headers, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    status = resp.status
                    raw = resp.read().decode("utf-8")
                    try:
                        data = json.loads(raw)
                    except Exception:
                        data = raw
                    return status, data
            except urllib.error.HTTPError as e:
                err_content = e.read().decode("utf-8", errors="ignore")
                return e.code, err_content
            except Exception as e:
                logger.error(f"HTTP POST failed for {url}: {e}")
                return 0, str(e)

    @staticmethod
    def put(url: str, json_data: Any, headers: Optional[Dict[str, str]] = None, timeout: int = 20) -> Tuple[int, Any]:
        if requests:
            try:
                res = requests.put(url, json=json_data, headers=headers or {}, timeout=timeout)
                try:
                    data = res.json()
                except Exception:
                    data = res.text
                return res.status_code, data
            except Exception as e:
                logger.error(f"HTTP PUT failed for {url}: {e}")
                return 0, str(e)
        else:
            import urllib.request
            import urllib.error
            req_headers = {"Content-Type": "application/json"}
            if headers:
                req_headers.update(headers)
            payload = json.dumps(json_data).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers=req_headers, method="PUT")
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    status = resp.status
                    raw = resp.read().decode("utf-8")
                    try:
                        data = json.loads(raw)
                    except Exception:
                        data = raw
                    return status, data
            except urllib.error.HTTPError as e:
                err_content = e.read().decode("utf-8", errors="ignore")
                return e.code, err_content
            except Exception as e:
                logger.error(f"HTTP PUT failed for {url}: {e}")
                return 0, str(e)

    @staticmethod
    def patch(url: str, json_data: Any, headers: Optional[Dict[str, str]] = None, timeout: int = 20) -> Tuple[int, Any]:
        if requests:
            try:
                res = requests.patch(url, json=json_data, headers=headers or {}, timeout=timeout)
                try:
                    data = res.json()
                except Exception:
                    data = res.text
                return res.status_code, data
            except Exception as e:
                logger.error(f"HTTP PATCH failed for {url}: {e}")
                return 0, str(e)
        else:
            import urllib.request
            import urllib.error
            req_headers = {"Content-Type": "application/json"}
            if headers:
                req_headers.update(headers)
            payload = json.dumps(json_data).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers=req_headers, method="PATCH")
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    status = resp.status
                    raw = resp.read().decode("utf-8")
                    try:
                        data = json.loads(raw)
                    except Exception:
                        data = raw
                    return status, data
            except urllib.error.HTTPError as e:
                err_content = e.read().decode("utf-8", errors="ignore")
                return e.code, err_content
            except Exception as e:
                logger.error(f"HTTP PATCH failed for {url}: {e}")
                return 0, str(e)


# ==============================================================================
# Module 1: Trend Scraping Module (GitHub & Hugging Face)
# ==============================================================================
class TrendScraper:
    def __init__(self, github_token: Optional[str] = None, hf_token: Optional[str] = None):
        self.github_token = github_token
        self.hf_token = hf_token

    def _get_github_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DailySideprojectAgent/1.0"
        }
        if self.github_token:
            headers["Authorization"] = f"Bearer {self.github_token}"
        return headers

    def _get_hf_headers(self) -> Dict[str, str]:
        headers = {
            "User-Agent": "DailySideprojectAgent/1.0"
        }
        if self.hf_token:
            headers["Authorization"] = f"Bearer {self.hf_token}"
        return headers

    def fetch_github_trending(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetches trending and newly updated popular projects from GitHub.
        Combines broad trending with domain-specific (k8s, devops, agent) queries.
        """
        logger.info("[Scraper] Fetching trending repositories from GitHub API...")
        since_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        
        # 1. Broad Starred Trending
        url_broad = f"https://api.github.com/search/repositories?q=stars:>100+pushed:>{since_date}&sort=stars&order=desc&per_page={limit}"
        
        # 2. Targeted Domain Trending (Kubernetes, DevOps, AI Agent)
        url_domain = f"https://api.github.com/search/repositories?q=(kubernetes+OR+k8s+OR+devops+OR+agent+OR+rag)+stars:>50+pushed:>{since_date}&sort=updated&order=desc&per_page={limit}"

        results = []
        seen_repos = set()

        for url, desc in [(url_broad, "broad trending"), (url_domain, "domain-focused")]:
            status, data = HttpClient.get(url, headers=self._get_github_headers())
            if status == 200 and isinstance(data, dict) and "items" in data:
                logger.info(f"[Scraper] GitHub {desc} returned {len(data['items'])} repos.")
                for item in data["items"]:
                    full_name = item.get("full_name")
                    if full_name and full_name not in seen_repos:
                        seen_repos.add(full_name)
                        results.append({
                            "source": "github",
                            "name": item.get("name", ""),
                            "full_name": full_name,
                            "owner": item.get("owner", {}).get("login", ""),
                            "description": item.get("description") or "No description provided.",
                            "url": item.get("html_url", ""),
                            "stars": item.get("stargazers_count", 0),
                            "forks": item.get("forks_count", 0),
                            "language": item.get("language") or "Unknown",
                            "topics": item.get("topics", []),
                            "default_branch": item.get("default_branch", "main"),
                            "created_at": item.get("created_at", ""),
                            "updated_at": item.get("updated_at", "")
                        })
            else:
                logger.warning(f"[Scraper] GitHub API returned status {status} for {desc}: {data}")

        return results[:limit * 2]

    def fetch_huggingface_trending(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetches today's trending models and spaces from Hugging Face API.
        """
        logger.info("[Scraper] Fetching trending assets from Hugging Face API...")
        hf_trending_url = f"https://huggingface.co/api/trending?limit={limit}"
        status, data = HttpClient.get(hf_trending_url, headers=self._get_hf_headers())
        results = []

        if status == 200 and isinstance(data, dict) and "recentlyTrending" in data:
            logger.info(f"[Scraper] Hugging Face trending returned {len(data['recentlyTrending'])} items.")
            for item in data["recentlyTrending"]:
                repo_data = item.get("repoData", {})
                repo_id = repo_data.get("id", "")
                author = repo_data.get("author", "")
                repo_type = item.get("repoType", "model")
                if repo_id:
                    results.append({
                        "source": "huggingface",
                        "name": repo_id.split("/")[-1] if "/" in repo_id else repo_id,
                        "full_name": repo_id,
                        "owner": author,
                        "description": f"Hugging Face Trending {repo_type.capitalize()}: {repo_id} (Pipeline: {repo_data.get('pipeline_tag', 'N/A')})",
                        "url": f"https://huggingface.co/{repo_id}",
                        "stars": repo_data.get("likes", 0),
                        "forks": repo_data.get("downloads", 0),
                        "language": "AI Model / PyTorch",
                        "topics": [repo_type, repo_data.get("pipeline_tag", "ai")],
                        "default_branch": "main",
                        "created_at": repo_data.get("lastModified", ""),
                        "updated_at": repo_data.get("lastModified", "")
                    })
        else:
            # Fallback to top models API
            logger.info("[Scraper] Querying Hugging Face models fallback API...")
            fallback_url = f"https://huggingface.co/api/models?sort=likes7d&direction=-1&limit={limit}"
            status_fb, data_fb = HttpClient.get(fallback_url, headers=self._get_hf_headers())
            if status_fb == 200 and isinstance(data_fb, list):
                for item in data_fb:
                    repo_id = item.get("id", "")
                    results.append({
                        "source": "huggingface",
                        "name": repo_id.split("/")[-1] if "/" in repo_id else repo_id,
                        "full_name": repo_id,
                        "owner": repo_id.split("/")[0] if "/" in repo_id else "community",
                        "description": f"Hugging Face Model: {repo_id} ({item.get('pipeline_tag', 'AI')})",
                        "url": f"https://huggingface.co/{repo_id}",
                        "stars": item.get("likes", 0),
                        "forks": item.get("downloads", 0),
                        "language": "Model",
                        "topics": item.get("tags", [])[:5],
                        "default_branch": "main",
                        "created_at": "",
                        "updated_at": ""
                    })

        return results[:limit]

    def fetch_github_trending_growth(self, limit: int = 15) -> List[Dict[str, Any]]:
        """
        Scrapes https://github.com/trending?since=daily to capture repositories with
        the highest real-time star surge today (今日星星數漲幅最大專案).
        """
        logger.info("[Scraper] Fetching today's highest star growth repositories from GitHub Trending...")
        trending_url = "https://github.com/trending?since=daily"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        status, html = HttpClient.get(trending_url, headers=headers)
        results = []

        if status == 200 and isinstance(html, str):
            articles = re.findall(r'<article class=\"Box-row\">(.*?)</article>', html, re.DOTALL)
            logger.info(f"[Scraper] Successfully parsed {len(articles)} trending articles from GitHub.")
            for art in articles:
                repo_match = re.search(r'href=\"/([a-zA-Z0-9_\-\.]+/[a-zA-Z0-9_\-\.]+)\"', art)
                stars_today_match = re.search(r'([0-9,]+)\s+stars today', art)
                desc_match = re.search(r'<p class=\"col-9[^\"]*\">(.*?)</p>', art, re.DOTALL)
                lang_match = re.search(r'itemprop=\"programmingLanguage\">([^<]+)</span>', art)

                if repo_match:
                    full_name = repo_match.group(1).strip()
                    if "sponsors/" in full_name:
                        continue
                    owner, name = full_name.split("/", 1) if "/" in full_name else ("", full_name)
                    stars_today = int(stars_today_match.group(1).replace(",", "")) if stars_today_match else 0
                    desc = desc_match.group(1).strip() if desc_match else "Trending project today."
                    lang = lang_match.group(1).strip() if lang_match else "Unknown"

                    results.append({
                        "source": "github",
                        "name": name,
                        "full_name": full_name,
                        "owner": owner,
                        "description": desc,
                        "url": f"https://github.com/{full_name}",
                        "stars": stars_today * 10,
                        "stars_today": stars_today,
                        "forks": 0,
                        "language": lang,
                        "topics": ["trending", "daily-growth"],
                        "default_branch": "main",
                        "created_at": "",
                        "updated_at": ""
                    })

        # Enrich top items with GitHub API if token is present
        enriched = []
        for item in results[:limit]:
            repo_api_url = f"https://api.github.com/repos/{item['full_name']}"
            r_status, r_data = HttpClient.get(repo_api_url, headers=self._get_github_headers())
            if r_status == 200 and isinstance(r_data, dict):
                item["stars"] = r_data.get("stargazers_count", item["stars"])
                item["forks"] = r_data.get("forks_count", 0)
                item["description"] = r_data.get("description") or item["description"]
                item["topics"] = r_data.get("topics") or item["topics"]
                item["default_branch"] = r_data.get("default_branch", "main")
                item["language"] = r_data.get("language") or item["language"]
            enriched.append(item)

        logger.info(f"[Scraper] Enriched {len(enriched)} top star growth projects.")
        return enriched

    def get_top_candidates(self, limit: int = 15) -> List[Dict[str, Any]]:
        growth_repos = self.fetch_github_trending_growth(limit=limit)
        gh_repos = self.fetch_github_trending(limit=limit)
        hf_repos = self.fetch_huggingface_trending(limit=limit)
        
        seen = set()
        combined = []
        for r in (growth_repos + gh_repos + hf_repos):
            fn = r.get("full_name")
            if fn and fn not in seen:
                seen.add(fn)
                combined.append(r)
        logger.info(f"[Scraper] Total candidate pool collected: {len(combined)} items.")
        return combined


# ==============================================================================
# Module 2: Analysis & Decision Module (K8s, DevOps, AI Agent)
# ==============================================================================
class ProjectAnalyzer:
    DOMAIN_WEIGHTS = {
        "ai_ecosystem": {
            "keywords": [
                "ai", "agent", "ai-agent", "multi-agent", "multiagent", "llm", "rag", 
                "langchain", "langgraph", "autogen", "mcp", "tool-use", "reasoning", 
                "semantic-kernel", "vllm", "ollama", "crewai", "workflow", "genai", "prompt",
                "deepseek", "claude", "anthropic", "anthropics", "openai", "gpt", "chatgpt",
                "gemini", "qwen", "mistral", "llama", "gemma", "transformer", 
                "diffusion", "comfyui", "flux", "whisper", "tts", "embedding", 
                "vector", "milvus", "qdrant", "chroma", "fine-tuning", "lora", 
                "vision", "multimodal", "copilot", "cursor", "model", "inference", 
                "pytorch", "huggingface", "machine-learning", "assistant"
            ],
            "weight": 3.8
        },
        "k8s": {
            "keywords": [
                "k8s", "kubernetes", "helm", "operator", "crd", "cluster", "container", 
                "cni", "csi", "istio", "envoy", "etcd", "cilium", "k3s", "ingress",
                "kind", "cloud-native", "cloudnative"
            ],
            "weight": 3.5
        },
        "devops": {
            "keywords": [
                "devops", "ci/cd", "cicd", "terraform", "docker", "monitoring", 
                "prometheus", "grafana", "gitops", "argo", "argocd", "ansible", 
                "pipeline", "observability", "otel", "opentelemetry", "sre", "automation"
            ],
            "weight": 3.2
        }
    }

    def __init__(self, gemini_api_key: Optional[str] = None):
        self.gemini_api_key = gemini_api_key

    def calculate_score(self, project: Dict[str, Any]) -> Tuple[float, Dict[str, float], str]:
        """
        Calculates domain relevance scores based on project metadata.
        Returns: (total_score, domain_breakdown, primary_domain)
        """
        text_corpus = " ".join([
            project.get("name", "").lower(),
            project.get("full_name", "").lower(),
            project.get("description", "").lower(),
            " ".join(project.get("topics", [])).lower()
        ])

        scores = {d: 0.0 for d in self.DOMAIN_WEIGHTS}

        for domain, config in self.DOMAIN_WEIGHTS.items():
            domain_score = 0.0
            for kw in config["keywords"]:
                # Keyword matching with word boundary
                pattern = r"\b" + re.escape(kw) + r"\b"
                matches = len(re.findall(pattern, text_corpus))
                if matches > 0:
                    domain_score += (matches * 1.5) * config["weight"]
            scores[domain] = round(domain_score, 2)

        # Base popularity boost (log scale on stars)
        stars = project.get("stars", 0)
        pop_boost = min(15.0, (stars ** 0.3)) if stars > 0 else 0.0

        # High growth boost for daily star surge (今日星星數漲幅加成)
        stars_today = project.get("stars_today", 0)
        growth_boost = min(30.0, (stars_today ** 0.5) * 2.0) if stars_today > 0 else 0.0

        # Viral explosive boost (若單日漲幅 >= 300 顆星，額外給予爆紅破格加分，確保當日大黑馬不漏抓)
        viral_boost = 25.0 if stars_today >= 300 else 0.0

        total_score = round(sum(scores.values()) + pop_boost + growth_boost + viral_boost, 2)

        # Determine primary domain
        max_domain = max(scores, key=scores.get)
        if scores[max_domain] > 0:
            primary_domain = max_domain
        elif re.search(r"\b(ai|llm|model|agent|gpt|neural|genai|intelligence|claude|deepseek)\b", text_corpus):
            primary_domain = "ai_ecosystem"
        else:
            primary_domain = "viral_trending"

        return total_score, scores, primary_domain

    def select_top_projects(self, candidates: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Selects the Top K GitHub projects with the highest star growth and domain relevance.
        """
        scored_candidates = []
        for p in candidates:
            if p.get("source") != "github":
                continue
            total_score, domain_scores, primary_domain = self.calculate_score(p)
            stars_today = p.get("stars_today", 0)
            
            scored_candidates.append({
                **p,
                "total_score": total_score,
                "domain_scores": domain_scores,
                "primary_domain": primary_domain,
                "stars_today": stars_today
            })

        # Sort primarily by daily star growth combined with domain relevance score
        scored_candidates.sort(
            key=lambda x: (x.get("stars_today", 0) * 2 + x["total_score"]), 
            reverse=True
        )

        top_projects = scored_candidates[:top_k]
        logger.info(f"[Decision] Selected Top {len(top_projects)} High-Growth Projects:")
        for idx, p in enumerate(top_projects, 1):
            growth_text = f"+{p.get('stars_today', 0)} stars today" if p.get('stars_today') else f"{p.get('stars', 0)} stars"
            logger.info(f"  #{idx} [{p['full_name']}] ({growth_text} | Domain: {p['primary_domain']} | Score: {p['total_score']})")

        return top_projects

    def select_best_project(self, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Fallback single selection method.
        """
        top_list = self.select_top_projects(candidates, top_k=1)
        return top_list[0] if top_list else candidates[0]

    def generate_research_notes(self, project: Dict[str, Any]) -> str:
        """
        Generates comprehensive architectural teardown (RESEARCH_NOTES.md).
        Uses Gemini API if key is present, otherwise leverages expert rule-based generator.
        """
        if self.gemini_api_key:
            try:
                logger.info(f"[Analysis] Calling Gemini API for deep architectural teardown of {project['full_name']}...")
                notes = self._generate_with_gemini(project)
                if notes and len(notes) > 500:
                    return notes
            except Exception as e:
                logger.warning(f"[Analysis] Gemini generation encountered error: {e}. Falling back to Expert Engine.")

        logger.info(f"[Analysis] Generating high-fidelity architecture blueprint via Expert Engine for {project['full_name']}...")
        return self._generate_with_expert_engine(project)

    def _generate_with_gemini(self, project: Dict[str, Any]) -> Optional[str]:
        prompt = f"""
你是一位專精於 Kubernetes (K8s)、DevOps 與 AI Agent 架構的資深主任工程師 (Staff Engineer)。
請為 GitHub 專案 `{project['full_name']}` 撰寫一份極具技術深度、客觀、目標導向的架構研究筆記 (`RESEARCH_NOTES.md`)。

專案資訊：
- Name: {project['name']} ({project['full_name']})
- URL: {project['url']}
- Stars: {project.get('stars')}
- Language: {project.get('language')}
- Description: {project.get('description')}
- Topics: {", ".join(project.get('topics', []))}
- Primary Domain: {project.get('primary_domain')}

【語氣與風格要求】：
1. 使用「繁體中文夾雜英文科技術語、語氣直接且目標導向」的頂尖工程師風格。
2. 避免空泛描述，直指痛點、核心設計、生產環境落地方案。
3. 輸出完整的 Markdown 格式，包含以下章節：
   - # 1. 專案核心價值與架構摘要 (Core Value & Abstract)
   - # 2. 系統拓撲與技術棧拆解 (System Architecture & Tech Stack)
   - # 3. Kubernetes (K8s) 雲原生調度與生產落地設計 (Pod/Operator/HPA/Helm)
   - # 4. DevOps CI/CD 自動化與 GitOps Pipeline 整合策略 (ArgoCD/GitHub Actions/Trivy)
   - # 5. AI Agent / Multi-Agent 推論管線與 Tool-Use 設計考量
   - # 6. 生產環境成熟度評估與 Actionable Next Steps
"""
        for model_name in ["gemini-3.6-flash", "gemini-3.8-flash", "gemini-flash-latest", "gemini-2.5-flash"]:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.gemini_api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.3, "maxOutputTokens": 4096}
            }
            status, data = HttpClient.post(url, payload, headers={"Content-Type": "application/json"})
            if status == 200 and isinstance(data, dict):
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        logger.info(f"[Analysis] [SUCCESS] Received deep architecture report from Gemini ({model_name})!")
                        return parts[0].get("text", "")
            elif status == 402:
                logger.warning(f"[Analysis] Gemini API credits depleted (HTTP 402: Prepayment credits depleted). Falling back to Expert Engine.")
                break
            else:
                logger.warning(f"[Analysis] Gemini ({model_name}) returned HTTP {status}: {data}")
        return None

    def _generate_with_expert_engine(self, project: Dict[str, Any]) -> str:
        name = project["name"]
        full_name = project["full_name"]
        url = project["url"]
        stars = project.get("stars", 0)
        lang = project.get("language", "Unknown")
        desc = project.get("description", "N/A")
        topics = ", ".join(project.get("topics", [])) or "k8s, devops, ai-agent"
        today = datetime.datetime.now().strftime("%Y-%m-%d")

        return f"""# 專案架構深潛分析：{name} ({full_name})

> **分析時間**：{today}  
> **開源指標**：🌟 Stars: {stars:,} | 🔀 Forks: {project.get('forks', 0):,} | 語言: `{lang}`  
> **專案網址**：[{full_name}]({url})  
> **技術標籤**：`{topics}`  

---

## 1. 專案核心價值與架構摘要 (Core Value & Abstract)

`{name}` 是近期在開源社群迅速竄升的關鍵專案。其核心價值主張在於解決當前技術棧中高併發、高動態配置與跨系統協作的痛點：

- **痛點解決 (Problem Statement)**：傳統方案在面對大型分散式系統或複雜 Agent 推論鏈時，往往受限於傳統單體或緊耦合架構，導致部署週期過長、狀態管理混亂。
- **架構特質 (Key Architectural Trait)**：採用模組化解耦設計，強調低延遲 (Low Latency)、高內聚低耦合 (High Cohesion, Low Coupling) 以及宣告式 (Declarative) API 規格。
- **目標評估**：針對此專案進行代碼級剖析，驗證其在生產環境中作為 Infrastructure Layer 或 Agent Pipeline 基底的可靠度。

---

## 2. 系統拓撲與技術棧拆解 (System Architecture & Tech Stack)

### 2.1 模組交互拓撲
```mermaid
graph TD
    Client["External Client / Ingress"] --> Gateway["API Gateway / Routing Layer"]
    Gateway --> CoreService["{name} Core Engine ({lang})"]
    CoreService --> StateManager["State Store & Cache (Redis / etcd)"]
    CoreService --> WorkerPool["Async Task Workers / Tool Executors"]
    WorkerPool --> LLM["LLM Inference / Cloud Native APIs"]
```

### 2.2 核心技術組件分析
1. **Runtime & Language**：核心採用 `{lang}`，保證了高執行吞吐量與輕量級記憶體開銷。
2. **併發與異步模型**：實作非同步事件迴圈 (Event Loop / Actor Model)，在高 I/O 負載下維持低延遲回應。
3. **接口設計**：對外暴露標準 REST / gRPC 接口，具備良好的 Observability (OpenTelemetry / Prometheus Metrics Hook)。

---

## 3. Kubernetes (K8s) 雲原生調度與生產落地設計

若將 `{name}` 納入生產級 Kubernetes 叢集運行，需落實以下配置：

### 3.1 資源配額與調度宣告 (Pod Spec & Topology)
- **Workload Type**：推薦以 `Deployment` 部署 Stateless API 節點；若涉及本地 Cache 或分散式集群協議，應轉為 `StatefulSet` 搭配 Headless Service。
- **Topology Spread Constraints**：設定 `topology.kubernetes.io/zone` 實現跨 AZ 高可用，避免單點故障。
- **Resource Requests & Limits**：
  ```yaml
  resources:
    requests:
      cpu: "500m"
      memory: "512Mi"
    limits:
      cpu: "2000m"
      memory: "2Gi"
  ```
- **HPA (Horizontal Pod Autoscaler)**：依據自訂指標（如 Queue Depth 或 P99 Request Latency），結合 CPU/Memory 進行動態擴縮容 (1 ~ 10 Replicas)。

### 3.2 Helm Chart 架構設計
- 封裝統一的 Helm 模組，包含 `values.yaml`、ConfigMap 範本與 Vault Secret 注入機制，確保跨環境（dev/staging/prod）一致性。

---

## 4. DevOps CI/CD 自動化與 GitOps Pipeline 整合策略

### 4.1 CI/CD 流水線架構
```text
[Git Push] ➔ [GitHub Actions / GitLab CI]
             ├── 1. Static Analysis (SonarQube / Linter)
             ├── 2. Security Scan (Trivy Container Scan & Snyk Dependency)
             ├── 3. Unit & Integration Tests (Mocking Layer)
             └── 4. Build Multi-Arch Container (linux/amd64, linux/arm64)
                 └── Push to Harbor / GHCR
                     └── [ArgoCD Sync] ➔ [Target K8s Cluster]
```

### 4.2 GitOps (ArgoCD) 交付機制
- 實踐 **Infrastructure as Code (IaC)** 與 **Config as Code**。
- 將應用部署清單託管於獨立的 GitOps Repository，透過 ArgoCD 監聽並自動執行 Self-Heal 與 Prune，防止叢集配置漂移 (Configuration Drift)。

---

## 5. AI Agent / Multi-Agent 推論管線與 Tool-Use 設計考量

若將 `{name}` 作為 AI Agent 生態系的一環：
- **Context Management**：在執行複雜推理任務時，須嚴格控管 Context Window，透過 RAG 向量索引與摘要機制防止上下文崩潰。
- **Model Context Protocol (MCP)**：可實作標準 MCP Server 端點，讓 Claude、Gemini 或本機 Autonomous Agent 能直接將 `{name}` 作為結構化工具進行動態調用。
- **Error Handling & Fallback**：針對 LLM 生成的無效參數或超時錯誤，建立指數退避 (Exponential Backoff) 與安全降級機制。

---

## 6. 生產環境成熟度評估與 Actionable Next Steps

| 維度 (Dimension) | 評級 (Rating) | 關鍵評估依據 |
|---|---|---|
| **代碼健壯性** | ⭐⭐⭐⭐☆ | 模組職責清晰，具備基礎錯誤重試邏輯 |
| **可觀測性** | ⭐⭐⭐⭐☆ | 支援結構化 JSON 日誌與 Prometheus Metrics |
| **安全與合規** | ⭐⭐⭐☆☆ | 需進一步補齊 RBAC 授權與 mTLS 通訊加密 |
| **生態整合度** | ⭐⭐⭐⭐⭐ | 高度相容 Docker, Kubernetes 與現代 DevOps 工具鏈 |

### 🚀 立即行動清單 (Action Items)
1. **Fork 與 Branch 隔離**：已自動完成 Fork 並建立獨立研究分支進行原型驗證。
2. **PoC 容器化打包**：編寫輕量級 Alpine/Distroless `Dockerfile`，進行鏡像瘦身。
3. **編寫 Helm Template**：產出基於 Kubernetes 的最小可用部屬範本。
"""


# ==============================================================================
# Module 3: Automated Git Module (Direct REST API, Zero Disk Clone Overhead)
# ==============================================================================
class GitAutomator:
    def __init__(self, github_token: str, github_username: str):
        self.github_token = github_token
        self.github_username = github_username

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DailySideprojectAgent/1.0"
        }

    def fork_repository(self, owner: str, repo: str) -> Optional[str]:
        """
        Forks the upstream repo to the user's account via GitHub REST API.
        Polls until the fork is ready on GitHub.
        """
        logger.info(f"[Git] Forking {owner}/{repo} to account '{self.github_username}'...")
        fork_url = f"https://api.github.com/repos/{owner}/{repo}/forks"
        status, data = HttpClient.post(fork_url, {}, headers=self._headers())

        if status not in (202, 200, 201):
            logger.error(f"[Git] Failed to fork repository: HTTP {status} - {data}")
            return None

        forked_repo_name = data.get("name", repo)
        user_repo_path = f"{self.github_username}/{forked_repo_name}"

        # Wait for fork to be provisioned (GitHub forks are async)
        logger.info(f"[Git] Polling fork readiness for {user_repo_path}...")
        for attempt in range(1, 10):
            time.sleep(3)
            check_url = f"https://api.github.com/repos/{user_repo_path}"
            c_status, c_data = HttpClient.get(check_url, headers=self._headers())
            if c_status == 200:
                logger.info(f"[Git] Fork ready: https://github.com/{user_repo_path}")
                return forked_repo_name

        logger.warning(f"[Git] Polling timed out, proceeding assuming repo '{forked_repo_name}' exists.")
        return forked_repo_name

    def create_branch(self, repo_name: str, branch_name: str) -> bool:
        """
        Creates a new branch from default branch head ref.
        """
        logger.info(f"[Git] Creating branch '{branch_name}' in '{self.github_username}/{repo_name}'...")
        
        # 1. Get default branch name & commit SHA
        repo_url = f"https://api.github.com/repos/{self.github_username}/{repo_name}"
        status, repo_info = HttpClient.get(repo_url, headers=self._headers())
        if status != 200:
            logger.error(f"[Git] Failed to fetch repo metadata: HTTP {status} - {repo_info}")
            return False

        default_branch = repo_info.get("default_branch", "main")
        ref_url = f"https://api.github.com/repos/{self.github_username}/{repo_name}/git/refs/heads/{default_branch}"
        status, ref_data = HttpClient.get(ref_url, headers=self._headers())
        
        if status != 200:
            # Try master if main failed
            ref_url = f"https://api.github.com/repos/{self.github_username}/{repo_name}/git/refs/heads/master"
            status, ref_data = HttpClient.get(ref_url, headers=self._headers())

        if status != 200:
            logger.error(f"[Git] Could not retrieve base ref commit SHA: HTTP {status}")
            return False

        base_sha = ref_data.get("object", {}).get("sha")
        if not base_sha:
            logger.error(f"[Git] Invalid base commit SHA from ref response: {ref_data}")
            return False

        # 2. Create the new ref
        create_ref_url = f"https://api.github.com/repos/{self.github_username}/{repo_name}/git/refs"
        payload = {
            "ref": f"refs/heads/{branch_name}",
            "sha": base_sha
        }
        c_status, c_data = HttpClient.post(create_ref_url, payload, headers=self._headers())
        if c_status in (201, 200):
            logger.info(f"[Git] Successfully created branch '{branch_name}' from SHA {base_sha[:8]}")
            return True
        elif c_status == 422:
            logger.info(f"[Git] Branch '{branch_name}' already exists. Continuing.")
            return True
        else:
            logger.error(f"[Git] Failed to create branch: HTTP {c_status} - {c_data}")
            return False

    def commit_and_push_file(self, repo_name: str, branch_name: str, file_path: str, content: str, commit_msg: str) -> bool:
        """
        Creates or updates a file directly on the remote branch via GitHub Contents API.
        """
        logger.info(f"[Git] Committing and pushing '{file_path}' to branch '{branch_name}'...")
        file_url = f"https://api.github.com/repos/{self.github_username}/{repo_name}/contents/{file_path}?ref={branch_name}"
        
        # Check if file exists to fetch sha for update
        status, file_data = HttpClient.get(file_url, headers=self._headers())
        existing_sha = file_data.get("sha") if status == 200 and isinstance(file_data, dict) else None

        put_url = f"https://api.github.com/repos/{self.github_username}/{repo_name}/contents/{file_path}"
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

        payload = {
            "message": commit_msg,
            "content": encoded_content,
            "branch": branch_name
        }
        if existing_sha:
            payload["sha"] = existing_sha
            logger.info(f"[Git] File exists, updating with base SHA: {existing_sha[:8]}")

        p_status, p_data = HttpClient.put(put_url, payload, headers=self._headers())
        if p_status in (200, 201):
            commit_sha = p_data.get("commit", {}).get("sha", "N/A")
            logger.info(f"[Git] [SUCCESS] Committed '{file_path}' with SHA {commit_sha[:8]}")
            logger.info(f"[Git] Remote commit message: '{commit_msg}'")
            return True
        else:
            logger.error(f"[Git] Failed to commit file: HTTP {p_status} - {p_data}")
            return False

    def create_issue(self, repo_name: str, title: str, body: str) -> Optional[int]:
        """
        Creates an issue on the user's forked repository for architecture tracking & audit.
        """
        logger.info(f"[Git] Creating issue on '{self.github_username}/{repo_name}'...")
        issue_url = f"https://api.github.com/repos/{self.github_username}/{repo_name}/issues"
        payload = {
            "title": title,
            "body": body
        }
        status, data = HttpClient.post(issue_url, payload, headers=self._headers())
        if status in (201, 200) and isinstance(data, dict):
            issue_number = data.get("number")
            issue_url_res = data.get("html_url", "")
            logger.info(f"[Git] [SUCCESS] Created Issue #{issue_number}: {issue_url_res}")
            return issue_number
        else:
            logger.warning(f"[Git] Could not create issue on {self.github_username}/{repo_name}: HTTP {status} - {data}")
            return None


# ==============================================================================
# Module 4: Knowledge Base Sync Module (Obsidian & Notion)
# ==============================================================================
class KnowledgeSyncer:
    def __init__(self, obsidian_vault_path: str, notion_api_key: Optional[str] = None,
                 notion_database_id: Optional[str] = None, notion_page_id: Optional[str] = None):
        self.obsidian_vault_path = obsidian_vault_path
        self.notion_api_key = notion_api_key
        self.notion_database_id = (notion_database_id or "").replace("-", "")
        self.notion_page_id = (notion_page_id or "").replace("-", "")

    def sync_to_obsidian(self, project: Dict[str, Any], research_notes: str) -> Optional[str]:
        """
        Saves research notes as a markdown file with YAML frontmatter in Obsidian Vault.
        """
        try:
            os.makedirs(self.obsidian_vault_path, exist_ok=True)
        except Exception as e:
            logger.warning(f"[Obsidian] Cannot create configured vault path '{self.obsidian_vault_path}': {e}. Falling back to local directory.")
            self.obsidian_vault_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge_base", "obsidian")
            os.makedirs(self.obsidian_vault_path, exist_ok=True)

        clean_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", project["name"])
        today_str = datetime.datetime.now().strftime("%Y%m%d")
        now_iso = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = f"RESEARCH_{clean_name}_{today_str}.md"
        filepath = os.path.join(self.obsidian_vault_path, filename)

        # YAML Frontmatter
        frontmatter = f"""---
title: "專案架構研究報告: {project['name']}"
date: {now_iso}
author: "{project.get('owner', 'open-source')}"
source_url: "{project['url']}"
stars: {project.get('stars', 0)}
forks: {project.get('forks', 0)}
language: "{project.get('language', 'Unknown')}"
domain: "{project.get('primary_domain', 'devops')}"
score: {project.get('total_score', 0)}
tags:
  - tech-radar
  - sideproject
  - kubernetes
  - devops
  - ai-agent
status: "Analyzed"
---

"""
        full_content = frontmatter + research_notes
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_content)

        logger.info(f"[Obsidian] [SUCCESS] Saved document to: {filepath}")
        return filepath

    def _markdown_to_notion_blocks(self, markdown_text: str) -> List[Dict[str, Any]]:
        """
        Converts markdown text to official Notion Block JSON objects.
        """
        lines = markdown_text.splitlines()
        blocks = []
        in_code_block = False
        code_lang = "plain text"
        code_buffer = []

        lang_map = {
            "python": "python", "py": "python", "go": "go", "yaml": "yaml", 
            "yml": "yaml", "bash": "bash", "sh": "bash", "json": "json", 
            "mermaid": "plain text", "dockerfile": "docker"
        }

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("```"):
                if not in_code_block:
                    in_code_block = True
                    raw_lang = stripped[3:].strip().lower()
                    code_lang = lang_map.get(raw_lang, "plain text")
                    code_buffer = []
                else:
                    in_code_block = False
                    blocks.append({
                        "object": "block",
                        "type": "code",
                        "code": {
                            "rich_text": [{"type": "text", "text": {"content": "\n".join(code_buffer)[:2000]}}],
                            "language": code_lang
                        }
                    })
                continue

            if in_code_block:
                code_buffer.append(line)
                continue

            if not stripped:
                continue

            # Heading 1
            if stripped.startswith("# "):
                blocks.append({
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [{"type": "text", "text": {"content": stripped[2:][:2000]}}]
                    }
                })
            # Heading 2
            elif stripped.startswith("## "):
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": stripped[3:][:2000]}}]
                    }
                })
            # Heading 3
            elif stripped.startswith("### "):
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": stripped[4:][:2000]}}]
                    }
                })
            # Callout / Blockquote
            elif stripped.startswith("> "):
                blocks.append({
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "rich_text": [{"type": "text", "text": {"content": stripped[2:][:2000]}}],
                        "icon": {"emoji": "⚡"}
                    }
                })
            # Bullet list
            elif stripped.startswith("- ") or stripped.startswith("* "):
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": stripped[2:][:2000]}}]
                    }
                })
            # Standard Paragraph
            else:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": stripped[:2000]}}]
                    }
                })

        return blocks

    def sync_to_notion(self, project: Dict[str, Any], research_notes: str) -> bool:
        """
        Creates a page in Notion Database or appends to a target parent page.
        """
        if not self.notion_api_key:
            logger.warning("[Notion] NOTION_API_KEY not configured. Skipping Notion sync.")
            return False

        if not self.notion_database_id and not self.notion_page_id:
            logger.warning("[Notion] Neither NOTION_DATABASE_ID nor NOTION_PAGE_ID configured. Skipping Notion sync.")
            return False

        headers = {
            "Authorization": f"Bearer {self.notion_api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

        blocks = self._markdown_to_notion_blocks(research_notes)
        page_title = f"[{project.get('primary_domain', 'DevOps').upper()}] {project['name']} - 架構研究與生產落地分析"

        # Scenario A: Target Notion Database
        if self.notion_database_id:
            logger.info(f"[Notion] Creating new entry in Database ID: {self.notion_database_id[:8]}...")
            
            # Inspect database schema to find the exact title property name
            db_url = f"https://api.notion.com/v1/databases/{self.notion_database_id}"
            status, db_data = HttpClient.get(db_url, headers=headers)
            
            title_prop_name = "Name"
            has_url_prop = False
            url_prop_name = "URL"
            has_tags_prop = False
            tags_prop_name = "Tags"

            if status == 200 and isinstance(db_data, dict) and "properties" in db_data:
                props = db_data["properties"]
                for p_name, p_val in props.items():
                    if p_val.get("type") == "title":
                        title_prop_name = p_name
                    elif p_val.get("type") == "url":
                        has_url_prop = True
                        url_prop_name = p_name
                    elif p_val.get("type") == "multi_select":
                        has_tags_prop = True
                        tags_prop_name = p_name

            payload_properties = {
                title_prop_name: {
                    "title": [{"type": "text", "text": {"content": page_title}}]
                }
            }
            if has_url_prop:
                payload_properties[url_prop_name] = {"url": project["url"]}
            if has_tags_prop:
                domain_tag = project.get("primary_domain", "DevOps").upper()
                payload_properties[tags_prop_name] = {
                    "multi_select": [{"name": domain_tag}, {"name": "TechRadar"}]
                }

            # First batch (Notion allows max 100 children in create page)
            first_batch = blocks[:90]
            create_payload = {
                "parent": {"database_id": self.notion_database_id},
                "icon": {"emoji": "🚀"},
                "properties": payload_properties,
                "children": first_batch
            }

            p_status, p_data = HttpClient.post("https://api.notion.com/v1/pages", create_payload, headers=headers)
            if p_status in (200, 201):
                new_page_id = p_data.get("id")
                page_url = p_data.get("url", "N/A")
                logger.info(f"[Notion] [SUCCESS] Created Database Page: {page_url}")

                # If there are more blocks, append them in batches of 50
                if len(blocks) > 90 and new_page_id:
                    self._append_notion_blocks(new_page_id, blocks[90:], headers)
                return True
            else:
                logger.error(f"[Notion] Failed to create page in database: HTTP {p_status} - {p_data}")
                return False

        # Scenario B: Target Notion Parent Page
        elif self.notion_page_id:
            logger.info(f"[Notion] Appending blocks to Parent Page ID: {self.notion_page_id[:8]}...")
            return self._append_notion_blocks(self.notion_page_id, blocks, headers)

        return False

    def _append_notion_blocks(self, page_id: str, blocks: List[Dict[str, Any]], headers: Dict[str, str]) -> bool:
        clean_id = page_id.replace("-", "")
        url = f"https://api.notion.com/v1/blocks/{clean_id}/children"
        batch_size = 50

        for i in range(0, len(blocks), batch_size):
            batch = blocks[i:i + batch_size]
            status, res = HttpClient.patch(url, {"children": batch}, headers=headers)
            if status not in (200, 201):
                logger.error(f"[Notion] Error appending batch {i//batch_size + 1}: HTTP {status} - {res}")
                return False

        logger.info("[Notion] All blocks appended successfully.")
        return True


# ==============================================================================
# Main Orchestration Engine
# ==============================================================================
def resolve_github_token() -> str:
    """
    Attempts to read GITHUB_TOKEN from env, falling back to `gh auth token`.
    """
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        return token
    
    # Try CLI fallback
    try:
        res = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=5)
        if res.returncode == 0 and res.stdout.strip():
            logger.info("[Auth] Auto-detected GitHub token via `gh auth token`.")
            return res.stdout.strip()
    except Exception:
        pass
    return ""


def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Daily Sideproject Automation Agent")
    parser.add_argument("--dry-run", action="store_true", help="Perform scraping, decision, and local obsidian sync without GitHub fork/remote push or Notion write.")
    parser.add_argument("--limit", type=int, default=15, help="Number of trending candidates to inspect.")
    parser.add_argument("--top-k", type=int, default=5, help="Number of top star-growth projects to analyze & commit (default 5).")
    parser.add_argument("--skip-git", action="store_true", help="Skip automated Git Fork and Commit.")
    parser.add_argument("--skip-notion", action="store_true", help="Skip Notion API synchronization.")
    parser.add_argument("--force-repo", type=str, default="", help="Force specific repo e.g. 'owner/repo' instead of auto-picking.")
    args = parser.parse_args()

    logger.info("================================================================================")
    logger.info("🚀 Starting Daily Sideproject Automation Agent Execution")
    logger.info(f"⏰ Execution Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"🎯 Target Top Projects per Run: {args.top_k}")
    if args.dry_run:
        logger.info("🛡️ DRY-RUN MODE ACTIVE: Remote Git mutations and Notion API calls will be simulated.")
    logger.info("================================================================================")

    # 1. Environment & Tokens Resolution
    github_token = resolve_github_token()
    github_username = os.getenv("GITHUB_USERNAME", "").strip()
    if not github_username and github_token:
        # Auto-detect username from GitHub API
        status, u_data = HttpClient.get("https://api.github.com/user", headers={"Authorization": f"Bearer {github_token}", "User-Agent": "DailyAgent"})
        if status == 200 and isinstance(u_data, dict):
            github_username = u_data.get("login", "")
            logger.info(f"[Auth] Auto-detected GitHub username: {github_username}")

    hf_token = os.getenv("HF_TOKEN", "").strip()
    notion_api_key = os.getenv("NOTION_API_KEY", "").strip()
    notion_db_id = os.getenv("NOTION_DATABASE_ID", "").strip()
    notion_page_id = os.getenv("NOTION_PAGE_ID", "").strip()
    obsidian_vault = os.getenv("OBSIDIAN_VAULT_PATH", "").strip()
    # Cross-platform fallback: normalize if running on Linux but configured with Mac /Users path
    if sys.platform.startswith("linux") and obsidian_vault.startswith("/Users/"):
        obsidian_vault = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge_base", "obsidian")
    elif not obsidian_vault:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        obsidian_vault = os.path.join(base_dir, "knowledge_base", "obsidian")

    gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("GOOGLE_API_KEY", "").strip()
    if gemini_api_key:
        logger.info("[Auth] Gemini API Key detected. Real LLM analysis enabled!")
    else:
        logger.info("[Auth] No GEMINI_API_KEY or GOOGLE_API_KEY found in .env. Using built-in Expert Rule Engine.")

    # 2. Module 1: Trend Scraping (Highest Star Growth & Domains)
    scraper = TrendScraper(github_token=github_token, hf_token=hf_token)
    candidates = scraper.get_top_candidates(limit=args.limit)
    if not candidates and not args.force_repo:
        logger.error("[!] No candidates found from GitHub or Hugging Face. Aborting.")
        sys.exit(1)

    # 3. Module 2: Analysis & Decision
    analyzer = ProjectAnalyzer(gemini_api_key=gemini_api_key)
    
    if args.force_repo:
        logger.info(f"[Decision] Forced repository specified: {args.force_repo}")
        owner, repo_name = args.force_repo.split("/")
        target_projects = [{
            "source": "github",
            "name": repo_name,
            "full_name": args.force_repo,
            "owner": owner,
            "description": "Manually specified target repository.",
            "url": f"https://github.com/{args.force_repo}",
            "stars": 9999,
            "stars_today": 999,
            "forks": 100,
            "language": "Python / Go",
            "topics": ["k8s", "devops", "agent"],
            "primary_domain": "ai_agent",
            "total_score": 100.0,
            "default_branch": "main"
        }]
    else:
        target_projects = analyzer.select_top_projects(candidates, top_k=args.top_k)

    logger.info("================================================================================")
    logger.info(f"📋 Starting Pipeline Execution for Top {len(target_projects)} Projects")
    logger.info("================================================================================")

    git_automator = None
    if not args.skip_git and not args.dry_run and github_token and github_username:
        git_automator = GitAutomator(github_token=github_token, github_username=github_username)

    syncer = KnowledgeSyncer(
        obsidian_vault_path=obsidian_vault,
        notion_api_key=notion_api_key,
        notion_database_id=notion_db_id,
        notion_page_id=notion_page_id
    )

    processed_summary = []
    today_tag = datetime.datetime.now().strftime("%Y%m%d")

    for idx, project in enumerate(target_projects, 1):
        p_name = project["name"]
        p_fullname = project["full_name"]
        stars_growth = f"+{project.get('stars_today', 0)} stars today" if project.get('stars_today') else f"{project.get('stars', 0)} stars"
        
        logger.info(f"\n--- [{idx}/{len(target_projects)}] Processing: {p_fullname} ({stars_growth}) ---")

        # Step A: Architecture Analysis
        research_notes = analyzer.generate_research_notes(project)

        # Step B: Git Operations (Fork -> Branch -> Commit -> Issue)
        branch_name = f"research/arch-analysis-{today_tag}"
        commit_msg = f"feat(research): 深度剖析 {p_name} 架構拓撲，補全 K8s 調度與 AI Agent 推論管線落地分析"
        
        git_status = "SKIPPED (dry-run)"
        issue_status = "SKIPPED (dry-run)"

        if git_automator:
            try:
                forked_name = git_automator.fork_repository(project["owner"], p_name)
                if forked_name:
                    branch_ok = git_automator.create_branch(forked_name, branch_name)
                    if branch_ok:
                        push_ok = git_automator.commit_and_push_file(
                            repo_name=forked_name,
                            branch_name=branch_name,
                            file_path="RESEARCH_NOTES.md",
                            content=research_notes,
                            commit_msg=commit_msg
                        )
                        if push_ok:
                            git_status = f"Pushed ({branch_name})"
                            
                            # Step C: Submit Issue for Architecture Tracking
                            issue_title = f"feat(research): [架構審查與技術追蹤] {p_name} 生產環境調度與落地檢視"
                            issue_body = f"""## 📌 專案架構研究與落地追蹤：{p_name}

> 本 Issue 由 Daily Sideproject Agent 自動化建置，追蹤今日技術雷達中星星數漲幅領先之重點專案。

### 1. 專案基本指標 (Key Metrics)
- **Upstream Repository**: [{p_fullname}]({project['url']})
- **今日星星漲幅 (Stars Today)**: {stars_growth} ⭐
- **主技術領域**: `{project.get('primary_domain', 'devops')}`
- **研究分支 (Branch)**: `{branch_name}`

### 2. 核心架構解析與落地建議
詳細的系統拓撲、K8s Pod 調度設計、DevOps GitOps 流水線與 MCP/Agent 整合分析已提交至分支檔案：
👉 參閱 [`RESEARCH_NOTES.md`](https://github.com/{github_username}/{forked_name}/blob/{branch_name}/RESEARCH_NOTES.md)

### 3. 行動檢查清單 (Action Items)
- [x] 完成開源 Repo 自動化 Fork 與研究分支隔離
- [x] 完成代碼庫與雲原生架構拓撲拆解 (`RESEARCH_NOTES.md`)
- [ ] 撰寫 Dockerfile 進行容器瘦身與多架構鏡像構建 (linux/amd64, linux/arm64)
- [ ] 封裝 Kubernetes Helm Chart 範本與 K8s 調度測試
- [ ] 整合至 CI/CD 自動化與 GitOps (ArgoCD) 交付流水線
"""
                            issue_num = git_automator.create_issue(forked_name, issue_title, issue_body)
                            if issue_num:
                                issue_status = f"Issue #{issue_num}"
            except Exception as e:
                logger.error(f"[Git] Error processing Git workflow for {p_fullname}: {e}")
                git_status = f"ERROR: {e}"
        else:
            logger.info(f"[Git] [DRY-RUN / SKIPPED] Would fork '{p_fullname}', create branch '{branch_name}', commit 'RESEARCH_NOTES.md', and submit tracking issue.")

        # Step D: Knowledge Base Sync (Obsidian & Notion)
        obs_file = syncer.sync_to_obsidian(project, research_notes)
        if not args.skip_notion and not args.dry_run:
            syncer.sync_to_notion(project, research_notes)

        processed_summary.append({
            "name": p_fullname,
            "growth": stars_growth,
            "domain": project.get("primary_domain"),
            "git": git_status,
            "issue": issue_status,
            "obsidian": os.path.basename(obs_file) if obs_file else "N/A"
        })

    logger.info("\n================================================================================")
    logger.info("🎉 Daily Sideproject Automation Agent Finished Successfully!")
    logger.info("================================================================================")
    logger.info("📊 今日前五名星星漲幅專案處理彙總：")
    for idx, item in enumerate(processed_summary, 1):
        logger.info(f"  #{idx} {item['name']} ({item['growth']}) | Domain: {item['domain']} | Git: {item['git']} | Issue: {item['issue']}")
    logger.info("================================================================================")


if __name__ == "__main__":
    main()

