from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, relationship
from typing import List
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
import uuid

db = SQLAlchemy()
migrate = Migrate()


users_to_groups = db.Table(
    'users_to_groups',
    db.Column('group_id', db.String(122), db.ForeignKey('group.id')),
    db.Column('user_id', db.String(122), db.ForeignKey('user.id'))
)

group_to_permissions = db.Table(
    'group_to_permissions',
    db.Column('permission_id', db.String(122), db.ForeignKey('permission.id')),
    db.Column('group_id', db.String(122), db.ForeignKey('group.id')),
)


def generate_uuid():
    return str(uuid.uuid4())


class Permission(db.Model):
    id = db.Column(db.String(122), default=generate_uuid, primary_key=True)
    name = db.Column(db.String(122), unique=True)
    description = db.Column(db.Text(), nullable=True)
    groups: Mapped[List["Group"]] = relationship(
        secondary=group_to_permissions, back_populates='permissions'
    )

    @property
    def short(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

    @property
    def full(self):
        return {
            **self.short,
            'groups': [g.short for g in self.groups]
        }


class Group(db.Model):
    id = db.Column(db.String(122), default=generate_uuid, primary_key=True)
    name = db.Column(db.String(122), unique=True)
    users: Mapped[List["User"]] = relationship(
        secondary=users_to_groups, back_populates='groups'
    )
    permissions: Mapped[List[Permission]] = relationship(
        secondary=group_to_permissions, back_populates='groups'
    )

    @property
    def short(self) -> dict:
        return {
            'id': self.id,
            'name': self.name
        }

    @property
    def full(self) -> dict:
        return {
            **self.short,
            'users': [u.short for u in self.users],
            'permissions': [p.short for p in self.permissions]
        }


class User(db.Model):
    id = db.Column(db.String(122), default=generate_uuid, primary_key=True)
    active = db.Column(db.Boolean(), default=False)
    username = db.Column(db.String(122))
    name = db.Column(db.String(122))
    password_hash = db.Column(db.String(122))
    groups: Mapped[List[Group]] = relationship(
        secondary=users_to_groups, back_populates='users'
    )

    @property
    def permissions(self) -> List[str]:
        perms = []
        for group in self.groups:
            perms += [p.name for p in group.permissions]
        return list(set(perms))

    @property
    def short(self) -> dict:
        return {
            'id': self.id,
            'active': self.active,
            'username': self.username,
            'name': self.name,
        }

    @property
    def identity(self) -> dict:
        return {
            **self.short,
            'groups': [group.name for group in self.groups],
            'permissions': self.permissions
        }

    def has_permission(self, permission) -> bool:
        return permission in self.permissions

    @property
    def password(self) -> str:
        return self.password_hash

    @password.setter
    def password(self, value: str):
        self.password_hash = generate_password_hash(value)

    def check_pass(self, password: str) -> bool:
        if password is None:
            return False
        return check_password_hash(self.password_hash, password)
