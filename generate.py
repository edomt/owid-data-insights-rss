import PyRSS2Gen
from bs4 import BeautifulSoup

import requests
import json
import datetime

URL = "https://ourworldindata.org/data-insights"
OUTPUT_FILE = "data_insights.xml"


def get_soup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup


def parse_json(soup):
    script = soup.find(
        "script",
        string=lambda x: "window._OWID_DATA_INSIGHTS_INDEX_PAGE_DATA" in x
        if x
        else False,
    )

    # Extract the json string, from the first { to the last }
    json_str = script.text.split("{", 1)[1].rsplit("}", 1)[0]

    # Strip the string of any leading/trailing whitespace
    json_str = json_str.strip()

    # Add back the first { and last }
    json_str = "{" + json_str + "}"

    # Load the JSON string into a Python dictionary
    return json.loads(json_str)


def generate_rss_feed(data):
    # Create an RSS feed
    rss = PyRSS2Gen.RSS2(
        title="Our World in Data - Data Insights",
        link="https://ourworldindata.org/data-insights",
        description="Data Insights from Our World in Data",
    )

    # Add items to the RSS feed
    for item in data["dataInsights"]:
        for part in item["content"]["body"]:
            if part["type"] == "text":
                excerpt = part["value"][0]["text"]
                break

        rss.items.append(
            PyRSS2Gen.RSSItem(
                title=item["content"]["title"],
                link=f'https://ourworldindata.org/data-insight/{item["slug"]}',
                description=excerpt,
                guid=PyRSS2Gen.Guid(
                    f'https://ourworldindata.org/data-insight/{item["slug"]}'
                ),
                pubDate=datetime.datetime.strptime(
                    item["publishedAt"], "%Y-%m-%dT%H:%M:%S.%fZ"
                ),
            )
        )

    # Set lastBuildDate to the max pubDate
    rss.lastBuildDate = max([item.pubDate for item in rss.items])

    # Generate the RSS feed
    return rss.to_xml()


def main():
    # Get the HTML page
    soup = get_soup(URL)

    # Parse the JSON data
    data = parse_json(soup)

    # Generate the RSS feed
    rss_feed = generate_rss_feed(data)

    # Write the RSS feed to a file
    with open(OUTPUT_FILE, "w") as f:
        f.write(rss_feed)


if __name__ == "__main__":
    main()
