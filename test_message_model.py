"""Message model tests"""

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()

class MessageModelTestCase(TestCase):
  """Test message model functionality"""

  def setUp(self):
    User.query.delete()
    Message.query.delete()
    Follows.query.delete()
    Likes.query.delete()

    self.client = app.test_client()

  def tearDown(self):
    db.session.rollback()

  def test_message_model(self):
    """Does basic model work?"""

    u = User(
      id=1,
      email="test@test.com",
      username="testuser",
      password="HASHED_PASSWORD"
    )

    message = Message(id=1, text="text message", user_id=u.id)

    db.session.add_all([u, message])
    db.session.commit()

    self.assertIsInstance(message, Message)
    self.assertEqual(str(message), "<Message 1>")
    self.assertEqual(message.user, u)


  def test_invalid_message(self):
    """Do invalid messages correctly fail in construction?"""

    # set up user
    u = User(
      id=1,
      email="test@test.com",
      username="testuser",
      password="HASHED_PASSWORD"
    )

    db.session.add(u)
    db.session.commit()

    # bad message - no text
    bad_message = Message(id=1, text=None, user_id=u.id)

    with self.assertRaises(exc.IntegrityError):
      db.session.add(bad_message)
      db.session.commit()

    # rollback to flush bad_message
    db.session.rollback()


    # bad message - no user id
    bad_message = Message(id=1, text="Test test test", user_id=None)

    with self.assertRaises(exc.IntegrityError):
      db.session.add(bad_message)
      db.session.commit()

    # rollback to flush bad message
    db.session.rollback()