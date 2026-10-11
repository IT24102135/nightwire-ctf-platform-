"""
CTFd Hint Penalty Plugin
Automatically deducts points when hints are viewed (before solving challenges)
"""

from flask import Blueprint, jsonify
from CTFd.models import db, Hints, Users, Awards, Challenges
from CTFd.plugins import register_plugin_blueprint
from CTFd.utils import get_current_user
from datetime import datetime
import logging

log = logging.getLogger("ctfd.plugins.hint_penalty")


class HintDeduction(db.Model):
    """Track which users have viewed which hints"""
    __tablename__ = "hint_deductions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    hint_id = db.Column(db.Integer, db.ForeignKey("hints.id"), nullable=False)
    challenge_id = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Integer, default=5)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    # Prevent duplicate penalties for same user viewing same hint
    __table_args__ = (
        db.UniqueConstraint("user_id", "hint_id", name="uq_user_hint_deduction"),
    )


# Create blueprint for hint penalty endpoints
bp = Blueprint("hint_penalty", __name__, url_prefix="/api/v1/hint-penalty")


@bp.route("/hints/<int:hint_id>", methods=["GET"])
def get_hint_unrestricted(hint_id):
    """
    Get a hint WITHOUT requiring challenge to be solved first.
    Automatically deducts points.
    """
    try:
        user = get_current_user()

        if not user:
            return jsonify({"success": False, "message": "Authentication required"}), 401

        if not user.team_id:
            return jsonify({"success": False, "message": "User must be on a team"}), 403

        # Get the hint
        hint = Hints.query.filter_by(id=hint_id).first()
        if not hint:
            return jsonify({"success": False, "message": "Hint not found"}), 404

        # Get challenge
        challenge = Challenges.query.filter_by(id=hint.challenge_id).first()
        if not challenge:
            return jsonify({"success": False, "message": "Challenge not found"}), 404

        # Check if user already viewed this hint
        existing = HintDeduction.query.filter_by(
            user_id=user.id,
            hint_id=hint_id
        ).first()

        if not existing:
            # First time viewing this hint - apply penalty
            cost = hint.cost if hint.cost else 5

            # Create deduction record
            deduction = HintDeduction(
                user_id=user.id,
                hint_id=hint_id,
                challenge_id=hint.challenge_id,
                cost=cost,
            )
            db.session.add(deduction)
            db.session.flush()

            # Create negative award (penalty)
            award = Awards(
                team_id=user.team_id,
                name="Hint penalty",
                description=f"Penalty for viewing hint on Challenge #{hint.challenge_id}",
                value=-cost,
                category="hints",
                type="standard",
            )
            db.session.add(award)
            db.session.commit()

            log.info(
                f"[HINT PENALTY] User {user.id} (Team {user.team_id}) "
                f"viewed hint {hint_id}: -{cost} points"
            )

            return jsonify({
                "success": True,
                "data": {
                    "id": hint.id,
                    "challenge_id": hint.challenge_id,
                    "content": hint.content,
                    "cost": cost,
                    "penalty_applied": True,
                    "penalty_amount": cost,
                }
            })
        else:
            # Already viewed - return hint without penalty
            cost = hint.cost if hint.cost else 5
            return jsonify({
                "success": True,
                "data": {
                    "id": hint.id,
                    "challenge_id": hint.challenge_id,
                    "content": hint.content,
                    "cost": cost,
                    "penalty_applied": False,
                    "penalty_message": "Hint already viewed - no additional penalty",
                }
            })

    except Exception as e:
        log.error(f"[HINT PENALTY ERROR] {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "message": "Error processing hint"}), 500


def load(app):
    """Initialize the hint penalty plugin"""

    # Register the blueprint
    register_plugin_blueprint(app, bp)

    # Create tables if they don't exist
    with app.app_context():
        try:
            db.create_all()
            log.info("✓ Hint Penalty Plugin initialized - hint_deductions table created")
        except Exception as e:
            log.error(f"✗ Error initializing plugin: {str(e)}")
            raise

    log.info("✓ Hint Penalty Plugin loaded successfully")
