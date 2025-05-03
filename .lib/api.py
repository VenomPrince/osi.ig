#!/usr/bin/env python3
"""
Instagram OSINT Tool API Module
Handles interactions with Instagram's public API and data processing
"""

import requests
import random
import json
import sys
import time
import logging
from typing import Dict, List, Any, Optional, Union
from .local import *
from .exceptions import InstagramAPIError, ProfileNotFoundError, RateLimitError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('instagram_osint')

class InstagramAPI:
    """Class to handle Instagram API interactions and data processing"""
    
    def __init__(self, config: Dict = None):
        """
        Initialize the Instagram API client
        
        Args:
            config: Configuration dictionary with optional proxy settings
        """
        self.session = self._create_session(config)
        self.resp_js = None
        self.is_private = False
        self.total_uploads = 12
        self.rate_limit_delay = 2  # Seconds between requests to avoid rate limiting
        
    def _create_session(self, config: Dict = None) -> requests.Session:
        """
        Create and configure a requests session
        
        Args:
            config: Configuration dictionary with optional proxy settings
            
        Returns:
            Configured requests session
        """
        session = requests.session()
        session.headers = {'User-Agent': random.choice(USERAGENT)}
        
        # Apply proxy configuration if provided
        if config and 'proxy' in config and config['proxy'].get('enabled', False):
            proxy_config = config['proxy']
            session.proxies = {
                'http': f"{proxy_config.get('type', 'socks5')}://{proxy_config.get('host', '127.0.0.1')}:{proxy_config.get('port', '9050')}",
                'https': f"{proxy_config.get('type', 'socks5')}://{proxy_config.get('host', '127.0.0.1')}:{proxy_config.get('port', '9050')}"
            }
            logger.info(f"Using proxy: {session.proxies['https']}")
            
        return session
    
    def enable_tor_proxy(self) -> None:
        """Enable TOR proxy for the session"""
        self.session.proxies = {
            'http':  'socks5://127.0.0.1:9050',
            'https': 'socks5://127.0.0.1:9050'
        }
        logger.info("TOR proxy enabled")
    
    def get_profile_page(self, username: str) -> str:
        """
        Fetch Instagram profile data
        
        Args:
            username: Instagram username to fetch
            
        Returns:
            JSON response as string
            
        Raises:
            ProfileNotFoundError: If profile doesn't exist
            RateLimitError: If rate limited by Instagram
            InstagramAPIError: For other API errors
        """
        time.sleep(self.rate_limit_delay)  # Rate limiting protection
        
        try:
            response = self.session.get(f'https://www.instagram.com/{username}/?__a=1', timeout=10)
            
            if response.status_code == 404:
                raise ProfileNotFoundError(f"Profile '{username}' not found")
            elif response.status_code == 429:
                raise RateLimitError("Rate limited by Instagram. Try again later or use a proxy.")
            elif response.status_code != 200:
                raise InstagramAPIError(f"Instagram API returned status code: {response.status_code}")
            
            # Check if the response is HTML (which would indicate an error or login requirement)
            if '<html' in response.text.lower():
                raise InstagramAPIError("Instagram returned HTML instead of JSON. The API may have changed or requires login.")
                
            self.resp_js = response.text
            return self.resp_js
            
        except requests.exceptions.RequestException as e:
            raise InstagramAPIError(f"Request failed: {str(e)}")
    
    def extract_info(self) -> Dict[str, List[str]]:
        """
        Extract additional information like emails, tags, and mentions
        
        Returns:
            Dictionary containing emails, tags, and mentions
        """
        if not self.resp_js:
            raise InstagramAPIError("No data available. Fetch profile first.")
            
        return find(self.resp_js)
    
    def get_user_info(self, username: str) -> Dict[str, Any]:
        """
        Get comprehensive information about an Instagram user
        
        Args:
            username: Instagram username
            
        Returns:
            Dictionary with user information
            
        Raises:
            Various exceptions for API errors
        """
        try:
            self.get_profile_page(username)
            js = json.loads(self.resp_js)
            
            # Handle API response structure changes
            if 'graphql' not in js:
                logger.error("Unexpected API response format")
                logger.debug(f"Response: {self.resp_js[:100]}...")  # Log truncated response for debugging
                raise InstagramAPIError("Instagram API response format has changed")
                
            js = js['graphql']['user']
            
            # Update class properties
            self.is_private = js['is_private']
            self.total_uploads = min(12, js['edge_owner_to_timeline_media']['count'])
            
            # Build user info dictionary
            userinfo = {
                'username': js['username'],
                'user_id': js['id'],
                'name': js['full_name'],
                'followers': js['edge_followed_by']['count'],
                'following': js['edge_follow']['count'],
                'posts_img': js['edge_owner_to_timeline_media']['count'],
                'posts_vid': js['edge_felix_video_timeline']['count'],
                'reels': js['highlight_reel_count'],
                'bio': js['biography'].replace('\n', ', '),
                'external_url': js['external_url'],
                'private': js['is_private'],
                'verified': js['is_verified'],
                'profile_img': urlshortner(js['profile_pic_url_hd']),
                'business_account': js['is_business_account'],
                'joined_recently': js['is_joined_recently'],
                'business_category': js['business_category_name'],
                'category': js['category_enum'],
                'has_guides': js['has_guides'],
            }
            
            # Get additional information
            additional_info = self.extract_info()
            userinfo.update({
                'emails': additional_info['email'],
                'most_used_tags': sort_list(additional_info['tags']),
                'most_mentioned': sort_list(additional_info['mention'])
            })
            
            return userinfo
            
        except json.JSONDecodeError:
            raise InstagramAPIError("Failed to parse Instagram API response")
        except KeyError as e:
            raise InstagramAPIError(f"Missing field in API response: {str(e)}")
    
    def get_post_info(self, post_index: int) -> Dict[str, Any]:
        """
        Get information about a specific post
        
        Args:
            post_index: Index of the post (0-based)
            
        Returns:
            Dictionary with post information
            
        Raises:
            InstagramAPIError: For various errors
        """
        if not self.resp_js:
            raise InstagramAPIError("No data available. Fetch profile first.")
            
        if self.is_private:
            raise InstagramAPIError("Cannot retrieve post info for private accounts")
            
        try:
            x = json.loads(self.resp_js)
            js = x['graphql']['user']['edge_owner_to_timeline_media']['edges'][post_index]['node']
            
            # Base post information
            info = {
                'comments': js['edge_media_to_comment']['count'],
                'comment_disabled': js['comments_disabled'],
                'timestamp': js['taken_at_timestamp'],
                'likes': js['edge_liked_by']['count'],
                'location': js['location'],
            }
            
            # Extract caption if available
            try:
                info['caption'] = js['edge_media_to_caption']['edges'][0]['node']['text']
            except (IndexError, KeyError):
                info['caption'] = None
                
            # Handle multiple images/videos in a post
            child_media = []
            
            if 'edge_sidecar_to_children' in js:
                # Multiple media in post
                for child in js['edge_sidecar_to_children']['edges']:
                    child_node = child['node']
                    media_info = self._extract_media_info(child_node)
                    child_media.append(media_info)
                    
            else:
                # Single media post
                media_info = self._extract_media_info(js)
                child_media.append(media_info)
                
            return {
                'info': info,
                'media': child_media
            }
            
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            raise InstagramAPIError(f"Error parsing post data: {str(e)}")
    
    def _extract_media_info(self, node: Dict) -> Dict:
        """
        Extract media information from a node
        
        Args:
            node: Media node from Instagram API
            
        Returns:
            Dictionary with media information
        """
        return {
            'typename': node['__typename'],
            'id': node['id'],
            'shortcode': node['shortcode'],
            'dimensions': f"{node['dimensions']['height']}x{node['dimensions']['width']}",
            'image_url': node['display_url'],
            'is_video': node['is_video'],
            'accessibility_caption': node.get('accessibility_caption'),
            'fact_check_overall': node.get('fact_check_overall_rating'),
            'fact_check_info': node.get('fact_check_information'),
        }
        
    def get_all_posts(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Get information about all available posts
        
        Args:
            limit: Maximum number of posts to retrieve (default: all available)
            
        Returns:
            List of post information dictionaries
        """
        if self.is_private:
            raise InstagramAPIError("Cannot retrieve posts for private accounts")
            
        post_count = min(limit or self.total_uploads, self.total_uploads)
        posts = []
        
        for i in range(post_count):
            try:
                post_info = self.get_post_info(i)
                posts.append(post_info)
            except InstagramAPIError as e:
                logger.warning(f"Failed to retrieve post {i}: {str(e)}")
                
        return posts
