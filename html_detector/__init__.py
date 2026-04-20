from enum import Enum
from ._html_detector import refine_xpath, detect_fast


class TargetType(Enum):
    SEARCH_RESULT_SELECTOR = "search_result_selector"


def detect(
    html: str,
    refined: bool = True,
    target_type: TargetType = TargetType.SEARCH_RESULT_SELECTOR,
) -> list[tuple[float, str]]:
    """
    Calculates the CSS selectors and scores of search results within the specified HTML.

    Arguments:

        html (str): The HTML content to parse.

        refined (bool, optional): Whether to refine the scores of the detected CSS selectors. Default is True.

        target_type (TargetType, optional): The target type to scan. Default is TargetType.SEARCH_RESULT_SELECTOR.

    Return Value:

        list[tuple[float, str]]: A list of the scores and selector paths of the detected CSS selectors.

    Exceptions:

        NotImplementedError: If the specified target type is not supported.
    """
    if target_type != TargetType.SEARCH_RESULT_SELECTOR:
        raise NotImplementedError(f"Target type {target_type} is not supported.")
    candidates = detect_fast(html)
    if not refined:
        return candidates
    return refine_xpath(html, candidates)


__all__ = ["detect"]
