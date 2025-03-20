#!/usr/bin/env python3
"""
Website Upload Path Finder
This script checks for common upload paths on websites to help identify where upload 
functionality might be located. This is intended for legitimate security testing and 
educational purposes only.
"""

import requests
import concurrent.futures
import argparse
import sys
from urllib.parse import urljoin
from colorama import init, Fore, Style

# Initialize colorama for colored terminal output
init()

# Common upload paths to check
UPLOAD_PATHS = [
    "/upload/",
    "/uploads/",
    "/fileupload/",
    "/file-upload/",
    "/uploadfiles/",
    "/upload-file/",
    "/uploader/",
    "/file/",
    "/files/",
    "/media/upload/",
    "/admin/upload/",
    "/admin/uploads/",
    "/wp-content/uploads/",
    "/images/uploads/",
    "/img/upload/",
    "/media/uploads/",
    "/assets/uploads/",
    "/upload/image/",
    "/upload/files/",
    "/upload/media/",
    "/upload/documents/",
    "/api/upload/",
    "/api/v1/upload/",
    "/api/files/upload/",
    "/public/uploads/",
    "/storage/uploads/",
    "/user/uploads/",
    "/users/uploads/",
    "/profile/upload/",
    "/avatar/upload/",
    "/temp/uploads/",
    "/tmp/uploads/",
    "/data/uploads/",
    "/content/uploads/",
    "/resources/uploads/",
    "/static/uploads/",
    "/attachments/",
    "/images/",
    "/img/",
    "/documents/",
    "/docs/",
    "/files/upload/",
    "/dashboard/upload/",
    "/panel/upload/",
    "/cp/upload/",
    "/administrator/uploads/",
    "/manager/uploads/",
    "/members/uploads/",
    "/customer/uploads/",
]

def check_url(base_url, path):
    """Check if a specific upload path exists on the website."""
    url = urljoin(base_url, path)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
        
        # Check for successful response codes
        if response.status_code < 400:
            # Try a GET request to confirm
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code < 400:
                # Look for upload-related keywords in the response
                if b'upload' in response.content.lower() or b'file' in response.content.lower():
                    return (True, url, response.status_code)
        
        # If not a success
        return (False, url, response.status_code)
    
    except requests.exceptions.RequestException:
        return (False, url, None)

def find_upload_paths(target_url):
    """Find potential upload paths on the target website."""
    
    print(f"{Fore.BLUE}[*] Scanning {target_url} for upload paths...{Style.RESET_ALL}")
    print(f"{Fore.BLUE}[*] Checking {len(UPLOAD_PATHS)} common upload paths{Style.RESET_ALL}")
    print("-" * 60)
    
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_path = {executor.submit(check_url, target_url, path): path for path in UPLOAD_PATHS}
        
        for future in concurrent.futures.as_completed(future_to_path):
            path = future_to_path[future]
            found, url, status_code = future.result()
            
            if found:
                print(f"{Fore.GREEN}[+] FOUND: {url} (Status: {status_code}){Style.RESET_ALL}")
                results.append(url)
            else:
                if status_code is not None and status_code < 404:
                    print(f"{Fore.YELLOW}[?] POSSIBLE: {url} (Status: {status_code}){Style.RESET_ALL}")
                    results.append(url)
                else:
                    print(f"{Fore.RED}[-] NOT FOUND: {url}{Style.RESET_ALL}")
    
    return results

def main():
    """Main function to parse arguments and run the scanner."""
    parser = argparse.ArgumentParser(description="Website Upload Path Finder")
    parser.add_argument("url", help="Target website URL (e.g., https://example.com)")
    parser.add_argument("-o", "--output", help="Output file to save results")
    args = parser.parse_args()
    
    target_url = args.url
    
    # Ensure the URL has the correct format
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'http://' + target_url
    
    print("\n" + "=" * 60)
    print(f"{Fore.CYAN}Website Upload Path Finder{Style.RESET_ALL}")
    print("=" * 60)
    
    try:
        found_paths = find_upload_paths(target_url)
        
        print("\n" + "=" * 60)
        if found_paths:
            print(f"{Fore.GREEN}[+] Found {len(found_paths)} potential upload paths:{Style.RESET_ALL}")
            for path in found_paths:
                print(f"    {path}")
                
            if args.output:
                with open(args.output, 'w') as f:
                    for path in found_paths:
                        f.write(f"{path}\n")
                print(f"\n{Fore.BLUE}[*] Results saved to {args.output}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}[!] No upload paths found. Try adding more paths to the script.{Style.RESET_ALL}")
        
        print("=" * 60)
    
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Scan interrupted by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()