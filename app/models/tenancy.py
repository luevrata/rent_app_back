from app.extensions import db
from sqlalchemy.orm import relationship

class Tenancy(db.Model):
    __tablename__ = 'tenancy'
    tenancy_id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.property_id', ondelete='CASCADE'), nullable=False)
    rent_due = db.Column(db.Numeric(10, 2), nullable=False)
    lease_start_date = db.Column(db.Date, nullable=False)
    lease_end_date = db.Column(db.Date, nullable=True) 
    group_chat_id = db.Column(db.Integer, db.ForeignKey('group_chat.group_chat_id'), unique=True, nullable=False)

    # Relationships
    property = relationship("Property", back_populates="tenancies")
    group_chat = relationship("GroupChat", back_populates="tenancy")
    tenancy_tenants = relationship(
        "TenancyTenants", back_populates="tenancy"
    )

    def __repr__(self):
        return f"<Tenancy ID: {self.tenancy_id}, PropertyID: {self.property_id}>"