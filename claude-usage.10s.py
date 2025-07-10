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
from datetime import datetime, timedelta
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
    today_cost_by_model = defaultdict(Decimal)
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
    
    # Get dates for the last 3 days in ISO format
    today = datetime.now().date().isoformat()
    yesterday = (datetime.now().date() - timedelta(days=1)).isoformat()
    day_before_yesterday = (datetime.now().date() - timedelta(days=2)).isoformat()
    
    # Track costs for the last 3 days
    daily_costs = {
        today: Decimal(0),
        yesterday: Decimal(0),
        day_before_yesterday: Decimal(0)
    }
    daily_sessions = {
        today: 0,
        yesterday: 0,
        day_before_yesterday: 0
    }
    daily_tokens = {
        today: {"input": 0, "output": 0, "cache_write": 0, "cache_read": 0},
        yesterday: {"input": 0, "output": 0, "cache_write": 0, "cache_read": 0},
        day_before_yesterday: {"input": 0, "output": 0, "cache_write": 0, "cache_read": 0}
    }
    
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
                                    
                                    # Track today's model costs
                                    pricing = get_model_pricing(model)
                                    if pricing:
                                        today_cost_by_model[pricing["name"]] += cost
                                
                                # Track costs for the last 3 days
                                for date_key in daily_costs:
                                    if timestamp.startswith(date_key):
                                        daily_costs[date_key] += cost
                                        daily_sessions[date_key] += 1
                                        # Track daily tokens
                                        daily_tokens[date_key]["input"] += usage.get("input_tokens", 0)
                                        daily_tokens[date_key]["output"] += usage.get("output_tokens", 0)
                                        daily_tokens[date_key]["cache_write"] += usage.get("cache_creation_input_tokens", 0)
                                        daily_tokens[date_key]["cache_read"] += usage.get("cache_read_input_tokens", 0)
                                        break
                                
                        except json.JSONDecodeError:
                            continue
                            
            except Exception:
                continue
    
    return {
        "total_cost": total_cost,
        "today_cost": today_cost,
        "cost_by_project": dict(cost_by_project),
        "cost_by_model": dict(cost_by_model),
        "today_cost_by_model": dict(today_cost_by_model),
        "token_counts": token_counts,
        "today_token_counts": today_token_counts,
        "session_count": session_count,
        "today_session_count": today_session_count,
        "daily_costs": dict(daily_costs),
        "daily_sessions": dict(daily_sessions),
        "daily_tokens": dict(daily_tokens),
        "dates": {
            "today": today,
            "yesterday": yesterday,
            "day_before_yesterday": day_before_yesterday
        }
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
    
    # Menu bar display - show today's cost
    print(f"🤖 {format_currency(result['today_cost'])}")
    print("---")
    
    # Overview Section
    print("💰 Overview | color=#1D1D1F font=system-bold size=12")
    print(f"Total Cost: {format_currency(result['total_cost'])} | color=#1D1D1F font=system-bold size=12")
    print(f"Sessions: {result['session_count']:,} | color=#3A3A3C font=system size=12")
    
    # Calculate average cost per session
    avg_cost = result['total_cost'] / result['session_count'] if result['session_count'] > 0 else 0
    print(f"Average: {format_currency(avg_cost)}/session | color=#3A3A3C font=system size=12")
    print("---")
    
    # Recent 3 days breakdown
    if result.get("daily_costs") and any(result["daily_costs"].values()):
        print("📊 Last 3 Days | color=#1D1D1F font=system-bold size=12")
        dates = result.get("dates", {})
        
        # Create day labels
        today_label = "Today"
        yesterday_label = "Yesterday" 
        day_before_label = "2 Days Ago"
        
        # Display each day with costs, sessions and tokens
        for i, (period, label) in enumerate([(dates.get("today"), today_label), 
                                           (dates.get("yesterday"), yesterday_label),
                                           (dates.get("day_before_yesterday"), day_before_label)]):
            if period and period in result["daily_costs"]:
                cost = result["daily_costs"][period]
                sessions = result["daily_sessions"].get(period, 0)
                daily_token_data = result["daily_tokens"].get(period, {})
                total_tokens = sum(daily_token_data.values()) if daily_token_data else 0
                
                if cost > 0 or sessions > 0:
                    icon = "├─" if i < 2 else "└─"
                    print(f"{icon} {label}: {format_currency(cost)} | color=#3A3A3C font=system size=11")
                    if sessions > 0 or total_tokens > 0:
                        session_text = f"Sessions: {sessions:,}" if sessions > 0 else "Sessions: 0"
                        token_text = f"Tokens: {format_tokens(total_tokens)}" if total_tokens > 0 else "Tokens: 0"
                        print(f"   {session_text}, {token_text} | color=#5A5A5C font=system size=10")
        print("---")
    
    # Cost by model today with visual bars
    if result["today_cost_by_model"] and result["today_cost"] > 0:
        print("🎯 By Model Today | color=#1D1D1F font=system-bold size=12")
        sorted_models = sorted(result["today_cost_by_model"].items(), 
                             key=lambda x: x[1], reverse=True)
        
        for model, cost in sorted_models:
            # Create a visual bar based on percentage of today's total
            percentage = (cost / result['today_cost']) * 100
            bar_length = int((percentage / 100) * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            print(f"{model}: {format_currency(cost)} ({percentage:.1f}%) | color=#3A3A3C font=system size=11")
            print(f"{bar} | color=#5A5A5C font=system size=8")
        print("---")
    
    # Actions
    print("🔧 Actions | color=#1D1D1F font=system-bold size=12")
    print("Refresh | refresh=true")
    print("View Claude Projects | bash=open | param1=~/.claude/projects")
    print("---")
    
    # Footer with last update time
    now = datetime.now().strftime("%I:%M %p")
    print(f"Last updated: {now} | color=#5A5A5C font=system size=10")

if __name__ == "__main__":
    main()
