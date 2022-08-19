"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        # reset database
        import seed
        sample_user = User.signup(username='sample_user', password='unhashed_password', email='sample_user@samp.com', image_url='')

        db.session.add(sample_user)
        db.session.commit()


    def tearDown(self):
        User.query.filter(User.username=='sample_user').delete()
        db.session.commit()


    def test_add_message(self):
        """Can use add a message?"""

        sample_user = User.query.filter(User.username=='sample_user').one()

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = sample_user.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.filter(Message.text=="Hello").one()
            self.assertEqual(msg.text, "Hello")


    def test_logged_in_messages(self):
        """    
        When you’re logged in, can you add a message as yourself?
        When you’re logged in, can you delete a message as yourself?
        """
        with app.test_client() as client:
            # login as sample_user
            sample_user = User.query.filter(User.username=='sample_user').one()
            resp = client.post("/login", data={'username': 'sample_user', 'password': 'unhashed_password'}, follow_redirects=True)
            self.assertIn('sample_user', resp.get_data(as_text=True))

            # Post new message
            resp = client.post('/messages/new', data={'text': 'Here\'s a message!'})
            
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.headers['location'], f'/users/{sample_user.id}')

            # Get message
            message_id = Message.query.filter(Message.text=='Here\'s a message!').one().id

            resp = client.get(f'/messages/{message_id}')
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Here&#39;s a message!', resp.get_data(as_text=True))

            # Delete message
            resp = client.post(f'/messages/{message_id}/delete')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.headers['location'], f'/users/{sample_user.id}')

            # Verify message does not appear
            resp = client.get(f'/users/{sample_user.id}')
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('Here&#39;s a message!', resp.get_data(as_text=True))

            # Verify message is gone
            self.assertIsNone(Message.query.get(message_id))


    def test_logged_out_messages(self):
        """
        When you’re logged out, are you prohibited from adding messages?
        When you’re logged out, are you prohibited from deleting messages?
        """
        with app.test_client() as client:
            # Ensure that we are logged out
            resp = client.get('/')

            self.assertIn('<a href="/signup" class="btn btn-primary">Sign up</a>', resp.get_data(as_text=True))

            # Post new message - should fail
            resp = client.post('/messages/new', data={'text': 'Here\'s a message!'})

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.headers['location'], '/')


            # Verify message does not exist
            self.assertEqual(len(Message.query.filter(Message.text=='Here\'s a message!').all()), 0)


            # get sample message to attempt deletion of
            sample_message = Message.query.first()

            # Delete message - should fail
            resp = client.post(f'/messages/{sample_message.id}/delete')
            
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.headers['location'], '/')

            # verify message is still there
            self.assertIsInstance(Message.query.get(sample_message.id), Message)

            # placeholder
            self.assertTrue(True)


    def test_other_user_msgs(self):
        """
        When you’re logged in, are you prohibiting from adding a message as another user? -Note, there is no interface or route logic to even attempt this, posting a new message verifies the user from the session and a user id cannot be passed to a new message.

        When you’re logged in, are you prohibiting from deleting a message as another user?
        """
        with app.test_client() as client:
            # login as sample_user
            resp = client.post("/login", data={'username': 'sample_user', 'password': 'unhashed_password'}, follow_redirects=True)
            self.assertIn('sample_user', resp.get_data(as_text=True))

            # get user to look at
            example_user_id = 1

            # get example sample_message
            sample_message = Message.query.filter(Message.user_id==example_user_id).first()

            # Delete message - should fail
            resp = client.post(f'/messages/{sample_message.id}/delete')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.headers['location'], '/')

            # Verify message still exists
            self.assertIsInstance(Message.query.get(sample_message.id), Message)

            # Verify can still view message
            resp = client.get(f'/messages/{sample_message.id}')

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<li class="list-group-item">', resp.get_data(as_text=True))

