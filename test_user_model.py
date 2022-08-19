"""User model tests."""

import os
from unittest import TestCase
from sqlalchemy import exc


from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test user model functionality"""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

        # User should have no likes
        self.assertEqual(len(u.likes), 0)

        # User should have correct string representation
        self.assertEqual(str(u), '<User #1: testuser, test@test.com>')


    def test_following(self):
        """Are following relationships handled correctly?"""

        user1 = User(
            id=2,
            email="user1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )

        user2 = User(
            id=3,
            email="user2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        ) 

        db.session.add_all([user1, user2])
        db.session.commit()
        
        follow = Follows(user_following_id=user1.id, user_being_followed_id=user2.id)

        db.session.add(follow)
        db.session.commit()

        self.assertTrue(user1.is_following(user2))
        self.assertFalse(user2.is_following(user1))
        self.assertFalse(user1.is_followed_by(user2))
        self.assertTrue(user2.is_followed_by(user1))


    def test_signup(self):
        """Do signup methods succeed and fail when they are supposed to?"""
        
        # valid signup
        user4 = User.signup("user4", "user4@test.com", "UNHASHED_PASSWORD", "/static/images/default-pic.png")
        
        db.session.commit()
        self.assertIsInstance(user4, User)

        # invalid signup, duplicate value on unique field
        with self.assertRaises(exc.IntegrityError):
            bad_user = User.signup("user5", user4.email, "some_password", "/static/images/default-pic.png")
            db.session.add(bad_user)
            db.session.commit()

        # rollback to flush bad_user
        db.session.rollback()

        # invalid signup, None value on non-nullable field
        with self.assertRaises(exc.IntegrityError):
            bad_user = User.signup(None, "bad_user@test.com", "some_password", "/static/images/default-pic.png")
            db.session.add(bad_user)
            db.session.commit()

        # rollback to flush bad_user
        db.session.rollback()

        # invalid signup, None value on non-nullable field
        with self.assertRaises(exc.IntegrityError):
            bad_user = User.signup("user5", None, "some_password", "/static/images/default-pic.png")
            db.session.add(bad_user)
            db.session.commit()

        # rollback to flush bad_user
        db.session.rollback()

        # invalid signup, None value on non-nullable field
        with self.assertRaises(ValueError):
            bad_user = User.signup("user5", "bad_user@test.com", None, "/static/images/default-pic.png")
            db.session.add(bad_user)
            db.session.commit()


    def test_authenticate(self):
        """Does authentication succeed and fail correctly?"""

        # sample user
        user5 = User.signup("user5", "user5@test.com", "UNHASHED_PASSWORD", "/static/images/default-pic.png")
        db.session.add(user5)
        db.session.commit()

        # check correct authentication
        self.assertIsInstance(User.authenticate("user5", "UNHASHED_PASSWORD"), User)

        db.session.rollback()

        # check incorrect (username) authentication
        self.assertNotIsInstance(User.authenticate("userwrong", "UNHASHED_PASSWORD"), User)

        db.session.rollback()

        # check incorrect (password) authentication
        self.assertNotIsInstance(User.authenticate("user5", "HASHED_PASSWORD"), User)
        