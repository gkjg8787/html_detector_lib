from enum import Enum

from ._html_detector import refine_xpath, detect_fast
from .data import EXTRACT_SORT_RULE, EXTRACT_CATEGORY_RULE
from .parser import get_match_select_option

__all__ = [
    "detect",
    "TargetType",
]


class TargetType(Enum):
    SEARCH_RESULT_SELECTOR = "search_result_selector"
    CATEGORY_SELECT_TAG = "category_select_tag"
    SORT_SELECT_TAG = "sort_select_tag"


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
    if not isinstance(target_type, TargetType) or target_type not in TargetType:
        raise NotImplementedError(f"Target type {target_type} is not supported.")
    match target_type:
        case TargetType.SEARCH_RESULT_SELECTOR:
            candidates = detect_fast(html)
            if not refined:
                return candidates
            return refine_xpath(html, candidates)
        case TargetType.CATEGORY_SELECT_TAG:
            return get_match_select_option(html, EXTRACT_CATEGORY_RULE)
        case TargetType.SORT_SELECT_TAG:
            return get_match_select_option(html, EXTRACT_SORT_RULE)
