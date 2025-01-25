from app.extensions import db
from sqlalchemy.orm import relationship

class Property(db.Model):
    __tablename__ = 'property'
    property_id = db.Column(db.Integer, primary_key=True)
    landlord_id = db.Column(db.Integer, db.ForeignKey('landlord.landlord_id'), nullable=False)
    address = db.Column(db.Text, nullable=False)

    # Relationships
    landlord = relationship("Landlord", back_populates="properties")
    group_chat = relationship("GroupChat", uselist=False, back_populates="property")
    rental_contracts = relationship("RentalContract", back_populates="property")

    def __repr__(self):
        return f"<Property ID: {self.property_id}, Address: {self.address}>"