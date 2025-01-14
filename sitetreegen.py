from anytree import Node, RenderTree
from tqdm import tqdm
import argparse


class VirtualTree:
    def __init__(self):
        self.root = Node("/")  # Root of the virtual directory tree
        self.path_nodes = {}

    def add_path(self, path):
        """Adds a relative path to the virtual directory tree."""
        path_parts = path.strip("/").split("/")
        current_node = self.root

        for part in path_parts:
            if part not in self.path_nodes:
                self.path_nodes[part] = Node(part, parent=current_node)
            current_node = self.path_nodes[part]

    def save_tree(self, filename):
        """Saves the tree structure to a file."""
        with open(filename, "w") as f:
            for pre, _, node in RenderTree(self.root):
                f.write(f"{pre}{node.name}\n")

    def print_tree(self):
        """Prints the tree structure to the console."""
        for pre, _, node in RenderTree(self.root):
            print(f"{pre}{node.name}")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate a virtual directory tree from relative paths.")
    parser.add_argument("-i", "--input", required=True, help="Input file containing relative paths.")
    parser.add_argument("-o", "--output", help="Output file to save the tree structure.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print the tree structure to the console.")
    return parser.parse_args()


def read_paths(filename):
    """Reads relative paths from the input file."""
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip()]


def main():
    args = parse_arguments()

    # Read relative paths from the input file
    paths = read_paths(args.input)

    # Create and populate the virtual directory tree
    tree = VirtualTree()
    for path in tqdm(paths, desc="Building Tree", unit="path", dynamic_ncols=True):
        tree.add_path(path)

    # Save the tree structure to a file if specified
    if args.output:
        tree.save_tree(args.output)
        print(f"Tree structure saved to {args.output}")

    # Print the tree structure to the console if verbose mode is enabled
    if args.verbose:
        tree.print_tree()


if __name__ == "__main__":
    main()
