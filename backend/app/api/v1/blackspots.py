"""
Known Bengaluru black spot endpoints.
GET /blackspots        — list all
GET /blackspots/{id}   — single spot detail
"""
from fastapi import APIRouter, Query, HTTPException
from app.core.blackspot_store import get_all_blackspots, get_blackspot_by_id
from app.schemas.blackspot import BlackSpot, BlackSpotList

router = APIRouter(prefix="/blackspots", tags=["Black Spots"])

VALID_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


@router.get(
    "",
    response_model=BlackSpotList,
    summary="Get all known black spots",
    description="Returns all known Bengaluru black spots with risk metadata. "
                "Used by the map page to render hotspot markers on load.",
)
async def list_blackspots(
    severity: str | None = Query(None, description="Filter: LOW|MEDIUM|HIGH|CRITICAL"),
    limit:    int        = Query(50, ge=1, le=200),
):
    spots = get_all_blackspots()

    if severity:
        sev = severity.upper()
        if sev not in VALID_SEVERITIES:
            raise HTTPException(
                status_code=422,
                detail=f"severity must be one of {VALID_SEVERITIES}",
            )
        spots = [s for s in spots if s["severity"] == sev]

    return BlackSpotList(spots=spots[:limit], total=len(spots))


@router.get(
    "/{spot_id}",
    response_model=BlackSpot,
    summary="Get single black spot details",
)
async def get_blackspot(spot_id: str):
    spot = get_blackspot_by_id(spot_id)
    if not spot:
        raise HTTPException(
            status_code=404,
            detail=f"Black spot '{spot_id}' not found",
        )
    return spot
