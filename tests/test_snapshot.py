import json
from unittest.mock import patch

import pytest

from core.deployment.snapshot import SnapshotManager


@pytest.fixture
def snapshot_manager(tmp_path):
    return SnapshotManager(str(tmp_path))


class TestSnapshotManager:
    def test_init(self, snapshot_manager, tmp_path):
        assert snapshot_manager.snapshot_dir == tmp_path
        assert snapshot_manager.snapshot_file == tmp_path / "snapshots.json"

    def test_has_snapshots_false(self, snapshot_manager):
        assert snapshot_manager.has_snapshots() is False

    def test_has_snapshots_true(self, snapshot_manager):
        snapshot_manager.snapshot_file.touch()
        assert snapshot_manager.has_snapshots() is True

    def test_load_snapshots_empty(self, snapshot_manager):
        snapshots = snapshot_manager._load_snapshots()
        assert snapshots["current"] is None
        assert snapshots["previous"] is None

    def test_load_snapshots_exists(self, snapshot_manager):
        data = {"current": {"CID": "Qm1"}, "previous": None}
        snapshot_manager.snapshot_file.write_text(json.dumps(data))
        snapshots = snapshot_manager._load_snapshots()
        assert snapshots["current"]["CID"] == "Qm1"

    def test_load_snapshots_error(self, snapshot_manager):
        # mock open to raise exception
        with patch("builtins.open", side_effect=Exception("Read error")):
            # ensure file exists so it tries to open
            with patch("pathlib.Path.exists", return_value=True):
                snapshots = snapshot_manager._load_snapshots()
                assert snapshots["current"] is None

    def test_save_snapshot_new(self, snapshot_manager):
        deploy_data = {
            "IpfsHash": "QmNew",
            "ID": "id-123",
            "PinSize": 100,
            "Timestamp": "2023-01-01",
            "name": "Test Blog",
        }

        success = snapshot_manager.save_snapshot(deploy_data)
        assert success is True

        current = snapshot_manager.get_current_snapshot()
        assert current["CID"] == "QmNew"
        assert current["name"] == "Test Blog"
        assert snapshot_manager.get_previous_snapshot() is None

    def test_save_snapshot_rotation(self, snapshot_manager):
        # Setup initial state
        initial_data = {"current": {"CID": "QmOld"}, "previous": None}
        snapshot_manager.snapshot_file.write_text(json.dumps(initial_data))

        deploy_data = {"IpfsHash": "QmNew"}
        snapshot_manager.save_snapshot(deploy_data)

        current = snapshot_manager.get_current_snapshot()
        previous = snapshot_manager.get_previous_snapshot()

        assert current["CID"] == "QmNew"
        assert previous["CID"] == "QmOld"

    def test_save_snapshot_error(self, snapshot_manager):
        with patch("builtins.open", side_effect=Exception("Write error")):
            success = snapshot_manager.save_snapshot({})
            assert success is False

    def test_display_snapshots(self, snapshot_manager, capsys):
        # Case 1: No snapshots
        snapshot_manager.display_snapshots()
        captured = capsys.readouterr()
        assert "CURRENT DEPLOYMENT: None" in captured.out

        # Case 2: With snapshots
        data = {
            "current": {
                "CID": "QmCurr",
                "pin_size": 100,
                "deployed_at": "now",
                "gateway_url": "url",
                "ipfs_url": "ipfs",
            },
            "previous": {
                "CID": "QmPrev",
                "pin_size": 100,
                "deployed_at": "before",
                "gateway_url": "url",
                "ipfs_url": "ipfs",
            },
        }
        snapshot_manager.snapshot_file.write_text(json.dumps(data))

        snapshot_manager.display_snapshots()
        captured = capsys.readouterr()
        assert "QmCurr" in captured.out
        assert "QmPrev" in captured.out
