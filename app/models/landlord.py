from app.extensions import db
from sqlalchemy.orm import relationship

class Landlord(db.Model):
    __tablename__ = 'landlord'
    landlord_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    user = relationship("User", back_populates="landlord")
    properties = relationship("Property", back_populates="landlord")

    def __repr__(self):
        return f"<Landlord ID: {self.landlord_id}>"