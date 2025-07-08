#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# <xbar.title>Claude Usage Monitor</xbar.title>
# <xbar.version>v1.0</xbar.version>
# <xbar.author>Claude Code Assistant</xbar.author>
# <xbar.desc>Monitors Claude API usage and costs from ~/.claude/projects</xbar.desc>
# <xbar.dependencies>python3</xbar.dependencies>

import json
import os
from pathlib import Path
from decimal import Decimal, getcontext
from datetime import datetime
from collections import defaultdict

# Set precision for currency calculations
getcontext().prec = 10

# Model pricing configuration (per million tokens)
MODEL_PRICING = {
    "opus-4": {
        "name": "Opus 4",
        "input_per_million": 15.0,
        "output_per_million": 75.0,
        "cache_write_per_million": 18.75,
        "cache_read_per_million": 1.50
    },
    "sonnet-4": {
        "name": "Sonnet 4", 
        "input_per_million": 3.0,
        "output_per_million": 15.0,
        "cache_write_per_million": 3.75,
        "cache_read_per_million": 0.30
    },
    "claude-4-opus": {
        "name": "Opus 4",
        "input_per_million": 15.0,
        "output_per_million": 75.0,
        "cache_write_per_million": 18.75,
        "cache_read_per_million": 1.50
    },
    "claude-4-sonnet": {
        "name": "Sonnet 4",
        "input_per_million": 3.0,
        "output_per_million": 15.0,
        "cache_write_per_million": 3.75,
        "cache_read_per_million": 0.30
    },
    "claude-opus-4": {
        "name": "Opus 4",
        "input_per_million": 15.0,
        "output_per_million": 75.0,
        "cache_write_per_million": 18.75,
        "cache_read_per_million": 1.50
    },
    "claude-sonnet-4": {
        "name": "Sonnet 4",
        "input_per_million": 3.0,
        "output_per_million": 15.0,
        "cache_write_per_million": 3.75,
        "cache_read_per_million": 0.30
    }
}

def get_model_pricing(model_str):
    """Get pricing for a model based on its name."""
    if not model_str:
        return None
    
    model_lower = model_str.lower()
    for key, pricing in MODEL_PRICING.items():
        if key in model_lower:
            return pricing
    return None

def calculate_cost(model, usage_data):
    """Calculate cost for a single usage entry."""
    pricing = get_model_pricing(model)
    if not pricing:
        return Decimal(0)
    
    input_tokens = Decimal(usage_data.get("input_tokens", 0))
    output_tokens = Decimal(usage_data.get("output_tokens", 0))
    cache_creation = Decimal(usage_data.get("cache_creation_input_tokens", 0))
    cache_read = Decimal(usage_data.get("cache_read_input_tokens", 0))
    
    input_cost = (input_tokens * Decimal(pricing["input_per_million"])) / Decimal(1_000_000)
    output_cost = (output_tokens * Decimal(pricing["output_per_million"])) / Decimal(1_000_000)
    cache_write_cost = (cache_creation * Decimal(pricing["cache_write_per_million"])) / Decimal(1_000_000)
    cache_read_cost = (cache_read * Decimal(pricing["cache_read_per_million"])) / Decimal(1_000_000)
    
    return input_cost + output_cost + cache_write_cost + cache_read_cost

def parse_jsonl_files():
    """Parse all JSONL files in ~/.claude/projects/"""
    claude_dir = Path.home() / ".claude" / "projects"
    
    if not claude_dir.exists():
        return None, "Claude directory not found"
    
    total_cost = Decimal(0)
    today_cost = Decimal(0)
    cost_by_project = defaultdict(Decimal)
    cost_by_model = defaultdict(Decimal)
    token_counts = {
        "input": 0,
        "output": 0,
        "cache_write": 0,
        "cache_read": 0
    }
    today_token_counts = {
        "input": 0,
        "output": 0,
        "cache_write": 0,
        "cache_read": 0
    }
    session_count = 0
    today_session_count = 0
    processed_messages = set()
    
    # Get today's date in ISO format
    today = datetime.now().date().isoformat()
    
    # Walk through all project directories
    for project_dir in claude_dir.iterdir():
        if not project_dir.is_dir():
            continue
            
        project_name = project_dir.name
        
        # Find all JSONL files in project subdirectories
        for jsonl_file in project_dir.rglob("*.jsonl"):
            try:
                with open(jsonl_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if not line.strip():
                            continue
                            
                        try:
                            data = json.loads(line)
                            
                            # Extract message data if present
                            message = data.get("message", {})
                            if not message:
                                continue
                                
                            # Check for duplicate messages
                            msg_id = message.get("id")
                            req_id = data.get("requestId")
                            if msg_id and req_id:
                                unique_key = f"{msg_id}:{req_id}"
                                if unique_key in processed_messages:
                                    continue
                                processed_messages.add(unique_key)
                            
                            usage = message.get("usage", {})
                            if not usage:
                                continue
                                
                            # Skip entries with no token usage
                            if all(usage.get(k, 0) == 0 for k in ["input_tokens", "output_tokens", 
                                   "cache_creation_input_tokens", "cache_read_input_tokens"]):
                                continue
                            
                            model = message.get("model", "")
                            
                            # Use provided cost if available, otherwise calculate
                            if "costUSD" in data:
                                cost = Decimal(str(data["costUSD"]))
                            else:
                                cost = calculate_cost(model, usage)
                            
                            if cost > 0:
                                total_cost += cost
                                cost_by_project[project_name] += cost
                                
                                pricing = get_model_pricing(model)
                                if pricing:
                                    cost_by_model[pricing["name"]] += cost
                                
                                # Track token counts
                                token_counts["input"] += usage.get("input_tokens", 0)
                                token_counts["output"] += usage.get("output_tokens", 0)
                                token_counts["cache_write"] += usage.get("cache_creation_input_tokens", 0)
                                token_counts["cache_read"] += usage.get("cache_read_input_tokens", 0)
                                
                                session_count += 1
                                
                                # Check if this is from today
                                timestamp = data.get("timestamp", "")
                                if timestamp.startswith(today):
                                    today_cost += cost
                                    today_token_counts["input"] += usage.get("input_tokens", 0)
                                    today_token_counts["output"] += usage.get("output_tokens", 0)
                                    today_token_counts["cache_write"] += usage.get("cache_creation_input_tokens", 0)
                                    today_token_counts["cache_read"] += usage.get("cache_read_input_tokens", 0)
                                    today_session_count += 1
                                
                        except json.JSONDecodeError:
                            continue
                            
            except Exception:
                continue
    
    return {
        "total_cost": total_cost,
        "today_cost": today_cost,
        "cost_by_project": dict(cost_by_project),
        "cost_by_model": dict(cost_by_model),
        "token_counts": token_counts,
        "today_token_counts": today_token_counts,
        "session_count": session_count,
        "today_session_count": today_session_count
    }, None

def format_currency(amount):
    """Format decimal as currency."""
    return f"${amount:.2f}"

def format_tokens(count):
    """Format token count with appropriate units."""
    if count >= 1_000_000:
        return f"{count/1_000_000:.1f}M"
    elif count >= 1_000:
        return f"{count/1_000:.1f}K"
    else:
        return str(count)

def main():
    """Main function to generate xbar output."""
    result, error = parse_jsonl_files()
    
    if error:
        print(f"⚠️ {error}")
        print("---")
        print("Error loading Claude usage data")
        return
    
    if not result or result["total_cost"] == 0:
        print("🤖 $0.00")
        print("---")
        print("No Claude usage found")
        print("---")
        print("📁 View Claude Projects | bash=open | param1=~/.claude/projects")
        return
    
    # Menu bar display - show today's cost if significant
    if result["today_cost"] > 1:
        print(f"🤖 {format_currency(result['total_cost'])} (↑{format_currency(result['today_cost'])})")
    else:
        print(f"🤖 {format_currency(result['total_cost'])}")
    print("---")
    
    # Overview Section
    print("💰 Overview")
    print(f"Total Cost: {format_currency(result['total_cost'])} | color=#000000 font=Menlo-Bold size=13")
    print(f"Sessions: {result['session_count']:,} | color=#666666 font=Menlo size=12")
    
    # Calculate average cost per session
    avg_cost = result['total_cost'] / result['session_count'] if result['session_count'] > 0 else 0
    print(f"Average: {format_currency(avg_cost)}/session | color=#666666 font=Menlo size=12")
    print("---")
    
    # Today's usage with visual emphasis
    if result["today_cost"] > 0:
        print("📅 Today")
        print(f"Cost: {format_currency(result['today_cost'])} | color=#007AFF font=Menlo-Bold size=12")
        print(f"Sessions: {result['today_session_count']:,} | color=#666666 font=Menlo size=12")
        today_total_tokens = sum(result['today_token_counts'].values())
        print(f"Tokens: {format_tokens(today_total_tokens)} | color=#666666 font=Menlo size=12")
        print("---")
    
    # Token breakdown with icons
    total_tokens = sum(result['token_counts'].values())
    print("🔤 Token Usage")
    print(f"Total: {format_tokens(total_tokens)} | color=#000000 font=Menlo-Bold size=12")
    print(f"├─ Input: {format_tokens(result['token_counts']['input'])} | color=#666666 font=Menlo size=11")
    print(f"├─ Output: {format_tokens(result['token_counts']['output'])} | color=#666666 font=Menlo size=11")
    print(f"├─ Cache Write: {format_tokens(result['token_counts']['cache_write'])} | color=#666666 font=Menlo size=11")
    print(f"└─ Cache Read: {format_tokens(result['token_counts']['cache_read'])} | color=#666666 font=Menlo size=11")
    print("---")
    
    # Cost by model with visual bars
    if result["cost_by_model"]:
        print("🎯 By Model")
        sorted_models = sorted(result["cost_by_model"].items(), 
                             key=lambda x: x[1], reverse=True)
        max_cost = sorted_models[0][1] if sorted_models else 1
        
        for model, cost in sorted_models:
            # Create a simple visual bar
            bar_length = int((cost / max_cost) * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            percentage = (cost / result['total_cost']) * 100
            print(f"{model}: {format_currency(cost)} ({percentage:.1f}%) | font=Menlo size=11")
            print(f"{bar} | color=#999999 font=Menlo size=8")
        print("---")
    
    # Cost by project (top 5) with better formatting
    if result["cost_by_project"]:
        print("📁 Top Projects")
        sorted_projects = sorted(result["cost_by_project"].items(), 
                               key=lambda x: x[1], reverse=True)[:5]
        
        for i, (project, cost) in enumerate(sorted_projects):
            # Decode project name if needed
            try:
                if project.startswith("_"):
                    # Likely an encoded path
                    display_name = project.split("_")[-1] if "_" in project else project
                else:
                    display_name = project
                
                # Truncate long names
                if len(display_name) > 30:
                    display_name = display_name[:27] + "..."
                    
                icon = "├─" if i < len(sorted_projects) - 1 else "└─"
                print(f"{icon} {display_name} | font=Menlo size=11")
                print(f"   {format_currency(cost)} | color=#666666 font=Menlo size=10")
            except:
                print(f"{icon} {project}: {format_currency(cost)} | font=Menlo size=11")
        
        if len(result["cost_by_project"]) > 5:
            print(f"   ...and {len(result['cost_by_project']) - 5} more | color=#999999 font=Menlo size=10")
        print("---")
    
    # Actions
    print("🔧 Actions")
    print("Refresh | refresh=true")
    print("View Claude Projects | bash=open | param1=~/.claude/projects")
    print("---")
    
    # Footer with last update time
    now = datetime.now().strftime("%I:%M %p")
    print(f"Last updated: {now} | color=#999999 font=Menlo size=10")

if __name__ == "__main__":
    main()