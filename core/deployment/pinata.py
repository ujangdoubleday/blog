"""
Pinata IPFS deployment module for uploading blog output to IPFS.
"""
from pathlib import Path
from typing import Optional, Dict, Any
from pinatapy import PinataPy


class PinataDeployer:
    """Handle deployment to Pinata IPFS service using PinataPy SDK."""

    def __init__(self, api_key: str, api_secret: str, jwt: str = None):
        """Initialize Pinata deployer with credentials."""
        self.api_key = api_key
        self.api_secret = api_secret
        self.jwt = jwt  # Not used with SDK but kept for compatibility
        self.pinata = PinataPy(api_key, api_secret)

    def test_authentication(self) -> bool:
        """Test if Pinata credentials are valid by trying to list pins."""
        try:
            # Test authentication by listing pins (no parameters)
            self.pinata.pin_list()
            return True
        except Exception as e:
            print(f"Authentication test failed: {e}")
            return False

    def upload_folder(
        self, folder_path: str, name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Upload entire folder to Pinata IPFS using PinataPy SDK.

        Args:
            folder_path: Path to the folder to upload
            name: Optional name for the upload

        Returns:
            Response data from Pinata API or None if failed
        """
        folder_path = Path(folder_path)

        if not folder_path.exists() or not folder_path.is_dir():
            print(f"Error: Folder {folder_path} does not exist or is not a directory")
            return None

        try:
            print(f"📤 Uploading folder {folder_path} to IPFS...")

            destination = "/" if not name else f"/{name}"

            result = self.pinata.pin_file_to_ipfs(
                str(folder_path),
                ipfs_destination_path=destination,
                save_absolute_paths=False,
            )

            print("✅ Upload successful!")
            print(f"📍 IPFS Hash: {result['IpfsHash']}")
            print(
                f"📁 IPFS Link: https://gateway.pinata.cloud/ipfs/{result['IpfsHash']}"
            )
            print(f"🔗 Public Link: https://ipfs.io/ipfs/{result['IpfsHash']}")

            return result

        except Exception as e:
            print(f"❌ Error uploading folder: {e}")
            return None

    def list_pins(self, limit: int = 10) -> Optional[Dict[str, Any]]:
        """List pinned files on Pinata using SDK."""
        try:
            return self.pinata.pin_list()
        except Exception as e:
            print(f"Error listing pins: {e}")
            return None

    def unpin_file(self, ipfs_hash: str) -> bool:
        """Remove a file from Pinata using SDK."""
        try:
            self.pinata.remove_pin_from_ipfs(ipfs_hash)
            return True
        except Exception as e:
            print(f"Error unpinning file: {e}")
            return False
