from app.extensions import db
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint

class RentalContract(db.Model):
    __tablename__ = 'rental_contract'
    rental_contract_id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.property_id', ondelete='CASCADE'), nullable=False)
    rent_due = db.Column(db.Numeric(10, 2), nullable=False)
    lease_start_date = db.Column(db.Date, nullable=False)
    lease_end_date = db.Column(db.Date)
    group_chat_id = db.Column(db.Integer, db.ForeignKey('group_chat.group_chat_id'), unique=True, nullable=False)

    # Relationships
    property = relationship("Property", back_populates="rental_contracts")
    group_chat = relationship("GroupChat", back_populates="rental_contract")
    rental_contract_tenants = relationship(
        "RentalContractTenants", back_populates="rental_contract"
    )

    def __repr__(self):
        return f"<RentalContract ID: {self.rental_contract_id}, PropertyID: {self.property_id}>"
