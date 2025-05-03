#!/usr/bin/env python3
"""
OSI.IG - Open Source Information Instagram Tool
Main entry point for the Instagram OSINT tool

This tool fetches and displays information about Instagram profiles
without requiring authentication.
"""

import os
import sys
import json
import argparse
import logging
from typing import Dict, Any, List

# Add local library path to import path
sys.path.append(os.path.join(os.path.dirname(__file__), ".lib"))

from api import InstagramAPI
from local import banner, Colors, clear_screen, print_dict
from exceptions import InstagramOSINTError, ProfileNotFoundError
from check_mail import check_email

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('osint.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('osint.main')

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="OSI.IG - Open Source Information Instagram Tool",
        epilog="Example: python main.py -u username -p"
    )
    
    parser.add_argument("-u", "--user", help="Instagram username to scan")
    parser.add_argument("-p", "--post", action="store_true", help="Get detailed post information")
    parser.add_argument("-o", "--output", help="Output results to JSON file")
    parser.add_argument("-e", "--email", help="Validate a specific email address")
    parser.add_argument("--proxy", action="store_true", help="Use TOR proxy for requests")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--config", help="Path to configuration file")
    
    return parser.parse_args()

def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON file
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Error loading configuration: {str(e)}")
        print(f"{Colors.FAILURE} Error loading configuration file: {str(e)}")
        return {}

def save_to_json(data: Dict[str, Any], output_file: str) -> None:
    """
    Save data to a JSON file
    
    Args:
        data: Data to save
        output_file: Path to the output file
    """
    try:
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"{Colors.SUCCESS} Results saved to {output_file}")
    except Exception as e:
        logger.error(f"Error saving results: {str(e)}")
        print(f"{Colors.FAILURE} Error saving results: {str(e)}")

def display_user_info(user_info: Dict[str, Any]) -> None:
    """
    Display user information
    
    Args:
        user_info: User information dictionary
    """
    banner()
    
    print(f"{Colors.SUCCESS} {Colors.RED} User Information")
    print_dict(user_info)
    
    # Display emails if found
    if user_info.get('emails'):
        print(f"\n{Colors.SUCCESS} {Colors.RED} Emails Found:")
        for email in user_info['emails']:
            print(f"  {Colors.GREEN}{email}")
    
    # Display most used tags
    if user_info.get('most_used_tags'):
        print(f"\n{Colors.SUCCESS} {Colors.RED} Most Used Tags:")
        for tag, count in list(user_info['most_used_tags'].items())[:5]:
            print(f"  {Colors.GREEN}#{tag} : {Colors.WHITE}{count}")
    
    # Display most mentioned accounts
    if user_info.get('most_mentioned'):
        print(f"\n{Colors.SUCCESS} {Colors.RED} Most Mentioned Accounts:")
        for mention, count in list(user_info['most_mentioned'].items())[:5]:
            print(f"  {Colors.GREEN}@{mention} : {Colors.WHITE}{count}")
    
    print()

def display_post_info(posts: List[Dict[str, Any]]) -> None:
    """
    Display post information
    
    Args:
        posts: List of post information dictionaries
    """
    for i, post in enumerate(posts):
        print(f"\n{Colors.SUCCESS} {Colors.RED} Post {i+1}:")
        
        # Display post metadata
        print(f"{Colors.SUCCESS} {Colors.RED} Post Info:")
        print_dict(post['info'])
        
        # Display media information
        print(f"\n{Colors.SUCCESS} {Colors.RED} Contains {len(post['media'])} media items")
        for j, media in enumerate(post['media']):
            print(f"\n  {Colors.GREEN}Media Item {j+1}:")
            print_dict(media, "    ")

def main():
    """Main entry point for the application"""
    args = parse_arguments()
    
    # Set up logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Clear screen
    clear_screen()
    
    # Load configuration if specified
    config = load_config(args.config) if args.config else {}
    
    # Create API instance
    api = InstagramAPI(config)
    
    # Enable TOR proxy if requested
    if args.proxy:
        api.enable_tor_proxy()
    
    # Check if we're just validating an email
    if args.email:
        check_email(args.email)
        return
    
    # Ensure we have a username to process
    if not args.user:
        banner()
        print(f"{Colors.FAILURE} No username specified. Use -u/--user to specify an Instagram username.")
        print(f"Run 'python {sys.argv[0]} --help' for more information.")
        return
    
    try:
        # Get user information
        user_info = api.get_user_info(args.user)
        display_user_info(user_info)
        
        # Get post information if requested
        if args.post:
            if user_info['private']:
                print(f"{Colors.FAILURE} Cannot retrieve posts for private accounts.")
            else:
                posts = api.get_all_posts()
                display_post_info(posts)
        
        # Save results to JSON if requested
        if args.output:
            data = {
                "user_info": user_info
            }
            if args.post and not user_info['private']:
                data["posts"] = api.get_all_posts()
            save_to_json(data, args.output)
            
    except ProfileNotFoundError as e:
        logger.error(f"Profile not found: {str(e)}")
        print(f"{Colors.FAILURE} {str(e)}")
    except InstagramOSINTError as e:
        logger.error(f"Error: {str(e)}")
        print(f"{Colors.FAILURE} {str(e)}")
    except Exception as e:
        logger.exception("Unexpected error occurred")
        print(f"{Colors.FAILURE} An unexpected error occurred: {str(e)}")
        
if __name__ == "__main__":
    main()
