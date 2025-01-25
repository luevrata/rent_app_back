from app.extensions import db
from sqlalchemy.orm import relationship

class Message(db.Model):
    __tablename__ = 'message'
    message_id = db.Column(db.Integer, primary_key=True)
    group_chat_id = db.Column(db.Integer, db.ForeignKey('group_chat.group_chat_id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships
    group_chat = relationship("GroupChat", back_populates="messages")
    sender = relationship("User", back_populates="messages")

    def __repr__(self):
        return f"<Message ID: {self.message_id}, Content: {self.content[:30]}>"