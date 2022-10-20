import pytest  # noqa
import shutil
import sys
import pathlib
import asyncio

import pygls.uris as uri
from pytest_lsp.client import Client
from pytest_lsp import ClientServerConfig
from pytest_lsp import make_client_server
from pytest_lsp import make_test_client

from src.lsp.custom.hub import Hub

ROOT_PATH = pathlib.Path(__file__).parent / "workspace"
SERVER_CMD = [sys.executable, "src/main.py", "--logfile", "./lsp-server-test.log"]


def lsp_client_server_for(id: str):
    root_uri = uri.from_fs_path(str(ROOT_PATH))

    cs_config = ClientServerConfig(
        server_command=SERVER_CMD,
        root_uri=root_uri,
        initialization_options={
            "configs": {
                id: {
                    "enabled": True,
                }
            }
        },
        client_factory=make_test_client,
    )

    cs = make_client_server(cs_config)
    return cs


# TODO: handle multiple executbales?
def default_config_test(id: str, executable: str, extension: str):
    """
    All the setup needed to test configs.
      * Starting/stopping a dedicated server in the background.
      * Checking for the external executbales the config depends on.
      * Creating the file that the LSP server works with.
    """

    sample_file_path = f"{id}.{extension}"

    def wrapper(func):
        reason = f"`{executable}` executable not found"

        @pytest.mark.skipif(not shutil.which(executable), reason=reason)
        @pytest.mark.asyncio
        async def inner(*args, **kwargs):
            cs = lsp_client_server_for(id)
            await cs.start()
            sample_file_path_full = ROOT_PATH / sample_file_path
            open(sample_file_path_full, "w")
            config = Hub.load_default_config()
            language_id = config["configs"][id]["language_id"]
            sample_uri = uri.from_fs_path(str(sample_file_path_full))
            sample_file = open(sample_file_path_full)
            cs.client.notify_did_open(sample_uri, language_id, sample_file.read())

            try:
                await func(
                    cs.client, sample_file_path_full, sample_uri, *args, **kwargs
                )
            finally:
                await cs.stop()

        return inner

    return wrapper


async def wait_for_diagnostic_count(client: Client, uri: str, count: int):
    timeout = 3
    pause = 0.01
    accumulated = 0.0
    while True:
        accumulated += pause
        if accumulated > timeout:
            actual = 0
            if client.diagnostics.get(uri) is not None:
                actual = len(client.diagnostics[uri])
            raise Exception(
                f"Diagnostic count ({actual}) didn't reach target "
                + f"of {count} in timeout of {timeout}."
            )
        await asyncio.sleep(pause)

        if client.diagnostics.get(uri) is None:
            continue
        elif len(client.diagnostics[uri]) != count:
            continue
        elif len(client.diagnostics[uri]) == count:
            return
