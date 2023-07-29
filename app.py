from models import User
from flask import Flask, render_template, url_for, redirect, flash, current_app, send_file, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, current_user, logout_user, login_required
from extensions import db, login_manager
from models import User, Attendance, Task, OffRequest
from forms import LoginForm, RegistrationForm, ChangePasswordForm, AttendanceForm, TaskForm, UpdatePictureForm, OffBalanceForm, OffRequestForm
from datetime import datetime, timedelta
from flask_migrate import Migrate
from io import BytesIO
import googlemaps
import csv
import os


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

    import os
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
        os.path.join(basedir, 'site.db')

    # initialize login_manager with app
    login_manager.init_app(app)

    # initialize db with app
    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app


app = create_app()


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route("/")
def base():
    return redirect(url_for('login'))


@app.route("/home")
def home():
    return render_template('home.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password.data, method='sha256')
        image_file = form.picture.data.read() if form.picture.data else None
        new_user = User(username=form.username.data,
                        password=hashed_password, image_file=image_file)
        db.session.add(new_user)
        db.session.commit()
        return '<h1>New user has been created!</h1>'
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Login success")
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    from forms import LoginForm
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('home'))
        return '<h1>Invalid username or password</h1>'
    return render_template('login.html', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    from forms import RegistrationForm
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password.data, method='sha256')  # hashing the password
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/change_password", methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.current_password.data):
                hashed_password = generate_password_hash(
                    form.new_password.data, method='sha256')
                user.password = hashed_password
                if form.picture.data:
                    user.image_file = form.picture.data.read()
                db.session.commit()
                flash('Your password has been updated!', 'success')
                return redirect(url_for('login'))
        flash('Please check your login details and try again.', 'danger')
    return render_template('change_password.html', title='Change Password', form=form)


@app.route("/logout", methods=['POST'])
def logout():
    from flask_login import logout_user
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/get_image/<filename>')
def get_image(filename):
    user = User.query.filter_by(username=filename).first()
    return send_file(BytesIO(user.image_file), mimetype='image/jpeg')


@app.route("/attendance", methods=['GET', 'POST'])
@login_required
def attendance():
    form = AttendanceForm()
    if form.validate_on_submit():
        print("Form validation successful")
        print("Current User ID: ", current_user.id)

        dates = request.form.get('date').split(' - ')
        start_date = datetime.strptime(dates[0], '%Y-%m-%d')
        if len(dates) == 2:
            end_date = datetime.strptime(dates[1], '%Y-%m-%d')
        else:
            end_date = start_date
        delta = end_date - start_date

        for i in range(delta.days + 1):
            date = start_date + timedelta(days=i)

            gmaps = googlemaps.Client(
                key='AIzaSyDaSOYJH2Ak5nMD2p55MtdipOi270GgZGM')
            geolocate_result = gmaps.geolocate()

            lat = geolocate_result['location']['lat']
            lng = geolocate_result['location']['lng']
            reverse_geocode_result = gmaps.reverse_geocode((lat, lng))

            if reverse_geocode_result and len(reverse_geocode_result) > 0:
                address = reverse_geocode_result[0]['formatted_address']
            else:
                # Fallback to lat, lng if reverse geocoding fails
                address = f"{lat}, {lng}"

            time_of_submission = datetime.utcnow() + timedelta(hours=8)

            if form.status.data == 'OFF':
                off_request = OffRequest(date=date, user_id=current_user.id,
                                         location=address, time_of_submission=time_of_submission, duration=form.duration.data)
                db.session.add(off_request)
            else:
                attendance = Attendance(date=date, status=form.status.data, duration=form.duration.data,
                                        user_id=current_user.id, location=address, time_of_submission=time_of_submission)
                db.session.add(attendance)

        try:
            db.session.commit()
            print("Attendance committed successfully")
            flash('Your attendance has been submitted!', 'success')
            return redirect(url_for('attendance'))
        except Exception as e:
            print("Error occurred during commit: ", e)

    # Get current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Query all users
    users = User.query.with_entities(User.username).all()
    users = [user.username for user in User.query.all()]

    # Query all attendances in the current month and year
    attendances = Attendance.query.filter(
        db.extract('month', Attendance.date) == current_month,
        db.extract('year', Attendance.date) == current_year
    ).all()
    attendances = [
        {
            'user': a.user.username,
            'date': a.date,
            'status': a.status,
            'time_of_submission': a.time_of_submission,
            'duration': a.duration,
            'location': a.location
        }
        for a in attendances
    ]
    # Render the template with additional parameters
    return render_template(
        'attendance.html',
        form=form,
        attendances=attendances,
        users=users,
        current_month=current_month,
        current_year=current_year
    )


@app.route('/get_attendances', methods=['GET'])
@login_required
def get_attendances():
    month = request.args.get('month')
    year = request.args.get('year')

    print(f"Month: {month}, Year: {year}")  # Debug print

    attendances = Attendance.query.filter(
        db.extract('month', Attendance.date) == month,
        db.extract('year', Attendance.date) == year
    ).join(User).all()

    attendances = [
        {
            'user': a.user.username,
            'date': a.date.isoformat(),
            'status': a.status
        }
        for a in attendances
    ]

    return jsonify(attendances)


@app.route("/off_balance", methods=['GET', 'POST'])
@login_required
def off_balance():
    form = OffBalanceForm()
    form.usernames.choices = [(user.username, user.username)
                              for user in User.query.all()]

    user = User.query.filter_by(username=current_user.username).first_or_404()
    off_balance = user.off_balance

    off_requests = OffRequest.query.filter_by(
        status='Pending').all() if current_user.username == 'admin1' else []

    return render_template('off_balance.html', off_balance=off_balance, form=form, off_requests=off_requests)


@app.route("/update_off_balance", methods=['POST'])
@login_required
def update_off_balance():
    if current_user.username != 'admin1':
        abort(404)

    # Get all usernames from the database
    usernames = [user.username for user in User.query.all()]

    # Create the form with the choices
    form = OffBalanceForm()
    form.usernames.choices = usernames

    if form.validate_on_submit():
        users = User.query.filter(User.username.in_(form.usernames.data)).all()

        for user in users:
            if form.add.data:
                user.off_balance += form.off_balance.data
            elif form.subtract.data:
                user.off_balance -= form.off_balance.data

        db.session.commit()

        flash('Off balance has been updated!', 'success')
        return redirect(url_for('off_balance'))


@app.route("/all_users_off_balance", methods=['GET'])
@login_required
def all_users_off_balance():
    if current_user.username != 'admin1':
        abort(403)  # Forbidden access
    users = User.query.all()
    return render_template('all_users_off_balance.html', users=users)


@app.route("/request_off", methods=['GET', 'POST'])
@login_required
def request_off():
    form = OffRequestForm()
    if form.validate_on_submit():
        time_of_submission = datetime.utcnow() + timedelta(hours=8)
        off_request = OffRequest(
            date=datetime,
            user_id=current_user.id,
            time_of_submission=time_of_submission
        )
        db.session.add(off_request)
        db.session.commit()
        flash('Your off request has been submitted!', 'success')
        return redirect(url_for('request_off'))
    return render_template('request_off.html', title='Request Off', form=form)


@app.route("/approve_off_request/<int:request_id>")
@login_required
def approve_off_request(request_id):
    if current_user.username != 'admin1':
        abort(404)
    off_request = OffRequest.query.get_or_404(request_id)
    off_request.status = 'Approved'
    # Add off request to user's attendance
    user = User.query.get(off_request.user_id)
    attendance = Attendance(date=off_request.date, status='Off', duration=off_request.duration,
                            user_id=user.id, location=off_request.location,
                            time_of_submission=off_request.time_of_submission)
    db.session.add(attendance)
    db.session.commit()
    flash('Off request has been approved!', 'success')
    return redirect(url_for('off_balance'))


@app.route("/deny_off_request/<int:request_id>")
@login_required
def deny_off_request(request_id):
    if current_user.username != 'admin1':
        abort(404)
    off_request = OffRequest.query.get_or_404(request_id)
    off_request.status = 'Denied'
    db.session.commit()
    flash('Off request has been denied!', 'success')
    return redirect(url_for('off_balance'))


@app.route("/all_attendance")
@login_required
def all_attendance():
    all_attendance = db.session.query(Attendance, User).join(
        User, Attendance.user_id == User.id).all()
    return render_template('all_attendance.html', title='All Employees Attendance', all_attendance=all_attendance)


@app.route("/export_attendance_csv", methods=['GET'])
@login_required
def export_attendance_csv():
    if current_user.username != 'admin1':
        abort(404)

    filename = 'attendance.csv'
    attendances = db.session.query(Attendance, User).join(
        User, Attendance.user_id == User.id).all()

    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        # write the header
        writer.writerow(["Username", "Status of Attendance",
                        "Time of Submission", "Location"])

        for attendance, user in attendances:
            writer.writerow([user.username, attendance.status,
                            attendance.time_of_submission, attendance.location])

    path = os.path.join(os.getcwd(), filename)
    return send_file(path, as_attachment=True)


@app.route('/announcements')
def announcements():
    return render_template('announcements.html')


@app.route("/tasks", methods=['GET', 'POST'])
@login_required
def tasks():
    form = None
    if current_user.username == "admin1":  # Only the admin can create tasks
        form = TaskForm()

        # Load all the usernames into the assigned_to field's choices
        users = User.query.with_entities(User.username).all()
        form.assigned_to.choices = [user[0] for user in users]

        if form.validate_on_submit():
            new_task = Task(task_name=form.task_name.data,
                            assigned_to=form.assigned_to.data, created_by=current_user.username)
            db.session.add(new_task)
            db.session.commit()
            flash('Task has been assigned!', 'success')
            return redirect(url_for('tasks'))

    # Fetch tasks - admin sees all tasks, other users only see tasks assigned to them
    if current_user.username == "admin1":
        to_be_completed_tasks = Task.query.filter_by(is_completed=False).all()
        completed_tasks = Task.query.filter_by(is_completed=True).all()
    else:
        to_be_completed_tasks = Task.query.filter_by(
            assigned_to=current_user.username, is_completed=False).all()
        completed_tasks = Task.query.filter_by(
            assigned_to=current_user.username, is_completed=True).all()

    return render_template('tasks.html', title='Tasks', form=form, to_be_completed_tasks=to_be_completed_tasks, completed_tasks=completed_tasks)


@app.route("/complete_task/<int:task_id>", methods=['GET'])
@login_required
def complete_task(task_id):
    task = Task.query.get(task_id)
    if task and (current_user.username == task.assigned_to or current_user.username == 'admin1'):
        task.is_completed = True
        db.session.commit()
        flash('Task has been completed!', 'success')
    else:
        flash('Error: Task not found or insufficient permissions', 'error')
    return redirect(url_for('tasks'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdatePictureForm()
    if form.validate_on_submit():
        if form.picture.data:
            current_user.image_file = form.picture.data.read()
            db.session.commit()
            flash('Your profile picture has been updated!', 'success')
            return redirect(url_for('profile'))
    return render_template('profile.html', user=current_user, form=form)


if __name__ == '__main__':
    app.run(debug=True)
