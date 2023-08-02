import csv
import re

from functools import wraps
from time import time, sleep
from typing import List, Dict, Tuple

import requests
from bs4 import BeautifulSoup


def timer(func):
    """
    The timer function is a decorator that times the runtime of
    any function.
    It takes in a function as an argument and returns the result
    of that function,
    along with printing out how long it took to run.

    :param func: Pass the function that we want to time
    :return: The result of the function it is passed
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time() - start_time
        if args:
            print(f"Parsing {args[0]} runtime: {end_time:.6f} seconds.")
        else:
            print(f"Function {func.__name__} runtime: {end_time:.6f} seconds.")
        return result
    return wrapper


@timer
def parse_url(url: str) -> Tuple[List[Dict], int]:
    """
    The parse_url function takes a URL as an argument and returns a tuple of
    two elements:
        1. A list of dictionaries, each dictionary containing the following keys:
            - name (str)
            - link (str)
            - new_price (int or NoneType)
            - old_price (int or NoneType)  # if there is no discount, then this
            value will be equal to new_price. If there is no old price specified in
            the HTML code, then this value will be set to None.  # NOQA E501

    :param url: str: Pass the url of the page to be parsed
    :return: A tuple with two elements
    """
    count_goods = 0
    data_list = []
    response = requests.get(url)

    if response.status_code != 200:
        return response.status_code, count_goods

    try:
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception as err:
        print(f"Error creating BeautifulSoup object: {err}")
        return data_list, count_goods

    # Find all notebook tiles
    notebook_tiles = soup.find_all("li", class_="catalog-grid__cell")

    for notebook_tile in notebook_tiles:

        # Extract link
        try:
            link = notebook_tile.find(
                "a", class_="goods-tile__heading")["href"]
        except Exception as err:
            link = None
            print(f"Error link: {err} with\n\tURL: {url}\
                    \n\tGoods: {count_goods}\n")

        # Extract notebook name
        name = notebook_tile.find(
            "span", class_="goods-tile__title").text.strip()
        try:
            name_split = name.split("(")
            if len(name_split) == 1:
                name = " ".join(name_split[0].split())
            else:
                name = " ".join(name_split[0].split())
                characteristics = "(" + " ".join(name_split[1].split())
        except IndexError:
            name_split = name.split("/")
            if len(name_split) == 1:
                name = " ".join(name_split[0].split())
            name = " ".join(name_split[0].split())
            characteristics = " ".join(name_split[1].split())
        except Exception as err:
            characteristics = None
            print(f"Error name_split: {err} with\n\t {name}\n\tLink: {link}\n")

        # Extract prices
        try:
            old_price = notebook_tile.find(
                "div", class_="goods-tile__price--old")
            old_price = re.sub(r"\D", "", old_price.text.strip())
        except Exception as err:
            old_price = None
            print(f"Error old_price: {err} with\n\t {name}\n\tLink: {link}\n")

        try:
            new_price = notebook_tile.find("div", class_="goods-tile__price")
            new_price = re.sub(r"\D", "", new_price.find(
                "span", class_="goods-tile__price-value").text.strip())
        except Exception as err:
            new_price = None
            print(f"Error new_price: {err} with\n\t {name}\n\tLink: {link}\n")

        # Extract number of reviews
        try:
            num_reviews = re.sub(r"\D", "", notebook_tile.find(
                "span", class_="goods-tile__reviews-link").text.strip())
        except Exception:
            num_reviews = None

        # Extract availability status
        try:
            availability_status = notebook_tile.find(
                "div", class_="goods-tile__availability").text.strip()
        except Exception as err:
            print(f"Error availability_status: {err} with\
                    \n\t {name}\n\tLink: {link}\n")
        if availability_status != "Готовий до відправлення":
            continue

        count_goods += 1

        data = {
            "name": name,
            "link": link,
            "new_price": new_price,
            "old_price": old_price,
            "reviews": num_reviews,
            "characteristics": characteristics,
        }

        data_list.append(data)

    return data_list, count_goods


def append_data_to_csv(file_path, data_list):
    """
    The append_data_to_csv function takes in a file path
    and a list of dictionaries.
    It opens the file at the given path, and writes each
    dictionary to that file as a row.
    If there is no header, it will write one.

    :param file_path: Specify the path to the file where
    we want to write our data
    :param data_list: Pass the list of dictionaries to
    be written in the csv file
    :return: None
    """
    with open(file_path, mode="a", encoding="utf-8", newline="") as f:
        fieldnames = [
            "name", "link", "new_price",
            "old_price", "reviews", "characteristics"
            ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        # Check if the file is empty, if yes, write the header
        if f.tell() == 0:
            writer.writeheader()

        writer.writerows(data_list)


def save_to_csv(filename, data):
    """
    The save_to_csv function takes two arguments:
        filename - the name of the file to be saved as a .csv file.
        data - a list of dictionaries containing information about
        each product.

    :param filename: Specify the name of the file to be saved
    :param data: Pass the data to be written to the csv file
    :return: A csv file with the data from the parse function
    """
    with open(filename, mode="w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "name", "link", "new_price",
            "old_price", "reviews", "characteristics"
            ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()


def worker(
        url: str, filename: str, count_p: int, break_time: int, strat_page=2):
    """
    The worker function takes in a url, filename, count_p
    (number of pages to scrape),
    break_time (the time between each page request) and strat_page
    (the starting page).
    It then scrapes the first url for data and saves it to a csv file.
    It then loops through
    each subsequent page up until the number of pages specified by count_p.
    If there is an error
    with any of these requests it will be logged in errors_link.txt.

    :param url: str: Pass the url to the function
    :param filename: str: Save the data to a file
    :param count_p: int: Specify the number of pages to be scraped
    :param break_time: int: Set the time interval between requests
    :param strat_page: Start parsing from a specific page
    :return: The number of pages and goods
    """
    errors_link = []
    count_pages = 0
    count_goods = 0
    data, count_g = parse_url(url)

    if not isinstance(data, list):
        errors_link.append(url)
        print(f"Error with connection to url: {url}\n\tStatus code: {data}")
        return count_pages, count_goods
    count_pages += 1
    count_goods += count_g
    save_to_csv(filename, data)

    print(
        f"Successfully scraped:\n\tPages: {count_pages}, Goods: {count_goods}")

    for i in range(strat_page, count_p + 1):
        new_page_link = f"{url}page={i}/"
        print(f">>> Parse url: {new_page_link}")
        sleep(break_time)
        try:
            data, count_g = parse_url(new_page_link)

            if not isinstance(data, list):
                errors_link.append(new_page_link)
                print(
                    f"Error with connection to url: {url}\
                        \n\tStatus code: {data}")
            count_pages += 1
            count_goods += count_g

            print(
                f"Successfully scraped:\
                    \n\tPages: {count_pages}, Goods: {count_goods}")

            append_data_to_csv(filename, data)
        except Exception as err:
            print(f"Error: {err}")
            break

    if errors_link:
        with open("errors_link.txt", "w", encoding="utf-8") as file:
            file.write(errors_link)

    return count_pages, count_goods


@timer
def main():
    """
    The main function is the entry point of the program.
    It calls worker function with arguments:
        URL - url to parse;
        FILENAME - name of file for save data;
        COUTN_PAGES - count pages to parse;
        BREAK_BETWEEN_REQUESTS - break between requests in seconds.

    :return: None
    """
    URL = "https://rozetka.com.ua/ua/notebooks/c80004/"
    COUTN_PAGES = 67
    BREAK_BETWEEN_REQUESTS = 5
    FILENAME = "data_with_rozetka.csv"

    if "page=" in URL:
        strat_page = int(URL.split("page=")[1][:-2])
        count_p, count_goods = worker(
            URL, FILENAME, COUTN_PAGES,
            BREAK_BETWEEN_REQUESTS, strat_page=strat_page
            )
    else:
        count_p, count_goods = worker(
            URL, FILENAME, COUTN_PAGES, BREAK_BETWEEN_REQUESTS
            )
    print(f"COUNT PAGES: {count_p}\nCOUNT GOODS: {count_goods}")


if __name__ == "__main__":
    main()
