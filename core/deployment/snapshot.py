"""
Snapshot manager for IPFS deployments.
Maintains current and previous deployment snapshots.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


class SnapshotManager:
    """Manage deployment snapshots with rotation (current -> previous)."""

    def __init__(self, snapshot_dir: str = "."):
        """
        Initialize snapshot manager.

        Args:
            snapshot_dir: Directory to store snapshot files (default: root)
        """
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_file = self.snapshot_dir / "snapshots.json"

    def save_snapshot(self, deployment_data: Dict[str, Any]) -> bool:
        """
        Save new deployment snapshot and rotate previous.

        Process:
        1. Load existing snapshots
        2. Move current to previous
        3. Save new deployment as current

        Args:
            deployment_data: Deployment information from Pinata

        Returns:
            True if successful, False otherwise
        """
        try:
            # load existing snapshots
            snapshots = self._load_snapshots()

            # prepare new snapshot data
            cid = deployment_data.get("IpfsHash", "")  # v1 CID
            file_id = deployment_data.get("ID", "")  # Pinata file ID (UUID)

            new_snapshot = {
                "CID": cid,
                "ID": file_id,
                "pin_size": deployment_data.get("PinSize", 0),
                "timestamp": deployment_data.get("Timestamp", ""),
                "deployed_at": datetime.now().isoformat(),
                "gateway_url": f"https://{cid}.ipfs.dweb.link",
                "ipfs_url": f"ipfs://{cid}",
                "name": deployment_data.get("name", "Blog Deployment"),
            }

            # rotate: current -> previous
            if snapshots.get("current"):
                snapshots["previous"] = snapshots["current"]
                print("📦 Rotated current snapshot to previous")

            # save new current
            snapshots["current"] = new_snapshot

            # write to file
            with open(self.snapshot_file, "w", encoding="utf-8") as f:
                json.dump(snapshots, f, indent=2, ensure_ascii=False)

            print("✅ Saved snapshot to snapshots.json")
            return True

        except Exception as e:
            print(f"❌ Error saving snapshot: {e}")
            return False

    def _load_snapshots(self) -> Dict[str, Any]:
        """Load snapshots from file."""
        if not self.snapshot_file.exists():
            return {"current": None, "previous": None}

        try:
            with open(self.snapshot_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error reading snapshots: {e}")
            return {"current": None, "previous": None}

    def get_current_snapshot(self) -> Optional[Dict[str, Any]]:
        """
        Get current deployment snapshot.

        Returns:
            Current snapshot data or None if not exists
        """
        snapshots = self._load_snapshots()
        return snapshots.get("current")

    def get_previous_snapshot(self) -> Optional[Dict[str, Any]]:
        """
        Get previous deployment snapshot.

        Returns:
            Previous snapshot data or None if not exists
        """
        snapshots = self._load_snapshots()
        return snapshots.get("previous")

    def display_snapshots(self):
        """Display current and previous snapshots in a formatted way."""
        print("\n" + "=" * 70)
        print("📸 DEPLOYMENT SNAPSHOTS")
        print("=" * 70)

        # current snapshot
        current = self.get_current_snapshot()
        if current:
            print("\n🟢 CURRENT DEPLOYMENT:")
            # support both old and new field names
            cid = current.get("CID") or current.get("ipfs_hash", "")
            file_id = current.get("ID") or current.get("file_id", "")

            print(f"   CID         : {cid}")
            if file_id:
                print(f"   ID          : {file_id}")
            print(f"   Size        : {current['pin_size']:,} bytes")
            print(f"   Deployed At : {current['deployed_at']}")
            print(f"   Gateway URL : {current['gateway_url']}")
            print(f"   IPFS URL    : {current['ipfs_url']}")
        else:
            print("\n🟢 CURRENT DEPLOYMENT: None")

        # previous snapshot
        previous = self.get_previous_snapshot()
        if previous:
            print("\n🔵 PREVIOUS DEPLOYMENT:")
            # support both old and new field names
            cid = previous.get("CID") or previous.get("ipfs_hash", "")
            file_id = previous.get("ID") or previous.get("file_id", "")

            print(f"   CID         : {cid}")
            if file_id:
                print(f"   ID          : {file_id}")
            print(f"   Size        : {previous['pin_size']:,} bytes")
            print(f"   Deployed At : {previous['deployed_at']}")
            print(f"   Gateway URL : {previous['gateway_url']}")
            print(f"   IPFS URL    : {previous['ipfs_url']}")
        else:
            print("\n🔵 PREVIOUS DEPLOYMENT: None")

        print("\n" + "=" * 70)

    def has_snapshots(self) -> bool:
        """Check if any snapshots exist."""
        return self.snapshot_file.exists()
