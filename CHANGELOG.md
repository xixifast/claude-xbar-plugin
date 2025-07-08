# Changelog

All notable changes to the Claude xbar Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-01-08

### Changed
- Menu bar now displays only today's cost for cleaner, more relevant information
- Simplified format to just show amount (e.g., `🤖 $125.80`) without "Today:" prefix
- Total cost still available in dropdown menu for comprehensive view

## [1.0.0] - 2024-01-08

### Added
- Initial release of Claude xbar Plugin
- Real-time cost tracking in macOS menu bar
- Today's usage statistics with visual indicators
- Token usage breakdown (input, output, cache write, cache read)
- Cost visualization by model with progress bars
- Top 5 projects by cost
- Beautiful formatting with icons and tree structure
- Auto-refresh every 10 seconds (configurable)
- Support for Claude 4 models (Opus and Sonnet)
- Decimal precision for accurate financial calculations
- Duplicate message detection to prevent overcounting
- Light and dark mode compatible display
- Quick actions (refresh, open Claude projects)
- Installation script for easy setup

### Technical Features
- Python 3 compatible
- Zero external dependencies
- Efficient JSONL parsing
- Memory-conscious design for large datasets
- Error handling for corrupted data files