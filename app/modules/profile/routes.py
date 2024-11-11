from app.modules.auth.services import AuthenticationService
from app.modules.dataset.models import DataSet
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user

from app import db
from app.modules.profile import profile_bp
from app.modules.profile.forms import UserProfileForm, UpdateAnswersForm
from app.modules.profile.services import UserProfileService, AnswersUpdateService


@profile_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    auth_service = AuthenticationService()
    profile = auth_service.get_authenticated_user_profile
    if not profile:
        return redirect(url_for("public.index"))

    form = UserProfileForm()
    if request.method == "POST":
        service = UserProfileService()
        result, errors = service.update_profile(profile.id, form)
        return service.handle_service_response(
            result, errors, "profile.edit_profile", "Profile updated successfully", "profile/edit.html", form
        )

    return render_template("profile/edit.html", form=form)


@profile_bp.route('/profile/summary')
@login_required
def my_profile():
    page = request.args.get('page', 1, type=int)
    per_page = 5

    user_datasets_pagination = db.session.query(DataSet) \
        .filter(DataSet.user_id == current_user.id) \
        .order_by(DataSet.created_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    total_datasets_count = db.session.query(DataSet) \
        .filter(DataSet.user_id == current_user.id) \
        .count()

    print(user_datasets_pagination.items)

    return render_template(
        'profile/summary.html',
        user_profile=current_user.profile,
        user=current_user,
        datasets=user_datasets_pagination.items,
        pagination=user_datasets_pagination,
        total_datasets=total_datasets_count
    )


@profile_bp.route('/profile/edit_answers', methods=['GET', 'POST'])
@login_required
def edit_answers():
    profile_service = AnswersUpdateService()

    form = UpdateAnswersForm()

    if request.method == 'POST' and form.validate_on_submit():
        result = profile_service.change_answers(current_user, form.answer1.data, form.answer2.data, form.answer3.data)

        if "successfully" in result:
            return redirect(url_for('profile.edit_profile'))

    return render_template("profile/edit_answers.html", form=form)
