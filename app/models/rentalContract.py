from app.extensions import db
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint

class RentalContract(db.Model):
    __tablename__ = 'rental_contract'
    rental_contract_id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.tenant_id', ondelete='CASCADE'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.property_id', ondelete='CASCADE'), nullable=False)
    rent_due = db.Column(db.Numeric(10, 2), nullable=False)
    lease_start_date = db.Column(db.Date, nullable=False)
    lease_end_date = db.Column(db.Date)

    # Add unique constraint
    __table_args__ = (
        UniqueConstraint('tenant_id', 'property_id', name='rental_contract_tenant_id_property_id_key'),
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="rental_contracts")
    property = relationship("Property", back_populates="rental_contracts")

    def __repr__(self):
        return f"<RentalContract ID: {self.rental_contract_id}, TenantID: {self.tenant_id}, PropertyID: {self.property_id}>"