from app import db

from app.models import User, Event, Blogpost

from datetime import datetime


def show_users():
	users = User.query.all()
	
	print('These are current registered users')
	print('--------------')
	for user in users:
		print("User number: " + str(user.id))
		print(user.second_name + " " + user.first_name + " " + user.middle_name)
		if user.role == 1:
			print("User role is: Pateint")
		elif user.role == 2:
			print("User role is: Vrach")
		else:
			print("User role is Administrtor.")
		if user.sex == 1:
			print("Female")
		else:
			print("Male")
		print("User phone number is " + str(user.phonenumber))
		print("Addresss: " + user.address)
		print("--------------")

def show_events():
	events = Event.query.all()
	print("--------------")
	for event in events:
		print(event.id)
		print(event.event_name)
		print(event.zacklucheniye)
		print(event.datetime)
		print(event.vrach_id)
		print(event.patient_id)
		print("--------------")

def show_user(id):
	user = User.query.filter(User.id == id).first_or_404()
	print("User number: " + str(user.id))
	print(user.second_name + " " + user.first_name + " " + user.middle_name)
	if user.role == 1:
		print("User role is: Pateint")
	elif user.role == 2:
		print("User role is: Vrach")
	else:
		print("User role is Administrtor.")
	if user.sex == 1:
		print("Female")
	else:
		print("Male")
	print("User phone number is " + str(user.phonenumber))
	print("Addresss: " + user.address)
	print("--------------")

def show_event(id):
	event = Event.query.filter(Event.id == id).first_or_404()
	print(event.id)
	print(event.event_name)
	print(event.zacklucheniye)
	print(event.datetime)
	print(event.id_vrach)
	print(event.id_patient)
	print("--------------")

def show_posts():
	posts = Blogpost.query.all()
	for post in posts:
		print(post.id)
		print(post.title)
		print(post.datetime)
		print(post.is_in_slider)


def fill_patients(number):
	for n in range(number):
		user = User(
			role = 1,
			first_name = n,
			second_name = "test",
			middle_name = n,
			email = "test@test.test",
			sex = 1,
			birthdate = datetime.utcnow(),
			address = "testing address",
			phonenumber = 666666666
			)
		user.set_password("")
		db.session.add(user)
		db.session.commit()
	print("Successfully added " + str(n + 1) + " testing patients.")

def fill_vrachi(number):
	for n in range(number):
		user = User(
			role = 2,
			first_name = n,
			second_name = "test",
			middle_name = n,
			email = "test@test.test",
			sex = 1,
			birthdate = datetime.utcnow(),
			address = "testing address",
			phonenumber = 666666666
			)
		user.set_password("")
		db.session.add(user)
		db.session.commit()
	print("Successfully added " + str(n + 1) + " testing doctors.")

def fill_admins(number):
	for n in range(number):
		user = User(
			role = 3,
			first_name = n,
			second_name = "test",
			middle_name = n,
			email = "test@test.test",
			sex = 1,
			birthdate = datetime.utcnow(),
			address = "testing address",
			phonenumber = 666666666
			)
		user.set_password("")
		db.session.add(user)
		db.session.commit()
	print("Successfully added " + str(n + 1) + " testing admins.")


def delete_testing():
	User.query.filter(User.second_name.like('%test%')).delete(synchronize_session = False)
	db.session.commit()
	print('Successfully delete all testing user.')

def session_commit():
	db.session.commit()
	print('Successfully commited session')