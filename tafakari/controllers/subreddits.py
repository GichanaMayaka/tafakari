from http import HTTPStatus

import pendulum
from flask import Blueprint, Response, jsonify
from flask_jwt_extended import current_user, jwt_required
from flask_pydantic import validate
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

from ..extensions import cache, limiter
from ..models.subreddit import Subreddit
from ..models.users import User
from ..utils import CACHE_KEYS_REFERENCE, cache_invalidator, cache_setter
from .schemas import (
    AllSubredditsViewSchema,
    CreateSubredditRequestSchema,
    SubredditViewSchema,
)

subreddits = Blueprint("subreddit", __name__)


@subreddits.route("/subreddits", methods=["POST"])
@limiter.limit("10/day")
@jwt_required(fresh=True)
@validate(body=CreateSubredditRequestSchema)
def create_subreddit(body: CreateSubredditRequestSchema) -> tuple[Response, int]:
    """Create a subreddit

    Args:
        body (CreateSubredditRequestSchema): Request Schema

    Returns:
        tuple[Response, int]: Response Object and Status Code
    """
    subreddit = Subreddit.query.filter_by(name=body.name).first()

    if not subreddit and current_user:
        new_subreddit = Subreddit.create(
            name=body.name, description=body.description, created_by=current_user.id
        )

        new_subreddit.user.append(current_user)
        new_subreddit.save()

        created_subreddit = SubredditViewSchema(
            id=new_subreddit.id,
            name=new_subreddit.name,
            description=new_subreddit.description,
            members=new_subreddit.get_members(),
            created_on=new_subreddit.created_on,
        ).dict()

        cache_key = CACHE_KEYS_REFERENCE["SUBREDDIT_ID"](f"{new_subreddit.id}")
        cache_setter(cache_key, created_subreddit)
        return jsonify(message="created"), HTTPStatus.CREATED

    return (
        jsonify(message=f"A subreddit with the title: {body.name}, already exists"),
        HTTPStatus.CONFLICT,
    )


@subreddits.route("/subreddits/<int:subreddit_id>", methods=["PUT"])
@limiter.limit("10/hour")
@jwt_required(fresh=True)
@validate(body=CreateSubredditRequestSchema)
def update_a_subreddit(
    body: CreateSubredditRequestSchema, subreddit_id: int
) -> tuple[Response, int]:
    """Update a subreddit

    Args:
        body (CreateSubredditRequestSchema): The Request body from the Client

    Returns:
        tuple[Response, int]: Response Object and Status Code
    """
    if current_user:
        subreddit: Subreddit = Subreddit.query.filter(
            and_(Subreddit.created_by == current_user.id, Subreddit.id == subreddit_id)
        ).first()

        if subreddit:
            updated_subreddit = subreddit.update(
                name=body.name, description=body.description, modified_on=pendulum.now()
            )

            response = SubredditViewSchema(
                id=updated_subreddit.id,
                name=updated_subreddit.name,
                description=updated_subreddit.description,
                created_on=updated_subreddit.created_on,
                members=subreddit.get_members(),
            ).dict()

            # Build relevant cache keys for setting and invalidation
            subreddit_cache_key = CACHE_KEYS_REFERENCE["SUBREDDIT_ID"](
                f"{updated_subreddit.id}"
            )
            current_user_profile_cache_key = CACHE_KEYS_REFERENCE["PROFILE"](
                f"{current_user.username}"
            )
            all_subreddits_cache_key = CACHE_KEYS_REFERENCE["ALL_SUBREDDITS"]
            cache_setter(subreddit_cache_key, response)
            cache_invalidator(
                [current_user_profile_cache_key, all_subreddits_cache_key]
            )
            return jsonify(response), HTTPStatus.ACCEPTED

        return (
            jsonify(message="You can't edit a subreddit you did not create"),
            HTTPStatus.FORBIDDEN,
        )

    return (
        jsonify(message="You are not allowed to access this resource"),
        HTTPStatus.FORBIDDEN,
    )


@subreddits.route("/subreddits", methods=["GET"])
@limiter.limit("1000/day")
def get_all_subreddits() -> tuple[Response, int]:
    """Get all subreddits

    Returns:
        tuple[Response, int]: Response Object and Status Code
    """
    cache_key = CACHE_KEYS_REFERENCE["ALL_SUBREDDITS"]
    cached_data = cache.get(cache_key)

    if not cached_data:
        all_subs = Subreddit.query.all()

        all_subs_response = []
        if all_subs:
            for sub in all_subs:
                subreddit_schema = SubredditViewSchema(
                    id=sub.id,
                    name=sub.name,
                    description=sub.description,
                    members=sub.get_members(),
                    created_on=sub.created_on,
                )

                all_subs_response.append(subreddit_schema)

            response = AllSubredditsViewSchema(subreddits=all_subs_response).dict()

            cache_setter(cache_key, response)
            return (
                jsonify(response),
                HTTPStatus.OK,
            )

        return jsonify(message="Subreddit Not Found"), HTTPStatus.NOT_FOUND

    return jsonify(cached_data), HTTPStatus.OK


@subreddits.route("/subreddits/<int:subreddit_id>", methods=["GET"])
@limiter.limit("1000/day")
def get_subreddit_by_id(subreddit_id: int) -> tuple[Response, int]:
    """Get a single subreddit

    Args:
        subreddit_id (int): Subreddit Id parsed from URL

    Returns:
        tuple[Response, int]: Response Object and Status Code
    """
    cache_key = CACHE_KEYS_REFERENCE["SUBREDDIT_ID"](subreddit_id)
    cached_data = cache.get(cache_key)

    if not cached_data:
        subreddit = Subreddit.query.filter(Subreddit.id == subreddit_id).first()

        if subreddit:
            response = SubredditViewSchema(
                id=subreddit.id,
                name=subreddit.name,
                description=subreddit.description,
                members=subreddit.get_members(),
                created_on=subreddit.created_on,
            ).dict()

            cache_setter(cache_key, response)
            return (
                jsonify(response),
                HTTPStatus.OK,
            )

        return jsonify(message="No Subreddit Found"), HTTPStatus.NOT_FOUND

    return jsonify(cached_data), HTTPStatus.OK


@subreddits.route("/join/subreddits/<int:subreddit_id>", methods=["GET"])
@limiter.exempt
@jwt_required(fresh=True)
def join_a_subreddit(subreddit_id: int) -> tuple[Response, int]:
    """Join a subreddit

    Args:
        subreddit_id (int): Subreddit Id

    Returns:
        tuple[Response, int]: Response Object and Status Code
    """
    subreddit = Subreddit.get_by_id(subreddit_id)

    if subreddit and current_user:
        try:
            subreddit.user.append(current_user)
            subreddit.save()

            updated_subreddit = SubredditViewSchema(
                id=subreddit.id,
                name=subreddit.name,
                description=subreddit.description,
                members=subreddit.get_members(),
                created_on=subreddit.created_on,
            ).dict()

            subreddit_id_cache_key = CACHE_KEYS_REFERENCE["SUBREDDIT_ID"](subreddit.id)
            cache_setter(subreddit_id_cache_key, updated_subreddit)
            cache_invalidator(
                [
                    CACHE_KEYS_REFERENCE["ALL_SUBREDDITS"],
                    CACHE_KEYS_REFERENCE["PROFILE"](current_user.username),
                    subreddit_id_cache_key,
                ]
            )
            return (
                jsonify(
                    message=f"Successfully joined {subreddit.name}",
                    time_of_join=f"{pendulum.now()}",
                ),
                HTTPStatus.OK,
            )

        except IntegrityError:
            return jsonify(message="You have already joined."), HTTPStatus.FORBIDDEN

    return jsonify(message="Subreddit Not Found"), HTTPStatus.NOT_FOUND


@subreddits.route("/subreddits/<int:subreddit_id>", methods=["DELETE"])
@limiter.exempt
@jwt_required(fresh=True)
def delete_a_subreddit(subreddit_id: int) -> tuple[Response, int]:
    """Delete a subreddit

    Args:
        subreddit_id (int): Subreddit Id

    Returns:
        tuple[Response, int]: Response Object and Status Code
    """
    creator_id = User.query.filter_by(username=current_user.username).first()

    if creator_id:
        subreddit_creator = Subreddit.query.filter(
            and_(Subreddit.id == subreddit_id, Subreddit.created_by == creator_id.id)
        ).first()

        if subreddit_creator:
            subreddit_creator.delete()

            cache.delete(f"subreddit_{subreddit_id}")
            cache.delete("all_subs")
            cache_invalidator(
                [
                    CACHE_KEYS_REFERENCE["ALL_SUBREDDITS"],
                    CACHE_KEYS_REFERENCE["SUBREDDIT_ID"](subreddit_id),
                    CACHE_KEYS_REFERENCE["PROFILE"](current_user.username),
                ]
            )
            return jsonify(message="Deleted Successfully"), HTTPStatus.ACCEPTED

    return (
        jsonify(message="You are not authorised to delete this subreddit"),
        HTTPStatus.FORBIDDEN,
    )
