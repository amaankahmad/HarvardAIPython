import os
import random
import re
import sys
import copy
import math

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # Initialise a dictionary for the distribution
    distribution = {}

    # Page has links
    if corpus[page]:
        for link in corpus: 
            distribution[link] = (1-damping_factor) / len(corpus)
            if link in corpus[page]:
                distribution[link] += damping_factor / len(corpus[page])
    # Page doesn't have links
    else:
        for link in corpus:
            distribution[link] = 1/len(corpus)

    return distribution

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.
    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Initialise a dictionary for the distribution of the pages
    pagerank = {}
    # Initialise a key for each page in the corpus
    for page in corpus:
        pagerank[page] = 0
    # Randomly choose a page
    page = random.choice(list(corpus.keys()))

    # Iterate through number of samples
    for i in range(1,n):
        # Obtain values from transition_model
        current_distribution = transition_model(corpus, page, damping_factor)
        # Iterating through each page, obtain the distribution values
        for page in pagerank:
            pagerank[page] = ((i-1) * pagerank[page] + current_distribution[page]) / i

        # Randomly choose a page from pagerank for transition model distribution
        page = random.choices(list(pagerank.keys()), list(pagerank.values()), k=1)[0]

    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.
    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Initialise a dictionary for the distribution of the pages
    pagerank = {}
    newrank = {}

    # Assign initial values for pagerank
    for page in corpus:
        pagerank[page] = 1 / len(corpus)

    # Intialise repeat value
    valid = True

    while valid:
        for page in pagerank:
            sum = 0.0
            for possible_page in corpus:
                # Page has links
                if page in corpus[possible_page]:
                    sum += pagerank[possible_page] / len(corpus[possible_page])
                # Page has no links
                if not corpus[possible_page]:
                    sum += pagerank[possible_page] / len(corpus)
            # Iterative formula 
            newrank[page] = (1 - damping_factor) / len(corpus) + damping_factor * sum
        # If change within threshold break out, else repeat process
        for page in pagerank:
            if math.isclose(newrank[page], pagerank[page], abs_tol=0.001):
                # Break out
                valid = False
            else:
                # Assign new values to current values and repeat
                pagerank[page] = newrank[page]

    return pagerank
            

if __name__ == "__main__":
    main()
