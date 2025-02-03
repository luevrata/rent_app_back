from app.extensions import db
from sqlalchemy.orm import relationship

class Property(db.Model):
    __tablename__ = 'property'
    property_id = db.Column(db.Integer, primary_key=True)
    landlord_id = db.Column(db.Integer, db.ForeignKey('landlord.landlord_id'), nullable=False)
    address = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="vacant")

    # Relationships
    landlord = relationship("Landlord", back_populates="properties")
    rental_contracts = relationship("RentalContract", back_populates="property")

    def to_dict(self):
        """
        Convert the property object to a dictionary.
        """
        return {
            'property_id': self.property_id,
            'landlord_id': self.landlord_id,
            'address': self.address,
            'status': self.status,
            'rental_contracts': [contract.contract_id for contract in self.rental_contracts] if self.rental_contracts else []
        }


    def __repr__(self):
        return f"<Property ID: {self.property_id}, Address: {self.address}>"