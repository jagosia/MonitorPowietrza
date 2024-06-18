import json

class User:
    def __init__(self, id, name, lastname, email, phone, city, passwordHash, notification, lastNotification=None):
        self.id = id
        self.name = name
        self.lastname = lastname
        self.email = email
        self.phone = phone
        self.city = city
        self.passwordHash = passwordHash
        self.notification = notification
        self.lastNotification = lastNotification

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'lastname': self.lastname,
            'email': self.email,
            'phone': self.phone,
            'city': self.city,
            'passwordHash': self.passwordHash,
            'partition': self.lastname[0],
            'notification': self.notification,
            'lastNotification': self.lastNotification
        }

    def to_json(self):
        return json.dumps(self.to_dict())