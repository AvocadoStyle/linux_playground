import time
import numpy as np


def benchmark(name, func):
    start = time.perf_counter()
    func()
    end = time.perf_counter()
    return end - start


def print_table(results):
    col1 = 45
    col2 = 15
    print("\n" + "=" * (col1 + col2 + 5))
    print(f"{'Operation':<{col1}} {'Time (s)':>{col2}}")
    print("=" * (col1 + col2 + 5))
    for name, t in results:
        print(f"{name:<{col1}} {t:>{col2}.6f}")
    print("=" * (col1 + col2 + 5))


def main():
    N = 5_000_000
    py_list = list(range(N))
    np_array = np.arange(N)

    results = []

    # =====================================================
    # ITERATION
    # =====================================================
    results.append(("list for-loop sum",
                    benchmark("",
                              lambda: sum(x for x in py_list))))

    results.append(("numpy for-loop sum",
                    benchmark("",
                              lambda: sum(x for x in np_array))))

    results.append(("numpy vectorized sum",
                    benchmark("",
                              lambda: np_array.sum())))

    # =====================================================
    # ARITHMETIC
    # =====================================================
    results.append(("list multiply",
                    benchmark("",
                              lambda: [x * 2 for x in py_list])))

    results.append(("numpy multiply",
                    benchmark("",
                              lambda: np_array * 2)))

    results.append(("numpy chained ops",
                    benchmark("",
                              lambda: (np_array * 2 + 5) / 3)))

    # =====================================================
    # FILTERING / CONDITIONS
    # =====================================================
    results.append(("list if filter",
                    benchmark("",
                              lambda: [x for x in py_list if x % 3 == 0])))

    results.append(("numpy boolean mask",
                    benchmark("",
                              lambda: np_array[np_array % 3 == 0])))

    # =====================================================
    # MATH FUNCTIONS
    # =====================================================
    results.append(("list sqrt",
                    benchmark("",
                              lambda: [x ** 0.5 for x in py_list])))

    results.append(("numpy sqrt",
                    benchmark("",
                              lambda: np.sqrt(np_array))))

    results.append(("numpy sin",
                    benchmark("",
                              lambda: np.sin(np_array))))

    # =====================================================
    # AGGREGATIONS
    # =====================================================
    results.append(("list max",
                    benchmark("",
                              lambda: max(py_list))))

    results.append(("numpy max",
                    benchmark("",
                              lambda: np_array.max())))

    results.append(("numpy mean",
                    benchmark("",
                              lambda: np_array.mean())))

    # =====================================================
    # SLICING & MEMORY
    # =====================================================
    results.append(("list slicing copy",
                    benchmark("",
                              lambda: py_list[1::2])))

    results.append(("numpy slicing view",
                    benchmark("",
                              lambda: np_array[1::2])))

    # =====================================================
    # SEARCH
    # =====================================================
    results.append(("list membership check",
                    benchmark("",
                              lambda: N - 1 in py_list)))

    results.append(("numpy argmax",
                    benchmark("",
                              lambda: np_array.argmax())))

    # =====================================================
    # SHAPE OPERATIONS
    # =====================================================
    matrix = np_array.reshape(-1, 10)
    results.append(("numpy reshape",
                    benchmark("",
                              lambda: np_array.reshape(-1, 10))))

    results.append(("numpy transpose",
                    benchmark("",
                              lambda: matrix.T)))

    # =====================================================
    # APPEND BEHAVIOR
    # =====================================================
    results.append(("list append",
                    benchmark("",
                              lambda: [py_list.append(i) for i in range(1000)])))

    results.append(("numpy append (copy)",
                    benchmark("",
                              lambda: np.append(np_array, range(1000)))))

    print_table(results)


if __name__ == "__main__":
    main()
