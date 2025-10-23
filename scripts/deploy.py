#!/usr/bin/env python3
"""
Deployment script for uploading blog to IPFS via Pinata.
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from cid import make_cid

# add parent directory to path to import core modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.deployment.pinata import PinataDeployer  # noqa: E402
from core.deployment.snapshot import SnapshotManager  # noqa: E402
from core.deployment.cloudflare import CloudflareManager  # noqa: E402


def load_environment():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent.parent / ".env"

    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment from {env_path}")
    else:
        print(f"⚠️  No .env file found at {env_path}")
        print(
            "Make sure to set PINATA_API_KEY, PINATA_SECRET_API_KEY, "
            "and PINATA_JWT environment variables"
        )


def get_pinata_credentials():
    """Get Pinata credentials from environment variables."""
    api_key = os.getenv("PINATA_API_KEY")
    api_secret = os.getenv("PINATA_SECRET_API_KEY")
    jwt = os.getenv("PINATA_JWT")  # required for file deletion

    if not all([api_key, api_secret]):
        missing = []
        if not api_key:
            missing.append("PINATA_API_KEY")
        if not api_secret:
            missing.append("PINATA_SECRET_API_KEY")

        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        print("Please set these variables in your .env file")
        return None, None, None

    return api_key, api_secret, jwt


def get_cloudflare_config():
    """
    Get Cloudflare configuration from environment variables.

    Returns:
        Tuple of (enabled, email, api_key, zone_id, hostname)
    """
    enabled = os.getenv("CLOUDFLARE", "false").lower() == "true"

    if not enabled:
        return False, None, None, None, None

    email = os.getenv("CLOUDFLARE_EMAIL")
    api_key = os.getenv("CLOUDFLARE_API_KEY")
    zone_id = os.getenv("CLOUDFLARE_ZONE_ID")
    hostname = os.getenv("CLOUDFLARE_HOSTNAME")

    if not all([email, api_key, zone_id, hostname]):
        print("⚠️  Cloudflare is enabled but missing required credentials")
        print(
            "Required: CLOUDFLARE_EMAIL, CLOUDFLARE_API_KEY, "
            "CLOUDFLARE_ZONE_ID, CLOUDFLARE_HOSTNAME"
        )
        return False, None, None, None, None

    return True, email, api_key, zone_id, hostname


def convert_cid_to_v1(cid_v0: str) -> str:
    """
    Convert CIDv0 to CIDv1 with base32 encoding.

    Args:
        cid_v0: CIDv0 string (starts with Qm)

    Returns:
        CIDv1 string (starts with baf)
    """
    try:
        cid = make_cid(cid_v0)
        # convert to v1 and encode in base32
        cid_v1 = cid.to_v1()
        return cid_v1.encode("base32").decode("utf-8")
    except Exception:
        # silent fallback to v0
        return cid_v0


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
        ipfs_hash_v0 = result["IpfsHash"]

        # convert CID to v1 (silent)
        ipfs_hash_v1 = convert_cid_to_v1(ipfs_hash_v0)

        # get previous snapshot BEFORE rotation
        snapshot_manager = SnapshotManager()
        previous_snapshot = snapshot_manager.get_previous_snapshot()

        # delete previous deployment from Pinata BEFORE rotation
        # so we delete the old "previous" before it gets overwritten
        if previous_snapshot:
            previous_id = previous_snapshot.get("ID") or previous_snapshot.get(
                "file_id"
            )
            if previous_id:
                print(f"🗑️  Deleting old deployment (ID: {previous_id})...")
                if deployer.delete_file_by_id(previous_id):
                    print("✅ Old deployment deleted from Pinata")
                # if deletion fails, warning is already printed by delete_file_by_id

        # NOW save snapshot (which will rotate current -> previous)
        result["IpfsHash"] = ipfs_hash_v1  # use v1 in snapshot
        if name:
            result["name"] = name
        snapshot_manager.save_snapshot(result)

        # update Cloudflare DNS if enabled
        (
            cf_enabled,
            cf_email,
            cf_api_key,
            cf_zone_id,
            cf_hostname,
        ) = get_cloudflare_config()

        if cf_enabled:
            print("🌐 Updating Cloudflare DNSLink...")
            cf_manager = CloudflareManager(
                cf_email, cf_api_key, cf_zone_id, cf_hostname
            )

            # use deployment ID as description
            deployment_id = result.get("ID", "")
            cf_result = cf_manager.update_dnslink(ipfs_hash_v1, deployment_id)

            if cf_result:
                # check if pending (status 202)
                if cf_result.get("_status_code") == 202:
                    print("⏳ Cloudflare DNSLink update pending")
                    print("   DNS propagation will complete in 1-2 minutes")
                else:
                    print(f"✅ Cloudflare DNSLink updated to /ipfs/{ipfs_hash_v1}")
            # if update fails, warning is already printed by update_dnslink

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
