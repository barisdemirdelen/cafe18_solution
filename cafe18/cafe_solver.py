import json
import time
from collections import defaultdict

from selenium import webdriver
from selenium.common.exceptions import JavascriptException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from cafe18.cafe5 import cafeize


corrects_file = "correct.json"
incorrects_file = "incorrect.json"


def find_problem(driver, current_problem):
    try:
        element = driver.find_element(By.ID, f"problem-{current_problem}")
    except NoSuchElementException as _:
        return None

    question_element = element.find_element(By.TAG_NAME, "span")
    question_text: str = question_element.text

    question_text = question_text.lstrip("What is ")
    question_text = question_text[: question_text.find("?")]
    print(f"Found problem {current_problem}: {question_text}")
    return question_text


def get_solution(problem_str, corrects, incorrects):
    solution = corrects.get(problem_str)
    if solution:
        print(f"Known solution {problem_str} : {solution}")
    else:
        solution = cafeize(problem_str)
        if solution in incorrects[problem_str]:
            print(f"Known incorrect {problem_str} : {solution}")
            solution = None
        else:
            print(f"New problem {problem_str} : {solution}")
    return solution


def solve_problem(driver, current_problem, solution):
    element = driver.find_element(By.ID, f"problem-{current_problem}")
    input_element = element.find_element(By.TAG_NAME, "input")
    submit_element = element.find_element(By.TAG_NAME, "button")

    input_element.send_keys(solution)
    submit_element.click()


def check_results(driver, problem, solution, corrects, incorrects):
    notifications_container = driver.find_element(By.ID, "notifications")
    notifications = notifications_container.find_elements(By.TAG_NAME, "div")

    # What is F4 + F6?: F874 is correct
    for notification in notifications:
        notification_text: str = notification.text
        notification_text = notification_text.lstrip("What is ")
        current_problem = notification_text.split("?")[0]
        if current_problem != problem:
            continue
        correct = notification_text.split(" ")[-1] == "correct"

        if correct and problem not in corrects:
            corrects[problem] = solution
            print(f"New correct: {problem}: {solution}")
            write_corrects(corrects)

        elif not correct and solution not in incorrects[problem]:
            incorrects[problem].add(solution)
            print(f"New incorrect: {problem}: {solution}")
            write_incorrects(incorrects)


def read_database():
    with open(corrects_file) as f:
        corrects = json.load(f)

    with open(incorrects_file) as f:
        incorrects = json.load(f)

    incorrects_out = defaultdict(set)
    for key, elem in incorrects.items():
        if len(elem) > 0:
            incorrects_out[key].update(elem)

    return corrects, incorrects_out


def write_corrects(corrects):
    with open(corrects_file, "w") as f:
        json.dump(corrects, f)


def write_incorrects(incorrects):
    incorrects_out = {}
    for key, elem in incorrects.items():
        if len(elem) > 0:
            incorrects_out[key] = list(sorted(elem))

    with open(incorrects_file, "w") as f:
        json.dump(incorrects_out, f)


def solve():
    driver = webdriver.Chrome()
    driver.get("https://dan-simon.github.io/misc/reduction/ic/index.html")
    driver.execute_script("startStuff();")

    corrects, incorrects = read_database()

    current_problem = 1
    while True:
        problem_str = find_problem(driver, current_problem)

        while problem_str:
            try:
                if solution := get_solution(problem_str, corrects, incorrects):
                    solve_problem(driver, current_problem, solution)
                    check_results(driver, problem_str, solution, corrects, incorrects)
            except Exception as e:
                print(e)
            current_problem += 1
            problem_str = find_problem(driver, current_problem)
        # driver.execute_script("giveNextProblem();")
        time.sleep(0.1)


if __name__ == "__main__":
    solve()
