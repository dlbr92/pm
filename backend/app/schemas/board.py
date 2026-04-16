from pydantic import BaseModel, Field, field_validator, model_validator


class CardModel(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    details: str


class ColumnModel(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    cardIds: list[str] = Field(default_factory=list)


class BoardModel(BaseModel):
    columns: list[ColumnModel] = Field(default_factory=list)
    cards: dict[str, CardModel] = Field(default_factory=dict)

    @field_validator("columns")
    @classmethod
    def column_ids_must_be_unique(cls, columns: list[ColumnModel]) -> list[ColumnModel]:
        ids = [column.id for column in columns]
        if len(ids) != len(set(ids)):
            raise ValueError("Column ids must be unique.")
        return columns

    @field_validator("cards")
    @classmethod
    def card_keys_must_match_card_ids(
        cls, cards: dict[str, CardModel]
    ) -> dict[str, CardModel]:
        for key, card in cards.items():
            if key != card.id:
                raise ValueError("Card map key must match card.id.")
        return cards

    @model_validator(mode="after")
    def column_card_references_must_exist(self):
        all_card_ids = set(self.cards.keys())
        for column in self.columns:
            for card_id in column.cardIds:
                if card_id not in all_card_ids:
                    raise ValueError(
                        f"Column '{column.id}' references unknown card id '{card_id}'."
                    )
        return self
