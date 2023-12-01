# jrank: 日本語大規模言語モデルの評価ランキング
[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/yuzu-ai/japanese-llm-ranking/blob/main/readme.md)
[![jp](https://img.shields.io/badge/lang-jp-yellow.svg)](https://github.com/yuzu-ai/japanese-llm-ranking/blob/main/readme_jp.md)

| [**Ranking**](https://yuzuai.jp/benchmark) |
[**Blog**](https://yuzuai.jp/blog/rakuda) |
[**Discord**](https://discord.com/invite/bHB9e2rq2r) |


LMSYS' [LLM Judge](https://github.com/lm-sys/FastChat/tree/main/fastchat/llm_judge)を採用した、日本語大規模言語モデルのベンチマーク(通称: Rakuda)である[Rakuda leaderboard](https://yuzuai.jp/benchmark)を管理するレポジトリです。

## 利用方法

最初に下記の操作で Python ライブラリをインストールしてください。

```bash
$ pip install -r requirements.txt
$ cd jrank
```

RakudaはLLM Judgeと同様に同じAPIを使用しています。始めに、モデル同士を比較させたい質問リストを用意します。質問は マルチターンでも可能です。Rakudaにおいて、defaultで使用している質問リストは`jrank/data/rakuda_v2/questions.jsonl` ([HF](https://huggingface.co/datasets/yuzuai/rakuda-questions))から確認することができます。
これらの質問に対して、`jrank/gen_model_answer.py`を実行することでモデルによる返答を生成します：

```bash
python3 gen_model_answer.py --bench_name rakuda_v2 --model-path line-corporation/japanese-large-lm-1.7b-instruction-sft --model-id line-1.7b --conv_template ./templates/line.json
```

APIモデルを使用する場合には、代わりに、`gen_api_answer.py`を使用してモデルの返答を生成します。

次に、`gen_judgement.py`を実行することでモデルによって生成された返答の判定を行います:

```bash
python gen_judgment.py --bench-name rakuda_v2 --model-list chatntq-7b-jpntuned claude-2 gpt-3.5-turbo-0301-20230614 gpt-4-20230713 elyza-7b-fast-instruct elyza-7b-instruct jslm7b-instruct-alpha line-3.6b-sft rinna-3.6b-ppo rinna-3.6b-sft rwkv-world-jp-v1 stablebeluga2 weblab-10b-instruction-sft super-trin --parallel 2 --mode pairwise-n --judge-model claude-2 --n 2000
```
Mode optionがどのような判定を行うかを決定します。Rakudaではデフォルトで、`n`個の判定に到達するまでに生成された返答をペアごとに比較する。`pairwise-n`を採用しています。

最後に、下された判定に対してBradley-Terryモデルをフィッティングすることで、評価ランキングを作成します:

```bash
python make_ranking.py --bench-name rakuda_v2 --judge-model claude-2 --mode pairwise --compute mle --make-charts --bootstrap-n 500 --plot-skip-list rinna-3.6b-sft super-trin elyza-7b-instruct
```

### LLM-JP

> [!CAUTION]
> 以下の llm-jp-13b-full-all と llm-jp-13b-lora-all の評価結果は既に jrank/data/rakuda_v2/model_judgment/gpt-4_pair.jsonl に記載してあります。
> win rate を計算したい場合、readme 下部にその方法を記載しています。

最初に `jrank/gen_model_answer.py` を使用して LLM の出力を生成してください。

```bash
$ python3 gen_model_answer.py \
  --bench_name rakuda_v2 \
  --model-path llm-jp/llm-jp-13b-instruct-full-jaster-dolly-oasst-v1.0 \
  --model-id llm-jp-13b-full-all \
  --conv_template ./templates/llm-jp.json \
  --temperature 0.7 \
  --top_p 0.95
```

LoRA モデルの出力を得る場合、ローカルに adapter をダウンロードし、フォルダ名を変更する必要があります。

```bash
$ git lfs install
$ git clone https://huggingface.co/llm-jp/llm-jp-13b-instruct-lora-jaster-dolly-oasst-v1.0
# フォルダ名に "peft" を含む必要があります
$ mv -f llm-jp-13b-instruct-lora-jaster-dolly-oasst-v1.0 llm-jp-13b-instruct-lora-jaster-dolly-oasst-v1.0-peft
$ python3 gen_model_answer.py \
  --bench_name rakuda_v2 \
  --model-path /path/to/llm-jp-13b-instruct-lora-jaster-dolly-oasst-v1.0-peft \
  --model-id llm-jp-13b-peft-all \
  --conv_template ./templates/llm-jp.json \
  --temperature 0.7 \
  --top_p 0.95
```

次に、`jrank/gen_judgment.py` を利用して評価を作成してください。

```bash
$ python3 gen_judgment.py \
  --bench_name rakuda_v2 \
  --model-list llm-jp-13b-full-all llm-jp-13b-lora-all \
  --parallel 1 \
  --mode pairwise-n \
  --judge-model gpt-4 \
  --n 2000  # これは最大で2,000リクエストまで行うことを意味しています。今回の場合は2*40で80リクエストになります。
```

最後に `jrank/gen_winrate.py` で win-rate を求めます。

```bash
$ python3 gen_winrate.py \
  --model_a llm-jp-13b-full-all \
  --model_b llm-jp-13b-lora-all
```
