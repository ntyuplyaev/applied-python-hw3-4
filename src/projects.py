from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import Project, Link, link_project_association, User
from src.schemas import ProjectCreate, ProjectResponse, ProjectWithLinks
from src.security import get_current_user

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


@router.post("/", response_model=ProjectResponse)
def create_project(
        project: ProjectCreate,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    existing = db.query(Project).filter(
        (Project.name == project.name) &
        (Project.user_id == user.id)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project with this name already exists"
        )

    new_project = Project(
        name=project.name,
        user_id=user.id
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


@router.get("/{project_id}", response_model=ProjectWithLinks)
def get_project(
        project_id: int,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(
        (Project.id == project_id) &
        (Project.user_id == user.id)
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return project


@router.post("/{project_id}/links/{short_code}")
def add_link_to_project(
        project_id: int,
        short_code: str,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    # Проверка прав на проект
    project = db.query(Project).filter(
        (Project.id == project_id) &
        (Project.user_id == user.id)
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Проверка прав на ссылку
    link = db.query(Link).filter(
        (Link.short_code == short_code) &
        (Link.user_id == user.id)
    ).first()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )

    # Проверка существующей связи
    existing = db.execute(
        link_project_association.select().where(
            (link_project_association.c.link_id == link.id) &
            (link_project_association.c.project_id == project_id)
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Link already in project"
        )

    db.execute(
        link_project_association.insert().values(
            link_id=link.id,
            project_id=project.id
        )
    )
    db.commit()
    return {"message": "Link added to project"}