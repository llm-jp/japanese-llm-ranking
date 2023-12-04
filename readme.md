# jrank: Ranking Japanese LLMs
[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/yuzu-ai/japanese-llm-ranking/blob/main/readme.md)
[![jp](https://img.shields.io/badge/lang-jp-yellow.svg)](https://github.com/yuzu-ai/japanese-llm-ranking/blob/main/readme_jp.md)

| [**Ranking**](https://yuzuai.jp/benchmark) |
[**Blog**](https://yuzuai.jp/blog/rakuda) |
[**Discord**](https://discord.com/invite/bHB9e2rq2r) |


This repository supports YuzuAI's [Rakuda leaderboard](https://yuzuai.jp/benchmark) of Japanese LLMs, which is a Japanese-focused version of LMSYS' [LLM Judge](https://github.com/lm-sys/FastChat/tree/main/fastchat/llm_judge).

## Usage

At first, need install python libraries.

```bash
$ pip install -r requirements.txt
$ cd jrank
```

Rakuda follows the same API as LLM Judge. First start with a question list you wish to compare the models on. These questions can be multi-turn. The default Rakuda question list is `jrank/data/rakuda_v2/questions.jsonl` ([HF](https://huggingface.co/datasets/yuzuai/rakuda-questions)).

Then generate model answers to these questions using `jrank/gen_model_answer.py`:

```bash
python3 gen_model_answer.py --bench_name rakuda_v2 --model-path line-corporation/japanese-large-lm-1.7b-instruction-sft --model-id line-1.7b --conv_template ./templates/line.json
```

For API models, use `gen_api_answer.py` instead.

After generating model answers, generate judgements of these answers using `gen_judgement.py`.

```bash
python gen_judgment.py --bench-name rakuda_v2 --model-list chatntq-7b-jpntuned claude-2 gpt-3.5-turbo-0301-20230614 gpt-4-20230713 elyza-7b-fast-instruct elyza-7b-instruct jslm7b-instruct-alpha line-3.6b-sft rinna-3.6b-ppo rinna-3.6b-sft rwkv-world-jp-v1 stablebeluga2 weblab-10b-instruction-sft super-trin --parallel 2 --mode pairwise-n --judge-model claude-2 --n 2000
```

The mode option determines what kind of judgements are performed. The default for rakuda is `pairwise-n`, in which model answers are compared pairwise until `n` judgements have been reached.

Finally, fit a Bradley-Terry model to these judgements to create a model ranking.
```bash
python make_ranking.py --bench-name rakuda_v2 --judge-model claude-2 --mode pairwise --compute mle --make-charts --bootstrap-n 500 --plot-skip-list rinna-3.6b-sft super-trin elyza-7b-instruct
```

### LLM-JP

> [!CAUTION]
> The evaluation results of the following llm-jp-13b-full-all and llm-jp-13b-lora-all have already benn described in jrank/data/rakuda_v2/model_judgment/gpt-4_pair.jsonl.
> If you want to calcuate win rate, it is described at the bottom of readme.

First, generate model answers using `jrank/gen_model_answer.py`:

```bash
$ python3 gen_model_answer.py \
  --bench_name rakuda_v2 \
  --model-path llm-jp/llm-jp-13b-instruct-full-jaster-dolly-oasst-v1.0 \
  --model-id llm-jp-13b-full-all \
  --conv_template ./templates/llm-jp.json \
  --temperature 0.7 \
  --top_p 0.95
```

If you would like to use a LoRA model, you need to download the adapter and rename folder:

```bash
# https://huggingface.co/llm-jp/llm-jp-13b-instruct-lora-jaster-dolly-oasst-v1.0
$ git lfs install
$ git clone https://huggingface.co/llm-jp/llm-jp-13b-instruct-lora-jaster-dolly-oasst-v1.0
# Include "peft" in the folder name.
$ mv -f llm-jp-13b-instruct-lora-jaster-dolly-oasst-v1.0 llm-jp-13b-instruct-lora-jaster-dolly-oasst-v1.0-peft
$ python3 gen_model_answer.py \
  --bench_name rakuda_v2 \
  --model-path /path/to/llm-jp-13b-instruct-lora-jaster-dolly-oasst-v1.0-peft \
  --model-id llm-jp-13b-lora-all \
  --conv_template ./templates/llm-jp.json \
  --temperature 0.7 \
  --top_p 0.95
```

Second, generate judgments using `jrank/gen_judgment.py`.

```bash
# Pairwise evaluation for llm-jp-13b-full-all and llm-jp-13b-lora-all.
$ python3 gen_judgment.py \
  --bench_name rakuda_v2 \
  --model-list llm-jp-13b-full-all llm-jp-13b-lora-all \
  --parallel 1 \
  --mode pairwise-n \
  --judge-model gpt-4 \
  --n 2000  # This would mean a maximum of 2,000 requests. For a pairwised evaluation of 2 models, that would be 80 cases.
```

Finally, generate win rate using `jrank/gen_winrate.py`.

```bash
$ python3 gen_winrate.py \
  --file_path data/rakuda_v2/model_judgment/gpt-4_pair.jsonl \
  --model_a llm-jp-13b-full-all \
  --model_b llm-jp-13b-lora-all
```
