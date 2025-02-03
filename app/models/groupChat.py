from app.extensions import db
from sqlalchemy.orm import relationship

class GroupChat(db.Model):
    __tablename__ = 'group_chat'
    group_chat_id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(255), nullable=False)

    # Relationships
    messages = relationship("Message", back_populates="group_chat")
    tenancy = relationship("Tenancy", back_populates="group_chat", uselist=False)

    def __repr__(self):
        return f"<GroupChat ID: {self.group_chat_id}, Name: {self.group_name}>"

    def to_dict(self, include_messages=False):
        """
        Convert the GroupChat instance into a dictionary.

        Args:
            include_messages (bool): Whether to include associated messages.

        Returns:
            dict: A dictionary representation of the GroupChat instance.
        """
        group_chat_dict = {
            "group_chat_id": self.group_chat_id,
            "group_name": self.group_name,
        }

        if include_messages:
            group_chat_dict["messages"] = [
                {
                    "message_id": message.message_id,
                    "content": message.content,
                    "timestamp": message.timestamp,
                    "sender_id": message.sender_id,
                }
                for message in self.messages
            ]

        return group_chat_dict
