import requests  
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from anytree import Node, RenderTree
from tqdm import tqdm
import argparse
import re

class WebCrawler:
    def __init__(self, base_url, max_depth=3):
        self.base_url = base_url
        self.max_depth = max_depth
        self.visited = set()
        self.directories = set()

    def crawl(self, url, depth=1):
        """Crawl the website recursively while preventing non-existent depths and adjusting depth starting from 1."""
        if depth > self.max_depth:
            return
        if url in self.visited:
            return
        self.visited.add(url)

        # Try fetching the page
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return
        except requests.RequestException:
            return

        # Parse the page
        soup = BeautifulSoup(response.content, "html.parser")
        self.extract_directories(url, soup)

        # Find all internal links
        links = soup.find_all("a", href=True)
        internal_links = []

        for link in links:
            href = link["href"]
            full_url = urljoin(url, href)
            parsed_url = urlparse(full_url)
            if parsed_url.netloc == urlparse(self.base_url).netloc:  # Ensure the link is internal
                internal_links.append(full_url)

        # If there are valid internal links, continue crawling
        if internal_links:
            for link in tqdm(internal_links, desc=f"Processing Links at Depth {depth}", unit="link", dynamic_ncols=True, leave=False):
                self.crawl(link, depth + 1)

    def extract_urls(self, content):
        """Extract and filter valid URLs from content."""
        url_pattern = r'/(?:[a-zA-Z0-9_-]+/?)+'  # Match paths
        all_urls = re.findall(url_pattern, content)
        
        # Filter unwanted patterns
        valid_urls = [
            url for url in all_urls
            if not re.search(r'@|\d+$|/VUMChealth', url)  # Exclude emails, purely numeric, and odd patterns
        ]
        return valid_urls

    def extract_directories(self, base_url, soup):
        """Extract directory-like URLs from the page."""
        page_content = soup.prettify()  # Get the HTML content as a string
        filtered_urls = self.extract_urls(page_content)  # Filter URLs using `extract_urls`
        self.directories.update(filtered_urls)  # Add to the directory set

    def get_directory_tree(self):
        """Create a directory tree from the relative paths."""
        root = Node("/")
        path_nodes = {}

        for directory in tqdm(self.directories, desc="Building Tree", unit="directory", dynamic_ncols=True, leave=False):
            path_parts = directory.strip("/").split("/")
            current_node = root

            for part in path_parts:
                if part not in path_nodes:
                    path_nodes[part] = Node(part, parent=current_node)
                current_node = path_nodes[part]

        return root

    def save_directory_list(self, filename):
        """Save the directory list to a file."""
        with open(filename, "w") as f:
            for directory in tqdm(sorted(self.directories), desc="Saving Directories", unit="directory", dynamic_ncols=True, leave=False):
                f.write(directory + "\n")

    def save_tree_structure(self, filename):
        """Save the tree structure to a text file."""
        root = self.get_directory_tree()
        with open(filename, "w") as f:
            for pre, _, node in RenderTree(root):
                f.write(f"{pre}{node.name}\n")


def get_domain_name(url):
    """Extract the main domain name from the URL."""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    # Remove subdomains and TLD (e.g., www.verily.com -> verily)
    domain_name = re.sub(r"^(www\.)?", "", domain).split(".")[0]
    return domain_name


def parse_arguments():
    parser = argparse.ArgumentParser(description="Crawl a website and generate directory structure.")
    parser.add_argument("url", help="The base URL of the website to crawl.")
    parser.add_argument("-d", "--depth", type=int, default=3, help="Maximum depth of the crawl.")
    return parser.parse_args()


def main():
    args = parse_arguments()

    # Extract the main domain name for file naming
    domain_name = get_domain_name(args.url)

    # Output file names
    list_filename = f"dirs_{domain_name}.txt"
    tree_filename = f"tree_{domain_name}.txt"

    # Initialize the crawler
    crawler = WebCrawler(args.url, args.depth)

    # Start crawling from the base URL
    crawler.crawl(args.url)

    # Save the directory list and tree structure
    crawler.save_directory_list(list_filename)
    crawler.save_tree_structure(tree_filename)

    print(f"Directory list saved to {list_filename}")
    print(f"Tree structure saved to {tree_filename}")


if __name__ == "__main__":
    main()
