"""The API key must stay in a per-instance fal client, never in os.environ
(writing FAL_KEY at node init poisons sibling fal nodes). No network calls."""
import configparser
import os
from io import BytesIO

import torch
from PIL import Image

import iclight_fal_node as mod


class FakeSyncClient:
    def __init__(self, key=None):
        self.key, self.calls = key, []

    def upload_file(self, path):
        self.calls.append(("upload_file", path))
        return "https://fal.test/in.png"

    def subscribe(self, model_id, arguments, **_kw):
        self.calls.append(("subscribe", model_id, arguments))
        return {"images": [{"url": "https://fal.test/out.png"}]}


class FakeResponse:
    status_code = 200

    def __init__(self):
        buf = BytesIO()
        Image.new("RGB", (8, 8), (200, 100, 50)).save(buf, format="PNG")
        self.content = buf.getvalue()


def test_key_scoped_to_client_not_environ(monkeypatch, tmp_path):
    monkeypatch.delenv("FAL_KEY", raising=False)
    monkeypatch.setattr(mod.fal_client, "SyncClient", FakeSyncClient)
    monkeypatch.setattr(mod.requests, "get", lambda url: FakeResponse())
    cfg = configparser.ConfigParser()
    cfg["falai"] = {"api_key": " config-key "}
    monkeypatch.setattr(mod.IcLightV2Node, "_load_config", lambda self: cfg)

    node = mod.IcLightV2Node()
    node.output_dir = str(tmp_path)
    (out,) = node.relight(torch.rand(1, 8, 8, 3), "beach", "", 28, 5.0, -1, "None",
                          False, 0.98, 0.95, 0.5, 1, 1.0, "png")

    assert "FAL_KEY" not in os.environ
    assert node._fal.key == "config-key"
    assert [c[0] for c in node._fal.calls] == ["upload_file", "subscribe"]
    assert node._fal.calls[1][2]["image_url"] == "https://fal.test/in.png"
    assert out.shape == (1, 8, 8, 3)


def test_env_key_wins_over_config(monkeypatch):
    monkeypatch.setenv("FAL_KEY", "env-key")
    monkeypatch.setattr(mod.fal_client, "SyncClient", FakeSyncClient)
    assert mod.IcLightV2Node()._fal.key == "env-key"
