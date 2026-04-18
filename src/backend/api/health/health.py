from fastapi import APIRouter, Depends, HTTPException, status
from models.health import HealthPublic
from db.session import get_session
from sqlmodel import Session, select
from models.health import Health

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=HealthPublic)
async def health(session: Session = Depends(get_session)):
    try:
        # select the latest health record
        result = session.exec(select(Health).order_by(Health.time.desc()).limit(1)).first()
        if result:
            return result
        elif result is None or result.status != "ok":
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service unavailable")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Error: {e}")