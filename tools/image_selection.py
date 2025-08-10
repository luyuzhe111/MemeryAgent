from agents import function_tool


def _select_local_image_impl(meme: str) -> str:
    return f"memes/{meme}/default.jpg"


@function_tool
def select_local_image(meme: str) -> str:
    return _select_local_image_impl(meme)
