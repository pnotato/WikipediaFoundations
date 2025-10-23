# Wikipedia Foundation Analysis

> Following the first hyperlink in the main text of an English Wikipedia article, and then repeating the process for subsequent articles, usually leads to the Philosophy article. [Getting to Philosphy - Wikipedia](https://en.wikipedia.org/wiki/Wikipedia:Getting_to_Philosophy)

Wikipedia maintains a user-reviewed, albeit incomplete list of "[Vital Articles](https://en.wikipedia.org/wiki/Wikipedia:Vital_articles)", which organize articles based on their perceived importance to the website on a 1 to 5 scale based on their overall importance to the site.

This project aims to compare the “Path to Philosophy metric” as a basis alongside the vital score to examine whether or not an article being closer to Philosophy is associated with a higher perceived importance, along with classifying which pages really form the foundation of Wikipedia's knowledge. 

### Usage

git clone the repository
```
git clone https://github.com/pnotato/WikipediaFoundations.git
cd WikipediaFoundations
```

Install the Python packages
```
pip install -r requirements.txt
```

- Scripts used to scrape Wikipedia and gather data from the API are located under ```/scripts```
- Scripts used to generate plots and compute p-values can be found under ```/analysis```
