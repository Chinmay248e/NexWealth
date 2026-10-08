"""
Goal API Router — Protected CRUD and funding endpoints for Person 2 Goal management.

All endpoints require JWT authentication via the `get_current_user` dependency.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.goal import (
    GoalCreate,
    GoalUpdate,
    GoalAddFunds,
    GoalResponse,
    GoalDeleteResponse,
)
from app.services.goal_service import (
    create_goal,
    get_goals,
    get_goal_by_id,
    update_goal,
    add_funds_to_goal,
    delete_goal,
)

goal_router = APIRouter(prefix="/goals", tags=["Goals"])


@goal_router.post(
    "",
    response_model=GoalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new target savings goal",
)
def create_goal_endpoint(
    goal_in: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new Goal for the authenticated user.
    """
    return create_goal(db=db, user_id=current_user.id, goal_in=goal_in)


@goal_router.get(
    "",
    response_model=List[GoalResponse],
    status_code=status.HTTP_200_OK,
    summary="List all savings goals for the current user",
)
def list_goals_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all Goals belonging to the authenticated user.
    """
    return get_goals(db=db, user_id=current_user.id)


@goal_router.get(
    "/{goal_id}",
    response_model=GoalResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a specific goal by ID",
)
def get_goal_endpoint(
    goal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a specific Goal by ID. Returns 404 if not found or unauthorized.
    """
    goal = get_goal_by_id(db=db, goal_id=goal_id, user_id=current_user.id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found.",
        )
    return goal


@goal_router.put(
    "/{goal_id}",
    response_model=GoalResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing goal",
)
def update_goal_endpoint(
    goal_id: str,
    goal_in: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing Goal.
    """
    goal = get_goal_by_id(db=db, goal_id=goal_id, user_id=current_user.id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found.",
        )
    return update_goal(db=db, goal=goal, goal_in=goal_in)


@goal_router.post(
    "/{goal_id}/add-funds",
    response_model=GoalResponse,
    status_code=status.HTTP_200_OK,
    summary="Add funds directly to an existing goal",
)
def add_funds_endpoint(
    goal_id: str,
    funds_in: GoalAddFunds,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Add funds to a Goal's accumulated currentAmount.
    """
    goal = get_goal_by_id(db=db, goal_id=goal_id, user_id=current_user.id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found.",
        )
    return add_funds_to_goal(db=db, goal=goal, amount=funds_in.amount)


@goal_router.delete(
    "/{goal_id}",
    response_model=GoalDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a savings goal",
)
def delete_goal_endpoint(
    goal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a Goal record.
    """
    goal = get_goal_by_id(db=db, goal_id=goal_id, user_id=current_user.id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found.",
        )
    deleted_id = goal.id
    delete_goal(db=db, goal=goal)
    return GoalDeleteResponse(
        message="Goal deleted successfully.",
        id=deleted_id,
    )
