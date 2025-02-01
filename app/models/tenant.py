from app.extensions import db
from sqlalchemy.orm import relationship

class Tenant(db.Model):
    __tablename__ = 'tenant'
    tenant_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    user = relationship("User", back_populates="tenant")

    # Relationships
    rental_contract_tenants = relationship(
        "RentalContractTenants", back_populates="tenant"
    )

    def __repr__(self):
        return f"<Tenant ID: {self.tenant_id}>"