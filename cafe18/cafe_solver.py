import time

from selenium import webdriver
from selenium.common.exceptions import JavascriptException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from cafe18.cafe5 import cafeize


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


def solve_problem(driver, current_problem, solution):
    element = driver.find_element(By.ID, f"problem-{current_problem}")
    input_element = element.find_element(By.TAG_NAME, "input")
    submit_element = element.find_element(By.TAG_NAME, "button")

    input_element.send_keys(solution)
    submit_element.click()


def check_results(driver, correct_set, incorrect_set):
    notifications_container = driver.find_element(By.ID, "notifications")
    notifications = notifications_container.find_elements(By.TAG_NAME, "div")

    # What is F4 + F6?: F874 is correct
    for notification in notifications:
        notification_text: str = notification.text
        notification_text = notification_text.lstrip("What is ")
        problem = notification_text.split("?")[0]
        solution = notification_text.split(":")[1].lstrip().split(" ")[0]
        correct = notification_text.split(" ")[-1] == "correct"

        record = f'("{problem}", "{solution}"),'
        if correct:
            before_len = len(correct_set)
            correct_set.add(record)
            if before_len < len(correct_set):
                print(f"Adding record {record} as correct")
                with open("correct_set.txt", "a") as f:
                    f.write(f"{record}\n")
        else:
            before_len = len(incorrect_set)
            incorrect_set.add(record)
            if before_len < len(correct_set):
                print(f"Adding record {record} as incorrect")
                with open("incorrect_set.txt", "a") as f:
                    f.write(f"{record}\n")


def solve():
    driver = webdriver.Chrome()
    driver.get("https://dan-simon.github.io/misc/reduction/ic/index.html")
    driver.execute_script("startStuff();")

    correct_set, incorrect_set = set(), set()

    current_problem = 1
    while True:
        problem_str = find_problem(driver, current_problem)

        if problem_str:
            solution = cafeize(problem_str)
            solve_problem(driver, current_problem, solution)
            check_results(driver, correct_set, incorrect_set)
            current_problem += 1
        time.sleep(1)


if __name__ == "__main__":
    solve()
