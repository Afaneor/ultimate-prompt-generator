# LLM Prompt Generator 🤖

[Join Russian Speaking Telegram Channel](https://t.me/pavlin_share) | [Watch Russian Video Tutorial](coming_soon)

A powerful and flexible tool for generating and managing prompts for different LLM providers. Currently supports OpenAI and Anthropic models with smart defaults (GPT-4o and Claude 3 Sonnet).

Totally inspired by [claude prompt generator](https://colab.research.google.com/drive/1SoAajN8CBYTl79VyTwxtxncfCWlHlyy9)
---

## 🌟 Features

- 🔄 **Multi-Provider Support**: Works with both OpenAI and Anthropic models
- 🎯 **Smart Defaults**: 
  - OpenAI: `gpt-4o`
  - Anthropic: `claude-3-sonnet-20240229`
- 🔑 **API Key Management**: Secure storage and reuse of API keys
- 💾 **Configuration Persistence**: Save and reuse your preferred settings

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/llm-prompt-generator.git
cd llm-prompt-generator

# Install dependencies
poetry install || pip install -r requirements.txt

# Run the tool
python main.py
```

## 📋 Requirements

Required packages:
- Python 3.8+
- llama-index
- openai
- anthropic

## 🎮 Usage

run `python main.py` and follow the prompts to generate your LLM prompts.
```bash
python main.py
```

1. **Select LLM Provider**:
```bash
Select LLM provider: openai  # or anthropic
```

2. **Configure API Key**:
```bash
Enter API key: sk-...
```

3. **Choose Model** (defaults available):
```bash
Enter model name (press Enter for default 'gpt-4o'): 
```

4. **Generate Prompts**:
```bash
Enter your task: Write a python function
Do you want to input text? (y/n): n
Do you want to specify variables? (y/n): y
```

## 🗺️ Roadmap

- [ ] CLI interface using Click
- [ ] Compiled versions for easy distribution
- [ ] More LLM providers


⭐ Found this useful? Star the repo and share it!

[Join Telegram Community](https://t.me/pavlin_share)
