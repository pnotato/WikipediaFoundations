# Thoughts

This file will probably be deleted in the final project submission. For those stalking my Github commits though, here is my thought process as I am making this project.

# Stage 1: Gathering the data

Experimenting with actually obtaining the data right now. Using bs4 we can achieve a pretty basic analysis by rapidly querying "https://en.wikipedia.org/wiki/Special:Random"

This however, does not provide any other important metadata. Perhaps use of the API may help?

Seems like I can extract the data from the API. Right now I have a very badly made scraper that will ping the random page, grab the title, and get the data from the API. 

# Other thoughts

Hmm... It seems pretty interesting how a lot of paths lead to the same page. Maybe I could do another project (i. e. optimal path from one page to another with Djikstra's?)