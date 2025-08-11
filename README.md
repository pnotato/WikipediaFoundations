# Wikipedia Foundations

> Following the first hyperlink in the main text of an English Wikipedia article, and then repeating the process for subsequent articles, usually leads to the Philosophy article. [Getting to Philosphy - Wikipedia](https://en.wikipedia.org/wiki/Wikipedia:Getting_to_Philosophy)

An analysis of this phenomenon in Python. My final project submission for CMPT 353: Computational Data Science.

### Goals
1. Scrape a large amount of Wikipedia articles and recursively enter the first hyperlink until we reach the Philosophy page. Keep track of the amount of pages it takes to reach the philosophy page, and the content of the pages at each level.
2. With this data, train a ML model with a classification technique (kNN, random forest), and determine how foundational/abstract each wikipedia page is.
3. Use the model to predict the complexity level of future pages.
4. Find a better name for this project.

### Changes

This idea doesn't seem to be original enough. I've added a few changes here. README will be changed later on.

1. Scrape a large amount of Wikipedia articles and recursively enter the first hyperlink until we reach the Philosophy page. Keep track of the amount of pages it takes to reach the philosophy page, and the content of the pages at each level.

2. Plot the amount of pages it takes to reach philosophy. This will be used to determine how "foundational" a page is. Other weights such as older pages, and more outbound pages will be used to determine this. Unsupervised classification?

3. Do pages with more inbound or outbound links tend to be more foundational? Perhaps some links are reached much more often, and we can determine how foundational they are.

4. Are longer articles considered to be more foundational? Are foundational articles more or less counted foundational?


