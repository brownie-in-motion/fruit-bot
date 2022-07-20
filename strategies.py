import random

def boxes(grid):
    prefix_sums = [
        [0] * (len(grid[0]) + 1)
        for _ in range(len(grid) + 1)
    ]

    # compute rectangle sums
    for i in range(1, len(grid) + 1):
        for j in range(1, len(grid[0]) + 1):
            prefix_sums[i][j] = (
                grid[i - 1][j - 1] +
                prefix_sums[i - 1][j] +
                prefix_sums[i][j - 1] -
                prefix_sums[i - 1][j - 1]
            )

    # for all rectangles, find ones that sum to 10
    for start_i in range(1, len(grid) + 1):
        for start_j in range(1, len(grid[0]) + 1):
            for end_i in range(start_i, len(grid) + 1):
                for end_j in range(start_j, len(grid[0]) + 1):
                    box_sum = (
                        prefix_sums[end_i][end_j] -
                        prefix_sums[start_i - 1][end_j] -
                        prefix_sums[end_i][start_j - 1] +
                        prefix_sums[start_i - 1][start_j - 1]
                    )

                    if box_sum == 10:
                        yield (
                            (start_i - 1, start_j - 1),
                            (end_i - 1, end_j - 1)
                        )


def first(grid):
    copy = [row[:] for row in grid]
    solutions = list(boxes(copy))
    output = []
    while solutions:
        (start_i, start_j), (end_i, end_j) = solutions[0]
        for i in range(start_i, end_i + 1):
            for j in range(start_j, end_j + 1):
                copy[i][j] = 0
        output.append(solutions[0])
        solutions = list(boxes(copy))
    return output


def best_random(grid, attempts):
    best = []
    for _ in range(attempts):
        copy = [row[:] for row in grid]
        solutions = list(boxes(copy))
        output = []
        while solutions:
            solution = random.choice(solutions)
            (start_i, start_j), (end_i, end_j) = solution
            for i in range(start_i, end_i + 1):
                for j in range(start_j, end_j + 1):
                    copy[i][j] = 0
            output.append(solution)
            solutions = list(boxes(copy))
        best = max(best, output, key=len)
    return best
