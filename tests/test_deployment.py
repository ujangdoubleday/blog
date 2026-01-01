from unittest.mock import MagicMock, patch

import pytest

from core.deployment.cloudflare import CloudflareManager
from core.deployment.pinata import PinataDeployer


# CloudflareManager Tests
@pytest.fixture
def cloudflare_manager():
    return CloudflareManager("user@example.com", "api_key", "zone_id", "example.com")


class TestCloudflareManager:
    def test_init(self, cloudflare_manager):
        assert cloudflare_manager.email == "user@example.com"
        assert cloudflare_manager.base_url == "https://api.cloudflare.com/client/v4"

    @patch("requests.patch")
    def test_update_dnslink_success(self, mock_patch, cloudflare_manager):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_patch.return_value = mock_response

        result = cloudflare_manager.update_dnslink("QmCID", "deploy-1")
        assert result["success"] is True
        mock_patch.assert_called_once()

    @patch("requests.patch")
    def test_update_dnslink_pending(self, mock_patch, cloudflare_manager):
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.json.return_value = {"result": "pending"}
        mock_patch.return_value = mock_response

        result = cloudflare_manager.update_dnslink("QmCID")
        assert result["_status_code"] == 202

    @patch("requests.patch")
    def test_update_dnslink_failure(self, mock_patch, cloudflare_manager):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Error"
        mock_patch.return_value = mock_response

        result = cloudflare_manager.update_dnslink("QmTest")
        assert result is None

    def test_update_dnslink_exception(self, cloudflare_manager):
        with patch("requests.patch", side_effect=Exception("API Error")):
            result = cloudflare_manager.update_dnslink("QmTest")
            assert result is None

    @patch("requests.get")
    def test_check_connection_success(self, mock_get, cloudflare_manager):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        assert cloudflare_manager.test_connection() is True

    @patch("requests.get")
    def test_check_connection_failure(self, mock_get, cloudflare_manager):
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response

        assert cloudflare_manager.test_connection() is False

    def test_check_connection_exception(self, cloudflare_manager):
        with patch("requests.get", side_effect=Exception("Net Error")):
            assert cloudflare_manager.test_connection() is False


# PinataDeployer Tests
@pytest.fixture
def pinata_deployer():
    with patch("core.deployment.pinata.PinataPy"):
        deployer = PinataDeployer("key", "secret", "jwt")
        deployer.pinata = MagicMock()
        return deployer


class TestPinataDeployer:
    def test_init(self):
        with patch("core.deployment.pinata.PinataPy"):
            deployer = PinataDeployer("k", "s", "j")
            assert deployer.jwt == "j"

    def test_test_authentication_success(self, pinata_deployer):
        pinata_deployer.pinata.pin_list.return_value = {}
        assert pinata_deployer.test_authentication() is True

    def test_test_authentication_failure(self, pinata_deployer):
        pinata_deployer.pinata.pin_list.side_effect = Exception("Auth failed")
        assert pinata_deployer.test_authentication() is False

    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.is_dir", return_value=True)
    def test_upload_folder_success(self, mock_isdir, mock_exists, pinata_deployer):
        pinata_deployer.pinata.pin_file_to_ipfs.return_value = {"IpfsHash": "QmTest"}
        result = pinata_deployer.upload_folder("/path/to/folder")
        assert result["IpfsHash"] == "QmTest"

    @patch("pathlib.Path.exists", return_value=False)
    def test_upload_folder_not_exist(self, mock_exists, pinata_deployer):
        result = pinata_deployer.upload_folder("/bad/path")
        assert result is None

    def test_list_pins(self, pinata_deployer):
        pinata_deployer.pinata.pin_list.return_value = {"rows": []}
        result = pinata_deployer.list_pins()
        assert "rows" in result

    def test_unpin_file_success(self, pinata_deployer):
        pinata_deployer.pinata.remove_pin_from_ipfs.return_value = {}
        assert pinata_deployer.unpin_file("QmCID") is True

    @patch("requests.delete")
    def test_delete_file_by_id_success(self, mock_delete, pinata_deployer):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_delete.return_value = mock_response
        assert pinata_deployer.delete_file_by_id("file_id") is True

    def test_delete_file_by_id_no_jwt(self, pinata_deployer):
        pinata_deployer.jwt = None
        assert pinata_deployer.delete_file_by_id("file_id") is False

    @patch("requests.delete")
    def test_delete_file_by_id_failure(self, mock_delete, pinata_deployer):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Error"
        mock_delete.return_value = mock_response
        assert pinata_deployer.delete_file_by_id("file_id") is False

    def test_unpin_file_failure(self, pinata_deployer):
        pinata_deployer.pinata.remove_pin_from_ipfs.side_effect = Exception("Error")
        assert pinata_deployer.unpin_file("QmCID") is False

    def test_list_pins_failure(self, pinata_deployer):
        pinata_deployer.pinata.pin_list.side_effect = Exception("Error")
        result = pinata_deployer.list_pins()
        assert result is None
