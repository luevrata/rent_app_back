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

    def to_dict(self, include_property=False, include_messages=False):
        """
        Convert the GroupChat instance into a dictionary.

        Args:
            include_property (bool): Whether to include associated property details.
            include_messages (bool): Whether to include associated messages.

        Returns:
            dict: A dictionary representation of the GroupChat instance.
        """
        group_chat_dict = {
            "group_chat_id": self.group_chat_id,
            "group_name": self.group_name,
            "property_id": self.property_id,
        }

        if include_property and self.property:
            group_chat_dict["property"] = {
                "property_id": self.property.property_id,
                "address": self.property.address,
                "landlord_id": self.property.landlord_id,
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
