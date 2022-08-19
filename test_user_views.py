"""User model tests."""


import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app
app.config['WTF_CSRF_ENABLED'] = False

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserViewsTestCase(TestCase):
  """Test User Views"""

  def setUp(self):
    # reset database
    import seed
    sample_user = User.signup(username='sample_user', password='unhashed_password', email='sample_user@samp.com', image_url='')

    db.session.add(sample_user)
    db.session.commit()


  def tearDown(self):
    User.query.filter(User.username=='sample_user').delete()
    db.session.commit()


  def test_logged_in_follow_views(self):
    with app.test_client() as client:
      """When you’re logged in, can you see the follower / following pages for any user?
      """

      # login as sample_user
      resp = client.post("/login", data={'username': 'sample_user', 'password': 'unhashed_password'}, follow_redirects=True)
      self.assertIn('sample_user', resp.get_data(as_text=True))

      # get user to look at
      example_user_id = 1

      # get that user's followers
      resp = client.get(f"/users/{example_user_id}/followers")

      self.assertEqual(resp.status_code, 200)
      html = resp.get_data(as_text=True)
      self.assertIn("card user-card", html)


      # get that user's follows
      resp = client.get(f"/users/{example_user_id}/following")

      self.assertEqual(resp.status_code, 200)
      html = resp.get_data(as_text=True)
      self.assertIn("card user-card", html)


  def test_logged_out_follow_views(self):
    """When you’re logged out, are you disallowed from visiting a user’s follower / following pages?
    """
    with app.test_client() as client:
      # login as sample_user
      resp = client.post("/login", data={'username': 'sample_user', 'password': 'unhashed_password'}, follow_redirects=True)
      self.assertIn('sample_user', resp.get_data(as_text=True))

      # get user to look at
      example_user_id = 1




