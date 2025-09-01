from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from ..schemas.generate import GenerateRequest, GenerateResponse
from ..db.base import get_db
from ..db.models.blog import Blog
from ..db.models.user import User
from ..core.deps import get_current_user

router = APIRouter()


def _simple_title_from_prompt(prompt: str) -> str:
    # Naive title creation. In real scenario, call AI provider.
    cleaned = prompt.strip().split(".")[0][:80]
    if len(cleaned) < 10:
        cleaned = f"Blog about {cleaned or 'your topic'}"
    return cleaned.title()


def _simple_content_from_prompt(prompt: str) -> str:
    # Naive content generation placeholder. Replace with external AI integration if needed.
    return (
        f"# {_simple_title_from_prompt(prompt)}\n\n"
        f"Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        f"## Introduction\n"
        f"{prompt}\n\n"
        f"## Key Points\n"
        f"- Insight 1 related to the prompt\n"
        f"- Insight 2 with practical advice\n"
        f"- Insight 3 summarizing outcomes\n\n"
        f"## Conclusion\n"
        f"This draft was generated automatically and should be reviewed and edited for accuracy."
    )


@router.post("", response_model=GenerateResponse, summary="Generate a blog draft from a prompt")
# PUBLIC_INTERFACE
def generate_blog(payload: GenerateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Generate a blog draft from a prompt and create a draft Blog record.

    Args:
        payload: GenerateRequest containing the prompt string
        db: DB session
        current_user: authenticated user

    Returns:
        GenerateResponse: title and content of the generated blog
    """
    title = _simple_title_from_prompt(payload.prompt)
    content = _simple_content_from_prompt(payload.prompt)

    blog = Blog(
        title=title,
        prompt=payload.prompt,
        generated_content=content,
        edited_content=None,
        status="draft",
        author_id=current_user.id,
    )
    db.add(blog)
    db.commit()
    return GenerateResponse(title=title, content=content)
