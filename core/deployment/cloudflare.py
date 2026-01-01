"""
Cloudflare DNS integration for updating DNSLink records.
"""

from typing import Any, Dict, Optional

import requests


class CloudflareManager:
    """Handle Cloudflare DNS updates for IPFS DNSLink."""

    def __init__(
        self,
        email: str,
        api_key: str,
        zone_id: str,
        hostname: str,
    ):
        """
        Initialize Cloudflare manager with credentials.

        Args:
            email: Cloudflare account email
            api_key: Cloudflare API key
            zone_id: Cloudflare zone ID
            hostname: Hostname to update (e.g., blog.example.com)
        """
        self.email = email
        self.api_key = api_key
        self.zone_id = zone_id
        self.hostname = hostname
        self.base_url = "https://api.cloudflare.com/client/v4"

    def update_dnslink(
        self, cid: str, description: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Update DNSLink record on Cloudflare to point to new IPFS CID.

        Args:
            cid: IPFS CID (v1) to point to
            description: Optional description (e.g., deployment ID)

        Returns:
            Response data if successful, None otherwise
        """
        try:
            url = f"{self.base_url}/zones/{self.zone_id}/web3/hostnames/{self.hostname}"

            headers = {
                "Content-Type": "application/json",
                "X-Auth-Email": self.email,
                "X-Auth-Key": self.api_key,
            }

            data = {
                "description": description,
                "dnslink": f"/ipfs/{cid}",
            }

            response = requests.patch(url, headers=headers, json=data)

            if response.status_code == 200:
                result = response.json()
                return result
            elif response.status_code == 202:
                # 202 Accepted - request is being processed
                result = response.json()
                result["_status_code"] = 202  # mark as pending
                return result
            else:
                print(
                    f"⚠️  Cloudflare update failed (status {response.status_code}): {response.text}"
                )
                return None

        except Exception as e:
            print(f"⚠️  Error updating Cloudflare DNS: {e}")
            return None

    def test_connection(self) -> bool:
        """
        Test Cloudflare API connection and credentials.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            url = f"{self.base_url}/zones/{self.zone_id}"

            headers = {
                "X-Auth-Email": self.email,
                "X-Auth-Key": self.api_key,
            }

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                return True
            else:
                print(f"⚠️  Cloudflare connection test failed: {response.text}")
                return False

        except Exception as e:
            print(f"⚠️  Error testing Cloudflare connection: {e}")
            return False
