"""
Unit tests for models.py
"""

def test_new_user(new_user):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the username, password are defined correctly
    """
    assert new_user.username == 'testuser123'
    assert new_user.password != 'testuser123'
