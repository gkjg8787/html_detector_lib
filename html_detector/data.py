from .models import SelectExtractionConfig, CategoryCriteria


def to_lower_keys(obj):
    if isinstance(obj, dict):
        # 新しい辞書を構築し、各キーを小文字に変換
        # 値が辞書の場合は再帰的にto_lower_keysを適用
        return {
            k.lower() if isinstance(k, str) else k: to_lower_keys(v)
            for k, v in obj.items()
        }
    elif isinstance(obj, list):
        # リストの場合は、各要素に対してto_lower_keysを適用
        return [to_lower_keys(elem) for elem in obj]
    else:
        # 辞書でもリストでもない場合はそのまま返す
        return obj


CATEGORY_PATTERN = {  # Required for rule
    "match_threshold": 2,  # Number of matching settings
    "rules": [
        {
            "match_type": "exact",
            "match_threshold": 1,
            "patterns": [
                "すべての商品",
                "全商品",
                "全ての商品",
                "全てのカテゴリ",
                "すべてのカテゴリ",
                "全カテゴリ",
                "すべてのジャンル",
                "全てのジャンル",
                "全ジャンル",
            ],
        },
        {
            "match_type": "contains",
            "match_threshold": 1,
            "patterns": [
                "パソコン",
                "周辺機器",
                "食品",
                "ドリンク",
                "酒",
                "菓子",
                "家電",
                "スマホ",
                "スマートフォン",
                "タブレット",
                "カメラ",
                "テレビ",
                "オーディオ",
                "楽器",
                "書籍",
                "医薬品",
                "エアコン",
                "ゲーム",
                "おもちゃ",
                "ホビー",
                "日用品",
                "家具",
                "インテリア",
                "寝具",
                "ファッション",
                "アクセサリー",
                "雑貨",
                "スポーツ",
                "アウトドア",
                "車",
                "化粧品",
                "美容",
                "ペット",
            ],
        },
    ],
}
SORT_PATTERN = {
    "match_threshold": 1,
    "rules": [
        {
            "match_type": "contains",
            "match_threshold": 1,
            "patterns": [
                "安い順",
                "人気順",
                "おすすめ順",
                "オススメ順",
                "新着順",
                "発売日",
                "北海道",
                "東京",
            ],
        },
    ],
}

EXTRACT_CATEGORY_RULE = SelectExtractionConfig(
    method="rule",
    positive_criteria=CategoryCriteria(**to_lower_keys(CATEGORY_PATTERN)),
    negative_criteria=CategoryCriteria(**to_lower_keys(SORT_PATTERN)),
)
EXTRACT_SORT_RULE = SelectExtractionConfig(
    method="rule",
    positive_criteria=CategoryCriteria(**to_lower_keys(SORT_PATTERN)),
    negative_criteria=CategoryCriteria(**to_lower_keys(CATEGORY_PATTERN)),
)
