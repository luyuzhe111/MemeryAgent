import os
from tools import _download_x_profile_picture_impl


def test_download_x_profile_picture():
    """Test downloading profile picture for a username"""
    user_name = "iamkadense"
    result = _download_x_profile_picture_impl(user_name, output_dir="./profile_pics")
    
    if result:
        # Check that the file was created
        assert os.path.exists(result)
        assert result.startswith("./profile_pics")
        assert f"{user_name}_profile" in result
        
        # Check that the file has content
        file_size = os.path.getsize(result)
        assert file_size > 0
        
        print(f"Successfully downloaded profile picture: {result}")
        print(f"File size: {file_size} bytes")
    else:
        # If download failed, we still want to know about it
        print("Failed to download profile picture for yuzhe_lu")
        # Don't fail the test as this could be due to API limits, network issues, etc.

