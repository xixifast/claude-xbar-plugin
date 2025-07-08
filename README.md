# Claude Usage Monitor for xbar

A beautiful macOS menu bar plugin that tracks your Claude API usage and costs in real-time.

<p align="center">
  <img src="assets/screenshot-menubar.png" alt="Menu Bar Screenshot" width="300">
  <img src="assets/screenshot-dropdown.png" alt="Dropdown Screenshot" width="400">
</p>

## Features

- 🤖 **Real-time Cost Tracking** - See your total Claude API costs at a glance
- 📊 **Today's Usage** - Track daily spending with visual indicators
- 🎯 **Model Breakdown** - Visualize costs by model (Opus, Sonnet, etc.)
- 📁 **Project Analytics** - See which projects use the most tokens
- 🔤 **Token Statistics** - Detailed breakdown of input, output, and cache tokens
- 🎨 **Beautiful Display** - Clean, professional interface with icons and visual bars
- ⚡ **Auto-refresh** - Updates every 10 seconds (configurable)

## Installation

### Prerequisites

- macOS (10.12 or later)
- [xbar](https://xbarapp.com/) - Install via Homebrew: `brew install --cask xbar`
- Python 3 (included with macOS)
- Claude API usage data in `~/.claude/projects/`

### Quick Install

1. **Install xbar** (if not already installed):
   ```bash
   brew install --cask xbar
   ```

2. **Install the plugin**:
   ```bash
   # Download and install in one command
   curl -sSL https://raw.githubusercontent.com/xixifast/claude-xbar-plugin/main/install.sh | bash
   ```

### Manual Install

1. Download `claude-usage.10s.py` from this repository
2. Copy to xbar plugins directory:
   ```bash
   cp claude-usage.10s.py ~/Library/Application\ Support/xbar/plugins/
   chmod +x ~/Library/Application\ Support/xbar/plugins/claude-usage.10s.py
   ```
3. Refresh xbar or restart the app

## Configuration

### Refresh Interval

The plugin refreshes every 10 seconds by default. To change this, rename the file:

- `claude-usage.5s.py` - Refresh every 5 seconds
- `claude-usage.30s.py` - Refresh every 30 seconds
- `claude-usage.1m.py` - Refresh every minute
- `claude-usage.5m.py` - Refresh every 5 minutes

### Model Pricing

To update model pricing, edit the `MODEL_PRICING` dictionary in the script:

```python
MODEL_PRICING = {
    "opus-4": {
        "name": "Opus 4",
        "input_per_million": 15.0,
        "output_per_million": 75.0,
        "cache_write_per_million": 18.75,
        "cache_read_per_million": 1.50
    },
    # Add more models here...
}
```

## Display Format

The plugin shows:

- **Menu Bar**: Total cost with today's increase (if > $1)
  - Format: `🤖 $347.86 (↑$12.34)`

- **Dropdown Menu**:
  - 💰 **Overview**: Total cost, sessions, and average cost per session
  - 📅 **Today**: Today's cost, sessions, and token usage
  - 🔤 **Token Usage**: Detailed breakdown with tree structure
  - 🎯 **By Model**: Cost distribution with visual progress bars
  - 📁 **Top Projects**: Top 5 projects by cost
  - 🔧 **Actions**: Refresh and quick access to Claude projects

## Troubleshooting

### No data showing?

1. Check if `~/.claude/projects/` exists and contains `.jsonl` files
2. Ensure the plugin has read permissions
3. Check Console.app for any Python errors

### Incorrect costs?

The plugin uses Claude's official pricing. If you see discrepancies:
1. Check if your model names match the configured patterns
2. Verify the pricing in `MODEL_PRICING` matches current rates

### Performance issues?

For large usage histories, consider:
1. Increasing the refresh interval (e.g., `claude-usage.1m.py`)
2. Cleaning old `.jsonl` files from `~/.claude/projects/`

## Development

### Project Structure

```
claude-xbar-plugin/
├── README.md
├── LICENSE
├── claude-usage.10s.py    # Main plugin script
├── install.sh             # Installation script
├── assets/                # Screenshots and images
└── examples/             # Example configurations
```

### Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Testing

Test the plugin locally:
```bash
python3 claude-usage.10s.py
```

## License

MIT License - see [LICENSE](LICENSE) file for details

## Acknowledgments

- Built for [xbar](https://xbarapp.com/) (formerly BitBar)
- Inspired by the Claude AI community
- Icons from Apple's SF Symbols

## Support

- 🐛 [Report bugs](https://github.com/xixifast/claude-xbar-plugin/issues)
- 💡 [Request features](https://github.com/xixifast/claude-xbar-plugin/issues)

---

Made with ❤️ for Claude users everywhere