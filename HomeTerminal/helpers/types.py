"""
Custom made types
"""


class Notification:
    """
    used to store each notfication for the user
    """
    def __init__(self, content, category="message"):
        self.content = content
        self.category = category
