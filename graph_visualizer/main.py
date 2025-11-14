import json
import sys

# === Этап 1: загрузка конфигурации ===
def load_config(path="config.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except FileNotFoundError:
        print(f"Ошибка: файл '{path}' не найден.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Ошибка: '{path}' — некорректный JSON.")
        sys.exit(1)

    required = ["package_name", "repo_url", "test_mode", "max_depth"]
    for key in required:
        if key not in cfg:
            print(f"В конфиге отсутствует обязательный параметр: '{key}'")
            sys.exit(1)

    if not isinstance(cfg["test_mode"], bool):
        print("'test_mode' должен быть true/false")
        sys.exit(1)
    if not isinstance(cfg["max_depth"], int) or cfg["max_depth"] < 0:
        print("'max_depth' должен быть целым ≥ 0")
        sys.exit(1)

    return cfg

# === Этап 2: получение прямых зависимостей ===
def get_direct_deps(pkg, config):
    if config["test_mode"]:
        try:
            with open("test_repo.json", "r", encoding="utf-8") as f:
                repo = json.load(f)
        except Exception as e:
            print(f"Не удалось прочитать test_repo.json: {e}")
            sys.exit(1)
        return repo.get(pkg, [])
    else:
        # Заглушка для pip (реальные данные нельзя — по ТЗ)
        fallback = {
            "requests": ["urllib3", "chardet"],
            "urllib3": ["six"],
            "chardet": [],
            "six": []
        }
        return fallback.get(pkg, [])

# === Этап 3: построение графа (DFS без рекурсии) ===
def build_graph(start, config):
    visited = set()
    stack = [(start, 0)]  # (пакет, глубина)
    graph = {}

    while stack:
        node, depth = stack.pop()
        if node in visited or depth > config["max_depth"]:
            continue
        visited.add(node)
        deps = get_direct_deps(node, config)
        graph[node] = deps
        # обратный порядок — чтобы слева-направо было как при рекурсии
        for dep in reversed(deps):
            if dep not in visited:
                stack.append((dep, depth + 1))
    return graph

# === ЗАПУСК ===
if __name__ == "__main__":
    config = load_config()

    print("Этап 1: параметры конфигурации:")
    for k, v in config.items():
        print(f"  {k}: {v}")

    # === Этап 2: прямые зависимости ===
    direct = get_direct_deps(config["package_name"], config)
    print(f"\nЭтап 2: прямые зависимости пакета '{config['package_name']}':")
    if direct:
        for d in direct:
            print(f"  - {d}")
    else:
        print("  (нет)")

    # === Этап 3: полный граф ===
    graph = build_graph(config["package_name"], config)
    print(f"\nЭтап 3: граф зависимостей (max_depth={config['max_depth']}):")
    for pkg, deps in graph.items():
        print(f"  {pkg} → {deps}")

