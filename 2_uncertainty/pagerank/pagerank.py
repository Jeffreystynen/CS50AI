import os
import random
import re
import sys

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
    probability_distribution = {page_name: 0 for page_name in corpus}
    
    # If page has no links pretend it has a link to every page
    if len(corpus[page]) == 0:
        for page_name in probability_distribution:
            probability_distribution[page_name] = 1 / len(corpus)
        return probability_distribution
    
    # Probabilty for picking a page at random
    random_page = (1 - damping_factor) / len(corpus)

     # Probablilty for picking a link at radom on the current page
    random_link = damping_factor / len(corpus[page])

    # Add probabilities to the distribution
    for page_name in probability_distribution:
        probability_distribution[page_name] += random_page

        # Add the probablity of clicking on a page to the ditribution
        if page_name in corpus[page]:
            probability_distribution[page_name] += random_link
    
    return probability_distribution



def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_ranks = {page: 0 for page in corpus}

    # Choose random page and add a visit to that page
    sample_page = random.choice(list(corpus.keys()))
    page_ranks[sample_page] += 1

    for i in range(n - 1):
        # Pass the sample to transition_model to calculate the probability distibution
        trans_model = transition_model(corpus, sample_page, damping_factor)
        
        # Choose next random sample based on the probability distribution form the transition model
        next_sample = random.choices(list(trans_model.keys()), weights=list(trans_model.values()))[0]

        # Add a visit to the page that was sampled
        page_ranks[next_sample] += 1

        sample_page = next_sample

    # Normalize page ranks
    total_samples = sum(page_ranks.values())
    page_ranks = {page: count / total_samples for page, count in page_ranks.items()}

    return page_ranks


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    total_number_of_pages = len(corpus)

    # Set the page ranks to 1/total number of pages
    page_rank = {page : 1 / total_number_of_pages for page in corpus}

    # Define accuracy parameter
    accuracy = 0.001

    # Keep itterating until the desired accuracy is achieved
    while True:
        # Make copy for comparison
        old_rank = page_rank.copy()

        # Apply formula to each page
        for page in corpus:
            rank = (1 - damping_factor) / total_number_of_pages
            rank += damping_factor * sum(old_rank[link] / len(corpus[link]) for link in corpus if page in corpus[link])
            page_rank[page] = rank

        # If the accuracy is achieved for every page, break the loop
        if all(abs(old_rank[page] - page_rank[page]) < accuracy for page in corpus):
            break

    # Normalize page ranks
    total_rank = sum(page_rank.values())
    page_rank = {page: count / total_rank for page, count in page_rank.items()}

    return page_rank


if __name__ == "__main__":
    main()
