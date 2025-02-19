# Ultimate Prompt Generator (UPG) 🤖

A powerful CLI tool for generating, managing, and reusing prompts for different LLM providers. 
Currently supports OpenAI and Anthropic models with smart defaults.

[Join Russian Speaking Telegram Channel](https://t.me/pavlin_share) | [Watch Russian Video Tutorial](https://youtu.be/R1evjTkOB_4)

## 🌟 Features

- 🔄 **Multi-Provider Support**: 
  - OpenAI (default: gpt-4o)
  - Anthropic (default: claude-3-sonnet-20240229)
- 📝 **Smart Prompt Generation**: 
  - Generate high-quality prompts for various tasks
  - Create prompts with or without variables
  - Automatic variable detection and validation
- 💾 **Prompt Management**:
  - Save and reuse generated prompts
  - Tag and categorize prompts
  - Search through saved prompts
- 🔑 **Secure Configuration**: Safe storage of API keys and preferences

## 🚀 Quick Start

```bash
# Install with pip
pip install upg-cli

# Or install with Poetry
poetry add upg-cli
```

### Initial Configuration

```bash
# Configure your preferred LLM provider
upg config --provider openai --api-key YOUR_API_KEY
```

### Basic Usage

```bash
# Generate a simple prompt without variables
upg generate "Write a story about a space traveler"

# Generate a prompt with variables
upg generate "Create a Python function to calculate fibonacci numbers" \
    -v FUNCTION_NAME \
    -v ARGS \
    --save --name "python-fibonacci" \
    --tag python --tag math

# Use a saved prompt
upg answer python-fibonacci \
    -v FUNCTION_NAME "fibonacci" \
    -v ARGS "n: int"
```

## 📋 Detailed Usage Guide

### Prompt Generation

You can generate prompts both with and without variables:

```bash
# Simple prompt without variables
upg generate "Write a poem about autumn"

# Prompt with variables
upg generate "Write a {GENRE} story about {TOPIC}" \
    -v GENRE \
    -v TOPIC

# Save generated prompt
upg generate "Your task description" [options]

Options:
  --provider TEXT           LLM provider to use (openai/anthropic)
  -v, --variable TEXT      Variable names for the prompt (optional)
  -o, --output FILENAME    Save prompt to file
  -s, --save              Save prompt for later use
  --name TEXT             Name for saved prompt
  -d, --description TEXT  Description for saved prompt
  -t, --tag TEXT         Tags for categorizing the prompt
```

### Using Prompts

For prompts without variables, you can use them directly:
```bash
# Using a simple prompt without variables
upg answer simple-story

# Using a prompt with variables
upg answer story-template \
    -v GENRE "mystery" \
    -v TOPIC "lost artifact"
```

### More Examples

#### Simple Prompts (No Variables)
```bash
# Generate a blog post outline
upg generate "Create an outline for a blog post about machine learning basics" \
    --save --name "blog-outline" \
    --tag content --tag blog

# Generate coding guidelines
upg generate "Write Python code style guidelines for a team" \
    --save --name "python-guidelines" \
    --tag python --tag guidelines

# Use saved prompts
upg answer blog-outline
upg answer python-guidelines
```

#### Prompts with Variables
```bash
# Generate a template for API documentation
upg generate "Write documentation for a REST API endpoint" \
    -v ENDPOINT \
    -v METHOD \
    --save --name "api-docs" \
    --tag api

# Use the template
upg answer api-docs \
    -v ENDPOINT "/users" \
    -v METHOD "POST"
```

## 🔧 Configuration

UPG provides flexible configuration options through the `config` command group:

### Provider Configuration

```bash
# Configure a provider
upg config provider --provider openai --api-key YOUR_API_KEY --model gpt-4o

# Or configure interactively
upg config provider
```

### Default Provider

```bash
# Set default provider
upg config set-default openai

# Switch to using Anthropic by default
upg config set-default anthropic
```

### View Configuration

```bash
# Show current configuration
upg config show
```

Example output:
```
Current Configuration:
----------------------------------------
Default Provider: openai

Configured Providers:

OPENAI:
  Model: gpt-4o
  Temperature: 1.0
  API Key: sk-abcd...wxyz

ANTHROPIC:
  Model: claude-3-sonnet-20240229
  Temperature: 1.0
  API Key: sk-ant...4321
```

### Configuration Storage

The tool stores configuration in `~/.config/upg/config.json`:
- API keys for LLM providers
- Default provider settings
- Provider-specific configurations
- Saved prompts and their metadata

## 🗃️ Prompt Storage

Prompts are stored with:
- Unique name
- Description
- Variables list (if any)
- Tags for categorization
- Creation and update timestamps

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

⭐ Found this useful? Star the repo and share it!

[Join Telegram Community](https://t.me/pavlin_share)