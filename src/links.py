from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from src.database import get_db
from src.models import User
from src.schemas import LinkCreate, LinkResponse, LinkUpdate, LinkStats
from src.utils import generate_short_code, handle_expiration
from src.security import get_current_user, get_optional_user
from src.schemas import ArchivedLinkStats
from src.models import Link, ArchivedLink
import json
import hashlib
from src.redis_client import redis_client, DEFAULT_EXPIRE


def cache_key_redirect(short_code: str) -> str:
    return f"redirect:{short_code}"


def cache_key_stats(short_code: str) -> str:
    return f"stats:{short_code}"


def cache_key_search(original_url: str) -> str:
    url_hash = hashlib.md5(original_url.encode()).hexdigest()
    return f"search:{url_hash}"


def check_link_ownership(link: Link, user: Optional[User]):
    if link.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anonymous links cannot be modified"
        )
    if user is None or link.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this link"
        )


router = APIRouter(prefix="/links")

@router.post("/shorten", response_model=LinkResponse)
def create_short_link(
    link: LinkCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)  
):

    expires_at = handle_expiration(link.expires_at)

    if link.custom_alias:
        existing = db.query(Link).filter(
            (Link.short_code == link.custom_alias) |
            (Link.custom_alias == link.custom_alias)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Alias already exists"
            )
        short_code = link.custom_alias
    else:
        short_code = generate_short_code()
        while db.query(Link).filter_by(short_code=short_code).first():
            short_code = generate_short_code()

    db_link = Link(
        original_url=str(link.original_url),
        short_code=short_code,
        custom_alias=link.custom_alias,
        expires_at=expires_at,
        user_id=current_user.id if current_user else None  
    )

    db.add(db_link)
    db.commit()
    db.refresh(db_link)

    return {
        **link.dict(),
        "short_url": short_code,
        "created_at": db_link.created_at
    }


@router.get("/{short_code}")
async def redirect_link(short_code: str, db: Session = Depends(get_db)):
    # Проверяем кэш
    cached_url = redis_client.get(cache_key_redirect(short_code))
    if cached_url:
        return {"Redirect": cached_url.decode()}

    link = db.query(Link).filter(
        (Link.short_code == short_code) &
        (Link.is_active == True)
    ).first()

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    if link.expires_at and link.expires_at < datetime.utcnow():
        archived_link = ArchivedLink(
            original_url=link.original_url,
            short_code=link.short_code,
            created_at=link.created_at,
            expires_at=link.expires_at,
            clicks=link.clicks,
            last_accessed=link.last_accessed,
            user_id=link.user_id
        )
        db.add(archived_link)
        db.delete(link)
        db.commit()
        # Очищаем кэш
        redis_client.delete(cache_key_redirect(short_code))
        raise HTTPException(status_code=410, detail="Link expired and archived")

    # Обновляем кэш
    redis_client.setex(
        cache_key_redirect(short_code),
        DEFAULT_EXPIRE,
        link.original_url
    )

    # Обновляем статистику
    link.clicks += 1
    link.last_accessed = datetime.utcnow()
    db.commit()

    return {"Redirect": link.original_url}


@router.put("/{short_code}")
def update_link(
        short_code: str,
        update: LinkUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    link = db.query(Link).filter_by(short_code=short_code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    check_link_ownership(link, current_user)

    link.original_url = str(update.new_url)
    db.commit()
    return {"message": "Link updated successfully"}


@router.delete("/{short_code}")
def delete_link(
        short_code: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    link = db.query(Link).filter_by(short_code=short_code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    check_link_ownership(link, current_user)

    db.delete(link)
    db.commit()

    # Очищаем кэш
    redis_client.delete(
        cache_key_redirect(short_code),
        cache_key_stats(short_code)
    )

    return {"message": "Link deleted"}


@router.get("/{short_code}/stats", response_model=LinkStats)
async def get_link_stats(short_code: str, db: Session = Depends(get_db)):
    cache_key = cache_key_stats(short_code)
    cached_stats = redis_client.get(cache_key)
    if cached_stats:
        return json.loads(cached_stats)

    link = db.query(Link).filter_by(short_code=short_code).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    stats_data = {
        "original_url": link.original_url,
        "created_at": link.created_at.isoformat(),
        "clicks": link.clicks,
        "last_accessed": link.last_accessed.isoformat() if link.last_accessed else None,
        "expires_at": link.expires_at.isoformat() if link.expires_at else None
    }

    redis_client.setex(
        cache_key,
        60,
        json.dumps(stats_data)
    )

    return stats_data


@router.get("/search/")
async def search_links(original_url: str, db: Session = Depends(get_db)):
    cache_key = cache_key_search(original_url)
    cached_result = redis_client.get(cache_key)
    if cached_result:
        return json.loads(cached_result)

    links = db.query(Link).filter(Link.original_url == original_url).all()
    if not links:
        raise HTTPException(status_code=404, detail="Link not found")

    result = [{
        "original_url": link.original_url,
        "short_code": link.short_code,
        "created_at": link.created_at.isoformat(),
        "expires_at": link.expires_at.isoformat() if link.expires_at else None
    } for link in links]

    redis_client.setex(
        cache_key,
        DEFAULT_EXPIRE,
        json.dumps(result)
    )


@router.get("/archive/", response_model=list[ArchivedLinkStats])
def get_archive(
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    archived = db.query(ArchivedLink).filter(
        ArchivedLink.user_id == user.id
    ).order_by(ArchivedLink.archived_at.desc()).all()

    return [
        {
            "original_url": link.original_url,
            "created_at": link.created_at.isoformat(),
            "clicks": link.clicks,
            "last_accessed": link.last_accessed.isoformat() if link.last_accessed else None,
            "expires_at": link.expires_at.isoformat() if link.expires_at else None,
            "archived_at": link.archived_at.isoformat(),
        }
        for link in archived
    ]
