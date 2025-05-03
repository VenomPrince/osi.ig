#!/usr/bin/env python3
"""
Email validation module for Instagram OSINT tool
"""

import re
import smtplib
import dns.resolver
import socket
import logging
from typing import Dict, Tuple, Optional
from .local import Colors

# Configure logging
logger = logging.getLogger('email_validator')

class EmailValidator:
    """Class to validate email addresses"""
    
    def __init__(self, timeout: int = 5):
        """
        Initialize the email validator
        
        Args:
            timeout: Timeout for SMTP connections in seconds
        """
        self.timeout = timeout
        self.regex = r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,})$"
    
    def validate_syntax(self, email: str) -> bool:
        """
        Validate email syntax using regex
        
        Args:
            email: Email address to validate
            
        Returns:
            True if syntax is valid, False otherwise
        """
        match = re.match(self.regex, email.lower())
        return match is not None
    
    def validate_domain(self, domain: str) -> Tuple[bool, Optional[str]]:
        """
        Validate email domain by checking MX records
        
        Args:
            domain: Domain to validate
            
        Returns:
            Tuple of (success, mx_record or None)
        """
        try:
            records = dns.resolver.resolve(domain, 'MX')
            mx_record = str(records[0].exchange).lower()
            return True, mx_record
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
            return False, None
        except Exception as e:
            logger.warning(f"Error checking MX records for {domain}: {str(e)}")
            return False, None
    
    def validate_mailbox(self, email: str, mx_record: str) -> bool:
        """
        Validate mailbox by attempting SMTP connection
        
        Args:
            email: Email address to validate
            mx_record: MX record to connect to
            
        Returns:
            True if mailbox appears valid, False otherwise
        """
        fromaddr = 'verify@example.com'
        
        try:
            connect = smtplib.SMTP(timeout=self.timeout)
            connect.set_debuglevel(0)
            connect.connect(mx_record)
            connect.helo(socket.getfqdn())
            connect.mail(fromaddr)
            code, message = connect.rcpt(str(email))
            connect.quit()
            
            return code == 250
            
        except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected,
                smtplib.SMTPHeloError, socket.timeout, ConnectionRefusedError):
            return False
        except Exception as e:
            logger.warning(f"Error during SMTP validation for {email}: {str(e)}")
            return False
    
    def validate(self, email: str) -> Dict[str, bool]:
        """
        Perform full email validation
        
        Args:
            email: Email address to validate
            
        Returns:
            Dictionary with validation results
        """
        results = {
            'syntax': False,
            'domain': False,
            'mailbox': False
        }
        
        # Check syntax
        syntax_valid = self.validate_syntax(email)
        results['syntax'] = syntax_valid
        print(f"Syntax validation: {'Success' if syntax_valid else 'Failed'}")
        
        if not syntax_valid:
            return results
            
        # Check domain
        domain = email.split('@')[1]
        domain_valid, mx_record = self.validate_domain(domain)
        results['domain'] = domain_valid
        
        if domain_valid:
            print(f"Domain validation: Success (MX: {mx_record})")
        else:
            print("Domain validation: Failed (No valid MX records)")
            return results
            
        # Check mailbox
        if mx_record:
            mailbox_valid = self.validate_mailbox(email, mx_record)
            results['mailbox'] = mailbox_valid
            print(f"SMTP validation: {'Success' if mailbox_valid else 'Failed'}")
            
        return results

def check_email(email: str) -> None:
    """
    Validate an email address and print results
    
    Args:
        email: Email address to validate
    """
    print(f"\n{Colors.SUCCESS} Validating email: {email}")
    validator = EmailValidator()
    validator.validate(email)
