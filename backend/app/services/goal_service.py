"""
Goal Service — Business logic for Person 2 Target Savings Goals.

All operations are strictly scoped to the authenticated user's ID.
"""
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.goal import Goal
from app.schemas.goal import GoalCreate, GoalUpdate


def create_goal(db: Session, user_id: str, goal_in: GoalCreate) -> Goal:
    """
    Create a new Goal for the authenticated user.
    """
    goal = Goal(
        userId=user_id,
        name=goal_in.name,
        targetAmount=goal_in.targetAmount,
        currentAmount=goal_in.currentAmount,
        targetDate=goal_in.targetDate,
        monthlyContribution=goal_in.monthlyContribution,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


def get_goals(db: Session, user_id: str) -> List[Goal]:
    """
    Retrieve all Goals for a given user, ordered by targetDate ascending.
    """
    return (
        db.query(Goal)
        .filter(Goal.userId == user_id)
        .order_by(Goal.targetDate.asc(), Goal.createdAt.desc())
        .all()
    )


def get_goal_by_id(db: Session, goal_id: str, user_id: str) -> Optional[Goal]:
    """
    Retrieve a single Goal by ID, scoped to the authenticated user.
    """
    return (
        db.query(Goal)
        .filter(Goal.id == goal_id, Goal.userId == user_id)
        .first()
    )


def update_goal(db: Session, goal: Goal, goal_in: GoalUpdate) -> Goal:
    """
    Update an existing Goal with partial update fields.
    """
    update_data = goal_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(goal, field, value)

    db.commit()
    db.refresh(goal)
    return goal


def add_funds_to_goal(db: Session, goal: Goal, amount: Decimal) -> Goal:
    """
    Add funds directly to a Goal's accumulated currentAmount.
    """
    goal.currentAmount = Decimal(str(goal.currentAmount)) + Decimal(str(amount))
    db.commit()
    db.refresh(goal)
    return goal


def delete_goal(db: Session, goal: Goal) -> None:
    """
    Delete a Goal record.
    """
    db.delete(goal)
    db.commit()
