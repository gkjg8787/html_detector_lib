from typing import Literal, Optional

from pydantic import BaseModel, Field


# -------- Schema ----------
class OptionData(BaseModel):
    value: Optional[str] = Field(
        description="Value attribute of the option", max_length=200
    )
    text: str = Field(description="Text content of the option", max_length=200)


class SelectData(BaseModel):
    id: Optional[str]
    name: Optional[str]
    class_list: list[str]
    options: list[OptionData]
    visible: bool = True


class CustomSelectData(BaseModel):
    # 外側のコンテナ（よく div や span になる）
    container_tag: str = Field(description="div, ul, span などの親タグ名")
    id: Optional[str]
    class_list: list[str]

    selector: Optional[str] = Field(
        None, description="この要素を一意に特定するための CSS セレクタ"
    )
    # ユーザーがクリックする「表示中の値」の部分
    trigger_text: Optional[str] = Field(
        None, description="クリックしてリストを開くための要素のセレクタやテキスト"
    )

    # 展開される選択肢のリスト
    # 既存の OptionData を再利用しつつ、タグ情報を追加
    options: list[OptionData]

    # 実体（隠れている本物のselect）との紐付け
    linked_select_id: Optional[str] = Field(
        None, description="display:none になっている本物の select の ID"
    )

    # 動的要素特有の状態
    is_expanded: bool = Field(False, description="ドロップダウンが開いているかどうか")

    # 選択肢が a タグや li タグなどの場合、その種類を保持
    item_tag_type: str = Field("li", description="li, a, div など選択肢のタグ種類")
    is_hidden: bool = Field(True, description="現在表示されているかどうか")
    is_dynamic: bool = Field(False, description="動的要素かどうか")


# -------- Rule Model ----------
class OptionMatchRule(BaseModel):
    match_type: Literal["exact", "contains"] = "exact"
    match_threshold: int = 1
    patterns: list[str] = Field(default_factory=list)


class CategoryCriteria(BaseModel):
    match_threshold: int = 1
    rules: list[OptionMatchRule] = Field(default_factory=list)


class SelectExtractionConfig(BaseModel):
    method: Literal["rule", "ai"] = Field(
        default="rule",
        description="Extraction method: 'rule' for pattern matching, 'ai' for LLM.",
    )
    positive_criteria: CategoryCriteria | None = Field(
        default=None,
        description="Rules to identify valid options.",
    )
    negative_criteria: CategoryCriteria | None = Field(
        default=None,
        description="Rules to exclude invalid options.",
    )
