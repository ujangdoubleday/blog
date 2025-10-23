#!/usr/bin/env python3
"""
Deployment script for uploading blog to IPFS via Pinata.
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# add parent directory to path to import core modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.deployment.pinata import PinataDeployer  # noqa: E402
from core.deployment.snapshot import SnapshotManager  # noqa: E402


def load_environment():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent.parent / ".env"

    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment from {env_path}")
    else:
        print(f"⚠️  No .env file found at {env_path}")
        print("Make sure to set API_KEY, API_SECRET, and JWT environment variables")


def get_pinata_credentials():
    """Get Pinata credentials from environment variables."""
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")
    jwt = os.getenv("JWT")  # Optional for SDK

    if not all([api_key, api_secret]):
        missing = []
        if not api_key:
            missing.append("API_KEY")
        if not api_secret:
            missing.append("API_SECRET")

        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        print("Please set these variables in your .env file")
        return None, None, None

    return api_key, api_secret, jwt


def deploy_to_ipfs(output_dir: str, name: str = None):
    """Deploy the blog output to IPFS via Pinata."""
    print("🚀 Starting deployment to IPFS...")

    # load environment variables
    load_environment()

    # get credentials
    api_key, api_secret, jwt = get_pinata_credentials()
    if not all([api_key, api_secret]):
        return False

    # initialize deployer
    deployer = PinataDeployer(api_key, api_secret, jwt)

    # test authentication
    print("🔐 Testing Pinata authentication...")
    if not deployer.test_authentication():
        print("❌ Authentication failed. Please check your credentials.")
        return False

    print("✅ Authentication successful!")

    # check if output directory exists
    output_path = Path(output_dir)
    if not output_path.exists():
        print(f"❌ Output directory {output_path} does not exist.")
        print("Please run the build script first: python scripts/build.py")
        return False

    # upload folder
    print(f"📤 Uploading {output_path} to IPFS...")
    result = deployer.upload_folder(str(output_path), name)

    if result:
        print("\n🎉 Deployment successful!")
        print("📋 Details:")
        print(f"   - IPFS Hash: {result['IpfsHash']}")
        print(f"   - Size: {result['PinSize']} bytes")
        print(f"   - Timestamp: {result['Timestamp']}")
        print("\n🌐 Your blog is now available at:")
        print(f"   - https://gateway.pinata.cloud/ipfs/{result['IpfsHash']}")
        print(f"   - https://ipfs.io/ipfs/{result['IpfsHash']}")

        # save snapshot
        snapshot_manager = SnapshotManager()
        if name:
            result["name"] = name
        snapshot_manager.save_snapshot(result)

        # display snapshots
        snapshot_manager.display_snapshots()

        return True
    else:
        print("❌ Deployment failed!")
        return False


def list_deployments():
    """List recent deployments."""
    print("📋 Listing recent deployments...")

    # load environment variables
    load_environment()

    # get credentials
    api_key, api_secret, jwt = get_pinata_credentials()
    if not all([api_key, api_secret]):
        return False

    # initialize deployer
    deployer = PinataDeployer(api_key, api_secret, jwt)

    # list pins
    result = deployer.list_pins(limit=10)

    if result and "rows" in result:
        pins = result["rows"]
        if pins:
            print(f"\n📌 Found {len(pins)} recent pins:")
            for i, pin in enumerate(pins, 1):
                metadata = pin.get("metadata", {})
                name = metadata.get("name", "Unnamed")
                size = pin.get("size", 0)
                date = pin.get("date_pinned", "Unknown")
                ipfs_hash = pin.get("ipfs_pin_hash", "")

                print(f"\n{i}. {name}")
                print(f"   Hash: {ipfs_hash}")
                print(f"   Size: {size} bytes")
                print(f"   Date: {date}")
                print(f"   URL: https://gateway.pinata.cloud/ipfs/{ipfs_hash}")
        else:
            print("No pins found.")
    else:
        print("❌ Failed to list deployments.")
        return False

    return True


def show_snapshots():
    """Display current and previous deployment snapshots."""
    snapshot_manager = SnapshotManager()

    if not snapshot_manager.has_snapshots():
        print("📭 No deployment snapshots found.")
        print("Deploy your blog first to create snapshots.")
        return False

    snapshot_manager.display_snapshots()
    return True


def main():
    """Main deployment script."""
    parser = argparse.ArgumentParser(description="Deploy blog to IPFS via Pinata")
    parser.add_argument(
        "--output",
        "-o",
        default="output",
        help="Output directory to deploy (default: output)",
    )
    parser.add_argument("--name", "-n", help="Name for the deployment")
    parser.add_argument(
        "--list", "-l", action="store_true", help="List recent deployments"
    )
    parser.add_argument(
        "--snapshots", "-s", action="store_true", help="Show deployment snapshots"
    )

    args = parser.parse_args()

    if args.list:
        success = list_deployments()
    elif args.snapshots:
        success = show_snapshots()
    else:
        success = deploy_to_ipfs(args.output, args.name)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
