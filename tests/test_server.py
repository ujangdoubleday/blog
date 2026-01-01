from unittest.mock import MagicMock, patch

import pytest

from core.dev.server import DevServer


@pytest.fixture
def mock_config(tmp_path):
    return {"dev": {"port": 8080}, "build": {"output_dir": str(tmp_path)}}


@pytest.fixture
def server(mock_config):
    return DevServer(mock_config)


class TestDevServer:
    def test_init(self, server):
        assert server.host == "0.0.0.0"
        assert server.port == 8080

    def test_get_local_ip(self, server):
        with patch("socket.socket") as mock_socket:
            mock_socket_instance = MagicMock()
            mock_socket.return_value = mock_socket_instance
            mock_socket_instance.getsockname.return_value = ["192.168.1.5"]

            ip = server._get_local_ip()
            assert ip == "192.168.1.5"

    def test_get_local_ip_failure(self, server):
        with patch("socket.socket") as mock_socket:
            mock_socket.side_effect = Exception("Error")
            ip = server._get_local_ip()
            assert ip == ""

    @patch("socketserver.TCPServer")
    @patch("os.chdir")
    def test_serve(self, mock_chdir, mock_tcp_server, server):
        mock_httpd = MagicMock()
        mock_tcp_server.return_value.__enter__.return_value = mock_httpd

        # We need to prevent the loop from running forever
        # mock serve_forever to just return immediately
        mock_httpd.serve_forever.return_value = None

        with patch("threading.Thread"):  # prevent browser opening
            server.serve()

        mock_chdir.assert_called_with(server.config["build"]["output_dir"])
        mock_httpd.serve_forever.assert_called_once()

    def test_build_and_serve(self, server):
        mock_generator = MagicMock()
        with patch.object(server, "serve") as mock_serve:
            server.build_and_serve(mock_generator)

            mock_generator.build.assert_called_once()
            mock_serve.assert_called_once()

    @patch("socketserver.TCPServer")
    @patch("os.chdir")
    def test_serve_with_port(self, mock_chdir, mock_tcp, server):
        # Prevent actual serve
        mock_tcp.return_value.__enter__.return_value.serve_forever.return_value = None
        with patch("threading.Thread"):
            server.serve(port=9000)
        assert server.port == 9000

    @patch("socketserver.TCPServer")
    @patch("os.chdir")
    def test_serve_interrupt(self, mock_chdir, mock_tcp, server):
        mock_httpd = MagicMock()
        mock_httpd.serve_forever.side_effect = KeyboardInterrupt
        mock_tcp.return_value.__enter__.return_value = mock_httpd

        with patch("threading.Thread"):
            # Should catch interrupt and not raise
            server.serve()

    @patch("socketserver.TCPServer")
    @patch("os.chdir")
    def test_serve_opens_browser(self, mock_chdir, mock_tcp, server):
        mock_tcp.return_value.__enter__.return_value.serve_forever.return_value = None

        with patch("threading.Thread") as mock_thread:
            with patch("webbrowser.open") as mock_web:
                with patch("time.sleep"):
                    server.serve()

                    # Get the target function passed to Thread
                    # kwargs usually, or check call_args
                    # Thread(target=open_browser, daemon=True)
                    args, kwargs = mock_thread.call_args
                    target = kwargs.get("target")
                    # Execute it
                    target()

                    mock_web.assert_called()
