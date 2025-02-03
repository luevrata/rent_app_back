from app.extensions import db
from sqlalchemy.orm import relationship

class TenancyTenants(db.Model):
    __tablename__ = 'tenancy_tenants'
    tenancy_id = db.Column(db.Integer, db.ForeignKey('tenancy.tenancy_id', ondelete='CASCADE'), primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.tenant_id', ondelete='CASCADE'), primary_key=True)

    # Relationships
    tenancy = relationship("Tenancy", back_populates="tenancy_tenants")
    tenant = relationship("Tenant", back_populates="tenancy_tenants")

    def __repr__(self):
        return f"<TenancyTenants TenancyID: {self.tenancy_id}, TenantID: {self.tenant_id}>"
