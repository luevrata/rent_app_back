from app.extensions import db
from sqlalchemy.orm import relationship

class GroupChat(db.Model):
    __tablename__ = 'group_chat'
    group_chat_id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(255), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.property_id'), unique=True, nullable=False)

    # Relationships
    property = relationship("Property", back_populates="group_chat")
    messages = relationship("Message", back_populates="group_chat")

    def __repr__(self):
        return f"<GroupChat ID: {self.group_chat_id}, Name: {self.group_name}>"