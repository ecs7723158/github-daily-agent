import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from daily_sideproject_agent import (
    ProjectAnalyzer,
    KnowledgeSyncer,
    TrendScraper,
    GitAutomator,
)


def test_analyzer_scoring_and_top_selection():
    analyzer = ProjectAnalyzer()
    
    candidates = [
        {
            "name": "cool-k8s-operator",
            "full_name": "cloud-native/cool-k8s-operator",
            "description": "Autonomous Kubernetes controller for autoscaling and microservices",
            "stars": 1500,
            "stars_today": 320,
            "language": "Go",
            "source": "github",
        },
        {
            "name": "ai-agent-framework",
            "full_name": "ai/ai-agent-framework",
            "description": "Multi-agent autonomous framework with LLM tool calling",
            "stars": 8500,
            "stars_today": 950,
            "language": "Python",
            "source": "github",
        },
        {
            "name": "random-css-theme",
            "full_name": "web/random-css-theme",
            "description": "A collection of plain CSS buttons and styling",
            "stars": 50,
            "stars_today": 5,
            "language": "CSS",
            "source": "github",
        },
    ]
    
    score1, _, rationale1 = analyzer.calculate_score(candidates[0])
    score2, _, rationale2 = analyzer.calculate_score(candidates[1])
    score3, _, rationale3 = analyzer.calculate_score(candidates[2])
    
    assert score1 > 0
    assert score2 > 0
    assert score1 > score3
    assert score2 > score3
    
    top_projects = analyzer.select_top_projects(candidates, top_k=2)
    assert len(top_projects) == 2
    assert top_projects[0]["name"] in ["cool-k8s-operator", "ai-agent-framework"]
    assert top_projects[1]["name"] in ["cool-k8s-operator", "ai-agent-framework"]


def test_research_notes_generation():
    analyzer = ProjectAnalyzer()
    sample_proj = {
        "name": "kueue-batch",
        "full_name": "kubernetes-sigs/kueue",
        "description": "Kubernetes-native Job Queueing Controller",
        "stars": 4200,
        "stars_today": 180,
        "language": "Go",
        "url": "https://github.com/kubernetes-sigs/kueue",
        "source": "github",
    }
    notes = analyzer.generate_research_notes(sample_proj)
    assert "專案架構深潛分析" in notes
    assert "kueue" in notes
    assert "核心價值與架構摘要" in notes
    assert "系統拓撲與技術棧拆解" in notes


def test_obsidian_knowledge_sync():
    with tempfile.TemporaryDirectory() as tmpdir:
        syncer = KnowledgeSyncer(obsidian_vault_path=tmpdir)
        proj = {
            "name": "test-repo",
            "full_name": "test-owner/test-repo",
            "description": "Test description",
            "stars": 100,
            "language": "Python",
            "url": "https://github.com/test-owner/test-repo",
            "source": "github",
        }
        notes = "### Architecture\nThis is a test architectural analysis."
        
        file_path = syncer.sync_to_obsidian(proj, notes)
        assert file_path is not None
        assert os.path.exists(file_path)
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "---" in content  # YAML frontmatter
            assert "test-owner/test-repo" in content
            assert notes in content


def test_notion_blocks_conversion():
    syncer = KnowledgeSyncer(obsidian_vault_path="/tmp")
    md = "# Heading 1\n## Heading 2\n### Heading 3\nThis is paragraph content."
    blocks = syncer._markdown_to_notion_blocks(md)
    assert len(blocks) >= 4
    types = [b["type"] for b in blocks]
    assert "heading_1" in types
    assert "heading_2" in types
    assert "heading_3" in types
    assert "paragraph" in types


def test_git_automator_mocked_flow():
    with patch("daily_sideproject_agent.HttpClient") as mock_http:
        mock_http.get.return_value = (200, {"object": {"sha": "fake_sha_12345"}})
        mock_http.post.return_value = (201, {"ref": "refs/heads/research/test"})
        
        automator = GitAutomator(github_token="fake_token", github_username="testuser")
        success = automator.create_branch("test-repo", "research/test")
        assert success is True
