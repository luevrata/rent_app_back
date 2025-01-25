from app.extensions import db
from sqlalchemy.orm import relationship

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="user", uselist=False)
    landlord = relationship("Landlord", back_populates="user")
    messages = relationship("Message", back_populates="sender")

    def __repr__(self):
        return f"<User {self.email}>"