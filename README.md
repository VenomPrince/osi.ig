OSI.IG - Open Source Information Instagram Tool
<p align="center"> <img src="https://raw.githubusercontent.com/th3unkn0n/OSI.IG/master/.lib/20191103_233944.jpg" width="300" height="120"> </p> <p align="center"> <img src="https://img.shields.io/badge/Version-3.0-brightgreen"> <a href="https://github.com/th3unkn0n"> <img src="https://img.shields.io/github/followers/th3unkn0n?label=Follow&style=social"> </a> <a href="https://github.com/th3unkn0n/osi.ig/stargazers"> <img src="https://img.shields.io/github/stars/th3unkn0n/osi.ig?style=social"> </a> </p> <p align="center"> Open Source Information Instagram - Enhanced OSINT Tool </p>
Features

OSI.IG is a powerful Instagram OSINT (Open Source Intelligence) tool that retrieves comprehensive information from Instagram profiles without requiring login credentials.
Information Collected:
📊 Profile Information

    User ID, username, full name
    Followers and following counts
    Post counts (images and videos)
    Profile image URL
    Bio information and external URL
    Account type (business, personal)
    Verification status
    Business category and other profile metadata

📧 Contact Information

    Emails mentioned in profile or posts
    Email validation (syntax, domain, and mailbox verification)

🔍 Content Analysis

    Most used hashtags
    Most mentioned accounts
    Post information and metadata
    Media URLs and types
    Captions and engagement metrics
    Location data (when available)

🛠️ Advanced Features

    Proxy support (including TOR)
    Output results to JSON
    Rate limit protection
    Comprehensive error handling

Installation
Option 1: Standard Installation

bash

# Install required packages
$ apt-get install python3 python3-pip git

# Clone the repository
$ git clone https://github.com/th3unkn0n/osi.ig.git && cd osi.ig

# Install dependencies
$ pip3 install -r requirements.txt

Option 2: Docker Installation

bash

# Build the Docker image
$ docker build -t osi-ig .

# Run the container
$ docker run -it osi-ig

Usage
Basic Commands

bash

# Get profile information
$ python3 main.py -u <username>

# Get profile and post information
$ python3 main.py -u <username> -p

# Use TOR proxy for requests
$ python3 main.py -u <username> --proxy

# Save results to JSON file
$ python3 main.py -u <username> -p -o results.json

# Validate an email address
$ python3 main.py -e example@domain.com

# Enable verbose output
$ python3 main.py -u <username> -v

# Show help
$ python3 main.py -h

Advanced Configuration

You can create a config.json file to customize settings:

json

{
  "proxy": {
    "enabled": true,
    "type": "socks5",
    "host": "127.0.0.1",
    "port": "9050"
  },
  "output": {
    "format": "json",
    "path": "./output/"
  }
}

Then use it with:

bash

$ python3 main.py -u <username> --config config.json

Limitations

    Instagram's API changes frequently, which may affect tool functionality
    Some information may not be available for private accounts
    Rate limiting may occur with frequent requests
    This tool is designed for educational and research purposes only

Legal Disclaimer

This tool is provided for educational and research purposes only. Usage of this tool for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state, and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program.
Contribution

Contributions are welcome! Please feel free to submit a Pull Request.
License

This project is licensed under the MIT License - see the LICENSE file for details.
