import argparse
import json
import random
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Tuple, Dict


@dataclass
class EvaluatedItem:
    prompt: str
    win_model: str
    lose_model: str
    judgment: str
    model_1: str
    model_2: str


@dataclass
class AggregatedItem:
    n_win: int
    n_lose: int
    n_draw: int
    n_error: int
    model_a_win_instance: List[str]
    model_b_win_instance: List[str]
    error_instance: List[str]
    draw_instance: List[str]


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_path", type=str, required=True, help="path to judgment jsonl file")
    parser.add_argument("--model_a", type=str, required=True, help="model name")
    parser.add_argument("--model_b", type=str, required=True, help="model name")
    return parser.parse_args()


def load_results(file_path: str, model_a: str, model_b: str) -> Dict[str, List[EvaluatedItem]]:
    result = defaultdict(list)
    with open(file_path) as i_f:
        for line in i_f:
            data = json.loads(line.strip())
            model_1_id = data["model1_id"]
            model_2_id = data["model2_id"]

            if model_1_id not in [model_a, model_b] or model_2_id not in [model_a, model_b]:
                # 関係ないモデルの結果は無視
                continue

            qid = data["question_id"]
            winner = data["winner"]
            prompt = data["prompt"]
            judgment = data["judgment"]

            win_model: str
            lose_model: str
            if winner == 1:
                win_model = model_1_id
                lose_model = model_2_id
            elif winner == 2:
                win_model = model_2_id
                lose_model = model_1_id
            else:
                win_model = "error"
                lose_model = "error"

            item = EvaluatedItem(
                prompt=prompt,
                win_model=win_model,
                lose_model=lose_model,
                judgment=judgment,
                model_1=model_1_id,
                model_2=model_2_id,
            )
            result[qid].append(item)
    return result


def aggregate_results(
    results: Dict[str, List[EvaluatedItem]], model_a: str, model_b: str
) -> AggregatedItem:
    count = {
        "n_win": 0,
        "n_lose": 0,
        "n_draw": 0,
        "n_error": 0,
    }
    instance = {
        "model_a_win_instance": [],
        "model_b_win_instance": [],
        "draw_instance": [],
        "error_instance": [],
    }

    for _, items in results.items():
        win_models = [item.win_model for item in items]
        if "error" in win_models:
            count["n_error"] += 1
            instance["error_instance"].append(items)
            continue

        model_first, model_second = win_models

        if model_first != model_second:
            count["n_draw"] += 1
            instance["draw_instance"].append(items)
        else:
            if model_first == model_a:
                count["n_win"] += 1
                instance["model_a_win_instance"].append(items)
            elif model_first == model_b:
                count["n_lose"] += 1
                instance["model_b_win_instance"].append(items)
            else:
                raise ValueError(f"Unexpected model: {model_first}")

    return AggregatedItem(
        n_win=count["n_win"],
        n_lose=count["n_lose"],
        n_draw=count["n_draw"],
        n_error=count["n_error"],
        model_a_win_instance=instance["model_a_win_instance"],
        model_b_win_instance=instance["model_b_win_instance"],
        error_instance=instance["error_instance"],
        draw_instance=instance["draw_instance"],
    )


def print_results(aggregated_results: AggregatedItem) -> None:
    def print_instance(instance: List[EvaluatedItem], need_reverse_judge: bool = False) -> None:
        print(f"Prompt: {instance[0].prompt}")
        print(f"Assistant1: {instance[0].model_1}")
        print(f"Assistant2: {instance[0].model_2}")
        print(f"Judgment: {instance[0].judgment}")
        if need_reverse_judge:
            print(f"Judgment (reverse position): {instance[1].judgment}")

    print(f"# win: {aggregated_results.n_win}")
    print(f"# lose: {aggregated_results.n_lose}")
    print(f"# draw: {aggregated_results.n_draw}")
    print(f"# error: {aggregated_results.n_error}")

    print("*"*100)
    print("Win instance")
    win_sample = random.choice(aggregated_results.model_a_win_instance)
    print_instance(win_sample)

    print("*"*100)
    print("Lose instance")
    lose_sample = random.choice(aggregated_results.model_b_win_instance)
    print_instance(lose_sample)

    print("*"*100)
    print("Draw instance")
    draw_sample = random.choice(aggregated_results.draw_instance)
    print_instance(draw_sample, need_reverse_judge=True)

    print("*"*100)
    print("Error instance")
    error_sample = random.choice(aggregated_results.error_instance)
    print_instance(error_sample, need_reverse_judge=True)


def main():
    args = get_args()
    results = load_results(args.file_path, args.model_a, args.model_b)
    aggregated_results = aggregate_results(results, args.model_a, args.model_b)

    print(f"Model {args.model_a}'s win rate")
    print_results(aggregated_results)


if __name__ == "__main__":
    main()
