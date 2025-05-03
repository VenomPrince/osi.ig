#!/usr/bin/env python3
"""
Utility functions and constants for Instagram OSINT tool
"""

import requests
import sys
import time
import re
import collections
from typing import Dict, List, Union, Any
from colorama import init, Fore, Style

# Initialize colorama for cross-platform color support
init(autoreset=True)

# Define colors in a more maintainable way
class Colors:
    NORMAL = Style.RESET_ALL
    RED = Fore.RED
    GREEN = Fore.GREEN
    CYAN = Fore.CYAN
    WHITE = Fore.WHITE
    YELLOW = Fore.BLUE
    
    SUCCESS = f"{Fore.RED}[{Fore.CYAN}+{Fore.RED}]{Style.RESET_ALL}"
    FAILURE = f"{Fore.RED}[{Fore.RED}!{Fore.RED}]{Style.RESET_ALL}"
    ERROR = f"{Fore.RED}[{Fore.BLUE}?{Fore.RED}]{Style.RESET_ALL}"

# User agents for rotating to avoid detection
USERAGENT = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36 Edg/91.0.864.53',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1'
]

def urlshortner(url: str) -> str:
    """
    Shorten a URL using TinyURL
    
    Args:
        url: URL to shorten
        
    Returns:
        Shortened URL or original URL on failure
    """
    try:
        data = requests.get("http://tinyurl.com/api-create.php?url=" + url, timeout=5)
        return data.text if data.status_code == 200 else url
    except requests.exceptions.RequestException:
        return url

def write_animated(text: str, delay: float = 0.05) -> None:
    """
    Print text with an animation effect
    
    Args:
        text: Text to print
        delay: Delay between characters (seconds)
    """
    for char in text:
        time.sleep(delay)
        sys.stdout.write(char)
        sys.stdout.flush()
    print()

def sort_list(items: List[str]) -> Dict[str, int]:
    """
    Count occurrences of items and sort by frequency
    
    Args:
        items: List of items to count and sort
        
    Returns:
        Dictionary with items as keys and counts as values, sorted by count (descending)
    """
    with_count = dict(collections.Counter(items))
    return {k: v for k, v in sorted(with_count.items(), reverse=True, key=lambda item: item[1])}

def find(text: str) -> Dict[str, List[str]]:
    """
    Extract emails, hashtags, and mentions from text
    
    Args:
        text: Text to search
        
    Returns:
        Dictionary with extracted information
    """
    result = {}
    
    # Find emails - improved regex pattern for better reliability
    emails = re.findall(r"[a-zA-Z0-9_.+-]+[＠@]{1}[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text.lower())
    result['email'] = emails
    
    # Find hashtags
    tags = re.findall(r"[＃#]{1}([_a-zA-Z0-9\.\+-]+)", text)
    result['tags'] = tags
    
    # Find mentions - cleaned up to handle edge cases
    mention = []
    raw_mention = re.findall(r"[＠@]([_a-zA-Z0-9\.\+-]+)", text)
    for x in raw_mention:
        if x.endswith("."):
            x = x.strip(".")
        mention.append(x)
    result['mention'] = mention
    
    return result

def clear_screen() -> None:
    """Clear the terminal screen in a cross-platform way"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def banner() -> None:
    """Display the OSINT tool banner"""
    print(f"""{Colors.CYAN}
 ╔═╗  ╔═╗  ╦     ╦  ╔═╗
 ║ ║  ╚═╗  ║     ║  ║ ╦
 ╚═╝  ╚═╝  ╩  {Colors.GREEN}o{Colors.CYAN}  ╩  ╚═╝
 
 {Colors.GREEN}Open Source Information Instagram v3.0
 {Colors.GREEN}https://github.com/th3unkn0n/osi.ig{Colors.NORMAL}
    """)

def format_table(headers: List[str], rows: List[List[Any]]) -> str:
    """
    Format data as a table with aligned columns
    
    Args:
        headers: List of column headers
        rows: List of rows, where each row is a list of values
        
    Returns:
        Formatted table as string
    """
    # Calculate column widths
    widths = [max(len(str(row[i])) for row in [headers] + rows) for i in range(len(headers))]
    
    # Create header
    header = " | ".join(f"{h:{w}}" for h, w in zip(headers, widths))
    separator = "-+-".join("-" * w for w in widths)
    
    # Create rows
    formatted_rows = [
        " | ".join(f"{str(v):{w}}" for v, w in zip(row, widths))
        for row in rows
    ]
    
    # Combine all parts
    return "\n".join([header, separator] + formatted_rows)

def print_dict(data: Dict, prefix: str = "", indent: int = 2) -> None:
    """
    Pretty print a dictionary with colored keys
    
    Args:
        data: Dictionary to print
        prefix: Prefix for each line
        indent: Indentation level
    """
    for key, value in data.items():
        if isinstance(value, dict):
            print(f"{prefix}{Colors.GREEN}{key}:")
            print_dict(value, prefix + " " * indent, indent)
        else:
            print(f"{prefix}{Colors.GREEN}{key}: {Colors.WHITE}{value}")
