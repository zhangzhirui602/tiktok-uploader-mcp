"""
Tests for the TikTokUploader class
"""

import os
from unittest.mock import MagicMock, patch

from tiktok_uploader.upload import TikTokUploader

FILENAME = "test.mp4"


def setup_function() -> None:
    """
    Creates a dummy file
    """
    with open(FILENAME, "w", encoding="utf-8") as file:
        file.write("test")


def teardown_function() -> None:
    """
    Deletes the dummy file
    """
    if os.path.exists(FILENAME):
        os.remove(FILENAME)


@patch("tiktok_uploader.upload.get_browser")
@patch("tiktok_uploader.auth.AuthBackend.authenticate_agent")
@patch("tiktok_uploader.upload.complete_upload_form")
def test_tiktok_uploader_lazy_loading(
    mock_complete_upload, mock_auth, mock_browser
) -> None:
    """
    Tests that the browser is not created until upload is called
    """
    mock_page = MagicMock()
    mock_browser.return_value = mock_page
    mock_auth.return_value = mock_page

    # Create uploader
    uploader = TikTokUploader(sessionid="test_session")

    # Browser should not be called yet
    mock_browser.assert_not_called()

    # Upload video
    uploader.upload_video(FILENAME, description="Test")

    # Now browser should be called
    mock_browser.assert_called_once()
    mock_auth.assert_called_once()
    mock_complete_upload.assert_called_once()


@patch("tiktok_uploader.upload.get_browser")
@patch("tiktok_uploader.auth.AuthBackend.authenticate_agent")
@patch("tiktok_uploader.upload.complete_upload_form")
def test_tiktok_uploader_reuse_browser(
    mock_complete_upload, mock_auth, mock_browser
) -> None:
    """
    Tests that the browser is reused for multiple uploads
    """
    mock_page = MagicMock()
    mock_browser.return_value = mock_page
    mock_auth.return_value = mock_page

    uploader = TikTokUploader(sessionid="test_session")

    # First upload
    uploader.upload_video(FILENAME, description="Test 1")

    # Second upload
    uploader.upload_video(FILENAME, description="Test 2")

    # Browser should be called only once
    mock_browser.assert_called_once()
    # Auth should be called only once
    mock_auth.assert_called_once()

    # Complete upload should be called twice
    assert mock_complete_upload.call_count == 2


@patch("tiktok_uploader.upload.get_persistent_browser")
def test_profile_session_expired_login_redirect(mock_get_persistent) -> None:
    """
    Tests that a RuntimeError is raised when the profile session has expired
    and TikTok redirects to the login page.
    """
    mock_context = MagicMock()
    mock_page = MagicMock()
    mock_get_persistent.return_value = (mock_context, mock_page)

    mock_context.cookies.return_value = [{"name": "sessionid", "value": "abc"}]
    mock_page.url = "https://www.tiktok.com/login/phone-or-email/phone"

    uploader = TikTokUploader(profile_dir="profiles/test_account")

    import pytest
    with pytest.raises(RuntimeError, match="session has expired"):
        _ = uploader.page


@patch("tiktok_uploader.upload.get_persistent_browser")
def test_profile_session_expired_explore_redirect(mock_get_persistent) -> None:
    """
    Tests that a RuntimeError is raised when TikTok redirects to the explore page
    (another sign of session expiry).
    """
    mock_context = MagicMock()
    mock_page = MagicMock()
    mock_get_persistent.return_value = (mock_context, mock_page)

    mock_context.cookies.return_value = [{"name": "sessionid", "value": "abc"}]
    mock_page.url = "https://www.tiktok.com/explore"

    uploader = TikTokUploader(profile_dir="profiles/test_account")

    import pytest
    with pytest.raises(RuntimeError, match="session has expired"):
        _ = uploader.page


@patch("tiktok_uploader.upload.get_persistent_browser")
def test_profile_no_sessionid_cookie(mock_get_persistent) -> None:
    """
    Tests that a RuntimeError is raised when the profile has no sessionid cookie at all
    (profile was never logged in).
    """
    mock_context = MagicMock()
    mock_page = MagicMock()
    mock_get_persistent.return_value = (mock_context, mock_page)

    mock_context.cookies.return_value = []
    mock_page.url = "https://www.tiktok.com/"

    uploader = TikTokUploader(profile_dir="profiles/test_account")

    import pytest
    with pytest.raises(RuntimeError, match="not logged in"):
        _ = uploader.page
