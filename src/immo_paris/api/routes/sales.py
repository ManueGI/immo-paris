from typing import Annotated

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException

from immo_paris.core.config import Settings, get_settings
from immo_paris.schemas.sale import Sale

router = APIRouter(prefix="/api/v1/sales", tags=["sales"])


@router.get("/sample", response_model=list[Sale])
def sales_sample(settings: Annotated[Settings, Depends(get_settings)]) -> list[Sale]:
    if not settings.sample_csv.exists():
        raise HTTPException(
            status_code=503,
            detail=f"Missing data ({settings.sample_csv}). Run first: uv run immo-ingest",
        )
    df = pd.read_csv(
        settings.sample_csv,
        nrows=10,
        dtype={"mutation_id": "string", "postal_code": "string"},
    )
    # NaN is not JSON-serializable: replace it with None
    records = df.astype(object).where(df.notna(), None).to_dict(orient="records")
    return [Sale.model_validate(record) for record in records]
