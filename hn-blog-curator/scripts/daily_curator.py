#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from fetch_hn_top import fetch_stories  # noqa: E402

STRONG_KEYWORDS = {
    "agent": "直接关联 agent 工作流或基础设施",
    "agents": "直接关联 agent 工作流或基础设施",
    "ai": "和 AI 产业或工具链直接相关",
    "llm": "和模型能力或部署直接相关",
    "gpt": "和模型能力或部署直接相关",
    "claude": "和模型能力或部署直接相关",
    "gemini": "和模型能力或部署直接相关",
    "openai": "来自核心模型/平台厂商，通常有行业信号",
    "anthropic": "来自核心模型/平台厂商，通常有行业信号",
    "google": "来自核心模型/平台厂商，通常有行业信号",
    "meta": "来自核心模型/平台厂商，通常有行业信号",
    "mistral": "来自核心模型/平台厂商，通常有行业信号",
    "cursor": "开发者工作流变化，适合 Agent Economy 角度",
    "codex": "开发者工作流变化，适合 Agent Economy 角度",
    "mcp": "协议/工具链变化，适合 Agent Economy 角度",
    "protocol": "协议层变化，值得关注",
    "api": "平台接口或基础设施变化，值得关注",
    "infra": "基础设施主题契合博客方向",
    "infrastructure": "基础设施主题契合博客方向",
    "cloud": "云与算力供给变化有产业意义",
    "gpu": "算力与硬件供给主题契合",
    "chip": "硬件/芯片层变化有产业意义",
    "chips": "硬件/芯片层变化有产业意义",
    "security": "安全与信任是核心主题",
    "privacy": "隐私与信任是核心主题",
    "trust": "信任与验证是核心主题",
    "auth": "身份/认证相关，契合安全与信任主题",
    "identity": "身份/认证相关，契合安全与信任主题",
    "payment": "支付与交易基础设施值得关注",
    "payments": "支付与交易基础设施值得关注",
    "market": "市场结构变化可能适合写分析",
    "developer": "开发者工具变化可能影响 AI 生产方式",
    "tool": "工具链变化可能影响 AI 生产方式",
    "tools": "工具链变化可能影响 AI 生产方式",
    "open source": "开源项目若足够强，适合延展成博客观点",
}

MAYBE_KEYWORDS = {
    "startup": "可能有商业或产品角度，但信号未必够强",
    "browser": "可能涉及平台入口或分发层",
    "search": "可能涉及分发入口或用户工作流",
    "design": "如果切中 AI 工作流，也许值得看",
    "automation": "自动化工具偶尔适合 Agent Economy 视角",
    "workflow": "工作流变化可能有延展空间",
    "productivity": "生产力工具有时能映射到 agent 工作流",
}

HIGH_SIGNAL_DOMAINS = {
    "openai.com",
    "anthropic.com",
    "googleblog.com",
    "blog.google",
    "deepmind.google",
    "mistral.ai",
    "meta.com",
    "engineering.fb.com",
    "github.blog",
    "vercel.com",
    "cloud.google.com",
    "aws.amazon.com",
    "azure.microsoft.com",
    "developer.nvidia.com",
    "huggingface.co",
    "pytorch.org",
}

LOW_SIGNAL_TOKENS = {
    "show hn",
    "ask hn",
    "who is hiring",
    "launch hn",
    "tell hn",
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def root_domain(url: str) -> str:
    host = urlparse(url or "").netloc.lower()
    return host[4:] if host.startswith("www.") else host


def classify(item: dict):
    title = normalize(item.get("title", ""))
    domain = root_domain(item.get("url") or "")
    score = int(item.get("score") or 0)
    comments = int(item.get("comments") or 0)

    if any(token in title for token in LOW_SIGNAL_TOKENS):
        return None

    strong_hits = []
    maybe_hits = []

    for key, reason in STRONG_KEYWORDS.items():
        if key in title:
            strong_hits.append(reason)
    for key, reason in MAYBE_KEYWORDS.items():
        if key in title:
            maybe_hits.append(reason)

    if domain in HIGH_SIGNAL_DOMAINS:
        strong_hits.append("来源站点本身信号较强")

    if score >= 250:
        strong_hits.append("HN 热度高，说明讨论度足够")
    elif score >= 120:
        maybe_hits.append("HN 热度还不错，可以留作候选")

    if comments >= 80:
        maybe_hits.append("评论活跃，说明有争议或行业关注")

    if strong_hits:
        tier = "strong"
        reason = strong_hits[0]
    elif maybe_hits:
        tier = "maybe"
        reason = maybe_hits[0]
    else:
        return None

    if tier == "strong" and score < 80 and comments < 20 and domain not in HIGH_SIGNAL_DOMAINS:
        tier = "maybe"
        reason = "主题相关，但当前信号还偏弱"

    return {
        "tier": tier,
        "reason": reason,
        "domain": domain,
        "score": score,
        "comments": comments,
    }


def fmt_item(item: dict, reason: str) -> str:
    url = item.get("url") or f"https://news.ycombinator.com/item?id={item.get('id')}"
    return f"- {item.get('title')} — {url} — {reason}"


def main():
    items = fetch_stories(30, "top")
    strong = []
    maybe = []

    for item in items:
        result = classify(item)
        if not result:
            continue
        formatted = fmt_item(item, result["reason"])
        if result["tier"] == "strong" and len(strong) < 5:
            strong.append(formatted)
        elif len(maybe) < 6:
            maybe.append(formatted)

    lines = ["Strong picks"]
    if strong:
        lines.extend(strong)
    else:
        lines.append("- 今天没有特别强的 HN 选题。")

    if maybe:
        lines.extend(["", "Maybe picks", *maybe])

    print("\n".join(lines))


if __name__ == "__main__":
    main()
