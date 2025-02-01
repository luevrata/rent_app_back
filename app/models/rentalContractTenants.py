from app.extensions import db
from sqlalchemy.orm import relationship

class RentalContractTenants(db.Model):
    __tablename__ = 'rental_contract_tenants'
    rental_contract_id = db.Column(db.Integer, db.ForeignKey('rental_contract.rental_contract_id', ondelete='CASCADE'), primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.tenant_id', ondelete='CASCADE'), primary_key=True)

    # Relationships
    rental_contract = relationship("RentalContract", back_populates="rental_contract_tenants")
    tenant = relationship("Tenant", back_populates="rental_contract_tenants")

    def __repr__(self):
        return f"<RentalContractTenants RentalContractID: {self.rental_contract_id}, TenantID: {self.tenant_id}>"
