# Imports

from flask import render_template, session, url_for, request, redirect, send_from_directory, abort, flash

from flask_login import current_user, login_user, logout_user, login_required

from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from app import app, db, avatars
from app.forms import RegistrationForm, LoginForm, NewEventCreatorForm, NewDiagnoz, NewAllergen, UploadAvatarForm, CropAvatarForm, GetEventsForm, EditProfileForm, NewPostForm, UserSearchForm
from app.models import User, Event, Diagnoz, Allergen, Blogpost
from app.functions import smart_truncate

from datetime import datetime, timedelta

from sqlalchemy import desc, or_

import os

# Routes

# Index route
@app.route('/')
@app.route('/index')
def index():
	posts = Blogpost.query.filter(Blogpost.is_in_slider == True).all()
	for post in posts:
		post.title = smart_truncate(post.title, 40)
	return render_template("index.html", posts = posts)

# Static pages routes
@app.route('/about')
def about():
	return render_template("about.html")

@app.route('/services')
def services():
	return render_template("services.html")

@app.route('/contacts')
def contacts():
	return render_template("contacts.html")

# Login route
@app.route('/login/<var_login>', methods=['GET', 'POST'])
def login(var_login):
	if current_user.is_authenticated:
		return redirect(url_for('kabinet'))
	form = LoginForm()
	if form.validate_on_submit():
		if var_login == '1' and form.password.data == "":
			flash('Заполните все поля, пожалуйста.')
			return redirect(url_for('login', var_login = var_login))
		user = User.query.filter_by(id = form.medzdravaid.data).first()
		if user is None or not user.check_password(form.password.data) or user.check_phonenumber(form.phonenumber.data):
			flash('Нет такого пользователя')
			return redirect(url_for('login', var_login = var_login))
		login_user(user)
		return redirect(kabinet)

	return render_template("login.html", form=form, var_login = var_login)
	
@app.route('/prelogin')
def prelogin():
	if current_user.is_authenticated:
		return redirect(url_for('kabinet'))
	return render_template('prelogin.html')

# Registration page
@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(
			role = form.role.data,
			first_name = form.first_name.data,
			second_name = form.second_name.data,
			middle_name = form.middle_name.data,
			email = form.email.data,
			sex = form.sex.data,
			birthdate = form.birthdate.data,
			address = form.address.data,
			phonenumber = form.phonenumber.data,
		)
		print('kek')
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		if user.role == 1:
			return redirect(url_for('users', role = 1))
		elif user.role == 2:
			return redirect(url_for('users', role = 2))
		elif user.role == 3:
			return redirect(url_for('users', role = 3))
	return render_template("register.html", form=form)


# User list
@app.route('/users/<role>', methods = ['GET', 'POST'])
@login_required
def users(role):
	form = UserSearchForm()
	if form.validate_on_submit():
		return redirect(url_for('user_search', role = role, search = form.search.data))

	page = request.args.get('page', 1, type = int)
	user_list = User.query.filter(User.role == int(role)).order_by(User.second_name).order_by(User.first_name).order_by(User.middle_name).paginate(page, app.config['USERS_PER_PAGE'], False)
	next_url = url_for('users', role = role, page = user_list.next_num) \
		if user_list.has_next else None
	prev_url = url_for('users', role = role, page = user_list.prev_num) \
		if user_list.has_prev else None
	return render_template("users.html", user_list = user_list.items, next_url = next_url, prev_url = prev_url, form = form)



# User search
@app.route('/user_search/<role>/<search>', methods = ['GET', 'POST'])
@login_required
def user_search(role, search):
	if current_user.role == 1:
		abort(404)

	form = UserSearchForm()
	
	if form.validate_on_submit():
		return redirect(url_for('user_search', role = 1, search = form.search.data))

	if int(role) not in range(1,4):
		abort(404)

	if search == "":
		abort(404)
	else:
		user_list = User.query.filter(User.role == int(role)).filter(or_(User.first_name.like("%"+search+"%"), User.second_name.like("%"+search+"%"), User.middle_name.like("%"+search+"%"))).order_by(User.second_name).order_by(User.first_name).order_by(User.middle_name).all()
	return render_template("user_search.html", user_list = user_list, form = form, role = int(role))

# Users pages
@app.route('/patient/<medzdravaid>')
@login_required
def patient(medzdravaid):
	if current_user.role == 1 and current_user.id != int(medzdravaid):
		abort(404)
	future_event_list = Event.query.filter_by(id_patient = medzdravaid).filter(Event.datetime > datetime.utcnow()).order_by(Event.datetime.desc())
	
	past_event_list = Event.query.filter_by(id_patient = medzdravaid).filter(Event.datetime < datetime.utcnow()).order_by(Event.datetime.desc())

	patient = User.query.filter_by(id = medzdravaid).first_or_404()
	if patient.role != 1:
		abort(404)
	patient.id = str(patient.id).zfill(6)
	patient.phonenumber = str(patient.phonenumber).zfill(10)
	allergens = Allergen.query.filter_by(id_patient = medzdravaid).all()
	diagnozes = Diagnoz.query.filter_by(id_patient = medzdravaid).all()
	return render_template('patient.html', patient=patient, past_events = past_event_list, future_events = future_event_list, allergens = allergens, diagnozes = diagnozes)

@app.route('/administrator/<medzdravaid>')
@login_required
def administrator(medzdravaid):
	if current_user.role == 3:
		administrator = User.query.filter_by(id = medzdravaid).first_or_404()
		if administrator.role != 3:
			abort(404)
		administrator.id = str(administrator.id).zfill(6)
		return render_template('administrator.html', administrator = administrator)
	else:
		abort(404)

@app.route('/vrach/<medzdravaid>', methods = ['GET', 'POST'])
@login_required
def vrach(medzdravaid):
	if current_user.role == 1:
		abort(404)
	else:	
		form = GetEventsForm()
		vrach = User.query.filter_by(id = medzdravaid).first_or_404()
		if vrach.role != 2:
			abort(404)
		vrach.id = str(vrach.id).zfill(6)
		if form.validate_on_submit():
			getdate = form.eventdate.data
			return redirect(url_for('vrach_events', medzdravaid = medzdravaid, getdate = getdate))
		return render_template('vrach.html', vrach = vrach, form = form)
		
@app.route('/vrach/<medzdravaid>/<getdate>')
@login_required
def vrach_events(medzdravaid, getdate):
	if current_user.role == 1:
		abort(404)
	else:
		date = datetime.strptime(getdate, "%Y-%m-%d")
		date2 = date + timedelta(hours = 24)
		events = Event.query.filter(Event.id_vrach == medzdravaid).filter(Event.datetime >= date).filter(Event.datetime <= date2).order_by(desc(Event.datetime)).all()
		vrach = User.query.filter_by(id = medzdravaid).first_or_404()
		return render_template('vrach_events.html', date = date, events = events, vrach = vrach)

# Личный кабинет
@app.route('/kabinet')
@login_required
def kabinet():
	if int(current_user.role) == 1:
		return redirect(url_for('patient', medzdravaid = current_user.id))
	elif int(current_user.role) == 2:
		return redirect(url_for('vrach', medzdravaid = current_user.id))
	elif int(current_user.role) == 3:
		return redirect(url_for('administrator', medzdravaid = current_user.id))
	return redirect(url_for('index'))

# Login users out
@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

# Creation of a new Event
@app.route('/new_event/<medzdravaid>', methods=['GET', 'POST'])
@login_required
def new_event(medzdravaid):
	if current_user.role == 1:
		abort(404)
	form = NewEventCreatorForm()
	if form.validate_on_submit():
		event = Event(
			id_patient = int(medzdravaid),
			id_vrach = int(form.id_vrach.data),
			datetime = form.datetime.data,
			zacklucheniye = form.zacklucheniye.data,
			event_name = form.event_name.data
		)
		db.session.add(event)
		db.session.commit()
		return redirect(url_for('patient', medzdravaid = medzdravaid))
	return render_template('new_event.html', form = form)

@app.route('/new_allergen/<medzdravaid>', methods=['GET', 'POST'])
@login_required
def new_allergen(medzdravaid):
	if current_user.role == 1:
		abort(404)
	form = NewAllergen()
	if form.validate_on_submit():
		allergen = Allergen(
			id_patient = int(medzdravaid),
			allergen = form.allergen.data
		)
		db.session.add(allergen)
		db.session.commit()
		return redirect(url_for('patient', medzdravaid = medzdravaid))
	return render_template('new_allergen.html', form = form)

@app.route('/new_diagnoz/<medzdravaid>', methods=['GET', 'POST'])
@login_required
def new_diagnoz(medzdravaid):
	if current_user.role == 1:
		abort(404)
	form = NewDiagnoz()
	if form.validate_on_submit():
		diagnoz = Diagnoz(
			id_patient = int(medzdravaid),
			diagnoz = form.diagnoz.data
		)
		db.session.add(diagnoz)
		db.session.commit()
		return redirect(url_for('patient', medzdravaid = medzdravaid))
	return render_template('new_diagnoz.html', form = form)

# Serving avatar image
@app.route('/avatars/<path:filename>')
@login_required
def get_avatar(filename):
	return send_from_directory(app.config['AVATARS_SAVE_PATH'], filename)

@app.route('/post_image/<path:filename>')
def get_post_image(filename):
	if filename == "None":
		return 0
	else:
		print(filename)
		print('wow')
		return send_from_directory(app.config['POST_IMAGE_SAVE_PATH'], filename)

@app.route('/new_avatar/<medzdravaid>', methods=['GET', 'POST'])
@login_required
def upload(medzdravaid):
	if current_user.role == 1 and current_user.id != medzdravaid:
		abort(404)
	form = UploadAvatarForm()
	if form.validate_on_submit():
		f = form.image.data
		raw_filename = avatars.save_avatar(f)
		patient = User.query.filter_by(id = medzdravaid).first_or_404()
		old_avatar = patient.avatar_file_path
		setattr(patient, "avatar_file_path", raw_filename)
		db.session.commit()
		if os.path.exists(os.path.join(app.config['AVATARS_SAVE_PATH'], old_avatar)):
			os.remove(os.path.join(app.config['AVATARS_SAVE_PATH'], old_avatar))
		return redirect(url_for('crop', medzdravaid = medzdravaid))
	return render_template('upload.html', form = form)

@app.route('/crop/<medzdravaid>', methods=['GET', 'POST'])
@login_required
def crop(medzdravaid):
	if current_user.role == 1 and current_user.id != medzdravaid:
		abort(404)
	form = CropAvatarForm()
	patient = User.query.filter_by(id = medzdravaid).first_or_404()

	if form.validate_on_submit():
		x = form.x.data
		y = form.y.data
		w = form.w.data
		h = form.h.data
		raw_file = patient.avatar_file_path
		filenames = avatars.crop_avatar(patient.avatar_file_path, x, y, w, h)
		os.remove(os.path.join(app.config['AVATARS_SAVE_PATH'], raw_file))
		os.remove(os.path.join(app.config['AVATARS_SAVE_PATH'], filenames[0]))
		os.remove(os.path.join(app.config['AVATARS_SAVE_PATH'], filenames[1]))
		setattr(patient, "avatar_file_path", filenames[2])
		db.session.commit()
		user = User.query.filter_by(id = int(medzdravaid)).first_or_404()
		if user.role == 1:
			return redirect(url_for('patient', medzdravaid = medzdravaid))
		elif user.role == 2:
			return redirect(url_for('vrach', medzdravaid = medzdravaid))
		elif user.role == 3:
			return redirect(url_for('administrator', medzdravaid = medzdravaid))
	return render_template('crop.html', patient = patient, form = form)

@app.route('/edit_profile/<medzdravaid>', methods = ['GET', 'POST'])
@login_required
def edit_profile(medzdravaid):
	if current_user.role != 3:
		abort(404)
	form = EditProfileForm()
	user = User.query.filter_by(id = medzdravaid).first_or_404()
	if form.validate_on_submit():
		user.first_name = form.first_name.data
		user.second_name = form.second_name.data
		user.middle_name = form.middle_name.data
		user.birthdate = form.birthdate.data
		user.phonenumber = form.phonenumber.data
		user.address = form.address.data
		user.email = form.email.data
		db.session.commit()
		if user.role == 1:
			return redirect(url_for('patient', medzdravaid = user.id))
		elif user.role == 2:
			return redirect(url_for('vrach', medzdravaid = user.id))
		else:
			return redirect(url_for('administrator', medzdravaid = user.id))
	elif request.method == 'GET':
		form.first_name.data = user.first_name
		form.second_name.data = user.second_name
		form.middle_name.data = user.middle_name
		form.birthdate.data = user.birthdate
		form.phonenumber.data = user.phonenumber
		form.address.data = user.address
		form.email.data = user.email
	return render_template('edit_profile.html', form = form)

@app.route('/new_post', methods = ['GET', 'POST'])
@login_required
def new_post():
	if current_user.role != 3:
		abort(404)
	form = NewPostForm()
	if form.validate_on_submit():
		file = form.main_image.data
		print(file)
		if file == None:
			filename = "post_default.png"
			print('yeah')
		else:
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['POST_IMAGE_SAVE_PATH'], filename))
		post = Blogpost(
			title = form.title.data,
			content = form.main_text.data,
			is_in_slider = form.is_in_slider.data,
			main_image_path = filename
			)
		print(post.main_image_path)
		db.session.add(post)
		db.session.commit()
		return redirect(url_for('posts'))
	return render_template('new_post.html', form = form)

@app.route('/posts')
@login_required
def posts():
	if current_user.role != 3:
		abort(404)
	posts = Blogpost.query.all()
	for post in posts:
		post.title = smart_truncate(post.title, 90)
	return render_template('posts.html', posts = posts)

@app.route('/post/<postid>')
def post(postid):
	post = Blogpost.query.filter_by(id = postid).first_or_404()
	if post.main_image_path == None:
		post.main_image_path = "None"
	return render_template('post.html', post = post)

@app.route('/edit_post/<postid>', methods = ['GET', 'POST'])
@login_required
def edit_post(postid):
	if current_user.role != 3:
		abort(404)
	form = NewPostForm()
	post = Blogpost.query.filter_by(id = postid).first_or_404()
	if form.validate_on_submit():
		post.title = form.title.data
		post.content = form.main_text.data
		post.is_in_slider = form.is_in_slider.data
		db.session.commit()
		return redirect(url_for('post', postid = postid))
	elif request.method == 'GET':
		form.title.data = post.title
		form.main_image.data = post.main_image_path
		form.main_text.data = post.content
		form.is_in_slider.data = post.is_in_slider

	return render_template('edit_post.html', post = post, form = form)

@app.route('/delete_post/<postid>')
@login_required
def delete_post(postid):
	if current_user.role != 3:
		abort(404)
	Blogpost.query.filter_by(id = postid).delete(synchronize_session = False)
	db.session.commit()
	return redirect(url_for('posts'))

@app.route('/delete_user/<medzdravaid>/<role>')
@login_required
def delete_user(medzdravaid, role):
	if current_user.role != 3:
		abort(404)

	User.query.filter_by(id = medzdravaid).delete(synchronize_session = False)
	db.session.commit()
	return redirect(url_for('users', role = role))

@app.route('/edit_event/<eventid>', methods = ['GET', 'POST'])
@login_required
def edit_event(eventid):
	if current_user.role == 1:
		abort(404)
	
	event = Event.query.filter_by(id = eventid).first_or_404()
	if request.method == 'GET':
		form = NewEventCreatorForm(id_vrach = event.id_vrach)
		form.datetime.data = event.datetime
		form.event_name.data = event.event_name
		form.zacklucheniye.data = event.zacklucheniye
	else:
		form = NewEventCreatorForm()
	if form.validate_on_submit():
		event.id_vrach = form.id_vrach.data
		event.datetime = form.datetime.data
		event.event_name = form.event_name.data
		event.zacklucheniye = form.zacklucheniye.data
		db.session.commit()
		return redirect(url_for('patient', medzdravaid = event.id_patient))

	return render_template('new_event.html', form = form)


@app.route('/delete_event/<eventid>/<medzdravaid>')
@login_required
def delete_event(eventid, medzdravaid):
	if current_user == 1:
		abort(404)

	event = Event.query.filter_by(id = eventid).first_or_404()
	medzdravaid = event.id_patient
	Event.query.filter_by(id = eventid).delete(synchronize_session = False)
	db.session.commit()
	user = User.query.filter_by(id = medzdravaid).first_or_404()
	if user.role == 1:
		return redirect(url_for('patient', medzdravaid = medzdravaid))
	elif user.role == 2:
		return redirect(url_for('vrach', medzdravaid = medzdravaid))

@app.route('/edit_diagnoz/<diagnozid>', methods = ['GET', 'POST'])
@login_required
def edit_diagnoz(diagnozid):
	if current_user.role == 1:
		abort(404)

	diagnoz = Diagnoz.query.filter_by(id = diagnozid).first_or_404()
	form = NewDiagnoz()
	if form.validate_on_submit():
		diagnoz.diagnoz = form.diagnoz.data
		db.session.commit()
		return redirect(url_for('patient', medzdravaid = diagnoz.id_patient))

	elif request.method == 'GET':
		form.diagnoz.data = diagnoz.diagnoz

	return render_template('new_diagnoz.html', form = form)

@app.route('/delete_diagnoz/<diagnozid>', methods = ['GET', 'POST'])
@login_required
def delete_diagnoz(diagnozid):
	if current_user.role == 1:
		abort(404)

	diagnoz = Diagnoz.query.filter_by(id = diagnozid).first_or_404()
	medzdravaid = diagnoz.id_patient
	Diagnoz.query.filter_by(id = diagnozid).delete(synchronize_session = False)
	db.session.commit()
	return redirect(url_for('patient', medzdravaid = medzdravaid))

@app.route('/edit_allergen/<allergenid>', methods = ['GET', 'POST'])
@login_required
def edit_allergen(allergenid):
	if current_user.role == 1:
		abort(404)

	allergen = Allergen.query.filter_by(id = allergenid).first_or_404()
	form = NewAllergen()
	if form.validate_on_submit():
		allergen.allergen = form.allergen.data
		db.session.commit()
		return redirect(url_for('patient', medzdravaid = allergen.id_patient))
	elif request.method == 'GET':
		form.allergen.data = allergen.allergen

	return render_template('new_allergen.html', form = form)

@app.route('/delete_allergen/<allergenid>', methods = ['GET', 'POST'])
@login_required
def delete_allergen(allergenid):
	if current_user.role == 1:
		abort(404)

	allergen = Allergen.query.filter_by(id = allergenid).first_or_404()
	medzdravaid = allergen.id_patient
	Allergen.query.filter_by(id = allergenid).delete(synchronize_session = False)
	db.session.commit()
	return redirect(url_for('patient', medzdravaid = medzdravaid))

@app.route('/edit_post_image/<postid>', methods = ['GET', 'POST'])
@login_required
def edit_post_image(postid):
	if current_user.role != 3:
		abort(404)

	post = Blogpost.query.filter_by(id = int(postid)).first_or_404()

	form = NewPostForm()

	if form.validate_on_submit():
		file = form.main_image.data
		if file == None:
			filename = "post_default.png"
		else:
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['POST_IMAGE_SAVE_PATH'], filename))
	
		post.main_image_path = filename
		db.session.commit()
		return redirect(url_for('post', postid = post.id))	

	return render_template('edit_post_image.html', form = form, post = post)

@app.route('/vrachi_static')
def vrachi_static():
	return render_template('vrachi_static.html')

@app.route('/vrach_static')
def vrach_static():
	return render_template('vrach_test.html')

@app.route('/news')
def news():
	posts = Blogpost.query.all()
	for post in posts:
		post.title = smart_truncate(post.title, 60)
		post.content = smart_truncate(post.content, 400)

	return render_template('news.html', posts = posts)