# Rozetka Web Scraping Project

This project uses web harvesting to retrieve and store data from the Rozetka website. It allows you to collect information about the selected category and save it to a CSV file.

## Contents

- [How to Run the Project](#how-to-run-the-project)
- [Results](#results)
- [Conclusion](#conclusion)

## How to Run the Project

1. Clone the repository to your computer:

   ```
   git clone https://github.com/ihor-vt/Scrapy-site-Rozetka.git
   ```

2. Install the dependencies using `requirements.txt`:

   ```
   pip install -r requirements.txt
   ```

3. Open the `scraping_script.py` file and configure the following variables in main() function:

   - `URL`: The URL of the "Notebooks" category on Rozetka.
   - `COUNT_PAGES`: The number of pages to parse.
   - `BREAK_BETWEEN_REQUESTS`: The delay between requests in seconds.
   - `FILENAME`: The name of the file to save the data.

4. Run the script:

   ```
   python scraping_script.py
   ```

5. After the script completes, the results will be saved in the `data_with_rozetka.csv` file.

## Results

Upon running the script, data from the "Notebooks" category on Rozetka will be collected and saved in the `data_with_rozetka.csv` file. This file will contain information about various laptops, including their names, prices, and specifications.

## Conclusion

This project demonstrates how to use web scraping to retrieve data from the Rozetka website. You can easily adapt the code to scrape other product categories on the site. The collected data can be used for analysis, product comparison, and other purposes.

**Note**: The use of web scraping may violate website usage rules, so always adhere to the rules and policies of the website when using web scraping.
