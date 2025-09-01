from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..db.models.blog import Blog
from ..db.models.user import User
from ..core.deps import get_current_user
from ..schemas.blogs import BlogCreate, BlogUpdate, BlogOut, BlogList

router = APIRouter()


def _to_out(b: Blog) -> BlogOut:
    return BlogOut(
        id=b.id,
        title=b.title,
        prompt=b.prompt,
        generated_content=b.generated_content,
        edited_content=b.edited_content,
        status=b.status,
        author_id=b.author_id,
        created_at=b.created_at,
        updated_at=b.updated_at,
    )


@router.post("", response_model=BlogOut, status_code=201, summary="Create a blog")
# PUBLIC_INTERFACE
def create_blog(payload: BlogCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a blog record (useful when not using generator directly)."""
    blog = Blog(
        title=payload.title,
        prompt=payload.prompt,
        generated_content=payload.generated_content,
        edited_content=payload.edited_content,
        status=payload.status or "draft",
        author_id=current_user.id,
    )
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return _to_out(blog)


@router.get("", response_model=BlogList, summary="List blogs (with pagination and optional status)")
# PUBLIC_INTERFACE
def list_blogs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max items to return"),
    status_filter: Optional[str] = Query(default=None, description="Filter by status"),
):
    """List blogs for the current user with pagination and optional status filter."""
    q = db.query(Blog).filter(Blog.author_id == current_user.id)
    if status_filter:
        q = q.filter(Blog.status == status_filter)
    total = q.count()
    items = q.order_by(Blog.created_at.desc()).offset(skip).limit(limit).all()
    return BlogList(items=[_to_out(b) for b in items], total=total)


@router.get("/{blog_id}", response_model=BlogOut, summary="Get a blog by id")
# PUBLIC_INTERFACE
def get_blog(blog_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retrieve a single blog owned by the current user."""
    blog = db.query(Blog).filter(Blog.id == blog_id, Blog.author_id == current_user.id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
    return _to_out(blog)


@router.put("/{blog_id}", response_model=BlogOut, summary="Update a blog (replace)")
# PUBLIC_INTERFACE
def update_blog(blog_id: int, payload: BlogCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Replace a blog's content."""
    blog = db.query(Blog).filter(Blog.id == blog_id, Blog.author_id == current_user.id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
    blog.title = payload.title
    blog.prompt = payload.prompt
    blog.generated_content = payload.generated_content
    blog.edited_content = payload.edited_content
    blog.status = payload.status or blog.status
    db.commit()
    db.refresh(blog)
    return _to_out(blog)


@router.patch("/{blog_id}", response_model=BlogOut, summary="Patch a blog (edit content/status/title)")
# PUBLIC_INTERFACE
def patch_blog(blog_id: int, payload: BlogUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Edit parts of a blog."""
    blog = db.query(Blog).filter(Blog.id == blog_id, Blog.author_id == current_user.id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
    if payload.title is not None:
        blog.title = payload.title
    if payload.edited_content is not None:
        blog.edited_content = payload.edited_content
    if payload.status is not None:
        blog.status = payload.status
    db.commit()
    db.refresh(blog)
    return _to_out(blog)


@router.delete("/{blog_id}", status_code=204, summary="Delete a blog")
# PUBLIC_INTERFACE
def delete_blog(blog_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete a blog owned by the current user."""
    blog = db.query(Blog).filter(Blog.id == blog_id, Blog.author_id == current_user.id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
    db.delete(blog)
    db.commit()
    return None
