from datetime import datetime
from sqlalchemy import (
    TIMESTAMP,
    Column,
    ForeignKey,
    Integer,
    String,
    Enum,
    FLOAT,
    event,
)

from sqlalchemy.orm import Mapper
from factory.database import Base, SessionLocal
from sqlalchemy.orm import relationship, backref, Session
from factory import utils


class DSOrder(Base):
    __tablename__ = "ds_orders"

    id = Column(Integer, primary_key=True, nullable=False)
    customer_id = Column(
        Integer,
        ForeignKey("customers.id", ondelete="SET NULL"),
        nullable=True,
    )
    manager_id = Column(
        Integer,
        ForeignKey("managers.id"),
        nullable=True,
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now().astimezone(utils.LOCAL_TIME_ZONE),
    )
    ds_customer = relationship(
        "Customer", uselist=False, backref=backref("ds_customer")
    )
    ds_manager = relationship("Manager", uselist=False, backref=backref("ds_manager"))
    # if uselist is true, ds_order.order_detail expects list instead of model.
    ds_order_detail = relationship(
        "DSOrderDetails",
        uselist=False,
        backref=backref("ds_order_detail"),
        cascade="all, delete, delete-orphan",
    )


class DSOrderDetails(Base):
    __tablename__ = "ds_order_details"

    id = Column(Integer, primary_key=True, nullable=False)
    ds_order_id = Column(
        Integer, ForeignKey("ds_orders.id", ondelete="CASCADE"), nullable=False
    )
    depth = Column(FLOAT(precision=1), nullable=False)
    length_per_sheet = Column(FLOAT(precision=2), nullable=False)
    no_of_sheets = Column(Integer, nullable=False)
    total_length = Column(FLOAT(precision=4), nullable=False)
    thickness = Column(FLOAT(precision=2), nullable=False)
    zinc_grade = Column(Integer(), nullable=False)
    pick_up_time = Column(TIMESTAMP(timezone=True), nullable=False)
    production_stage = Column(Enum(utils.ProductionStage), nullable=False)
    notes = Column(String, nullable=True)


class CChannelOrder(Base):
    __tablename__ = "cchannel_orders"

    id = Column(Integer, primary_key=True, nullable=False)
    customer_id = Column(
        Integer,
        ForeignKey("customers.id", ondelete="SET NULL"),
        nullable=True,
    )
    manager_id = Column(
        Integer,
        ForeignKey("managers.id"),
        nullable=True,
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now().astimezone(utils.LOCAL_TIME_ZONE),
    )
    cchannel_customer = relationship(
        "Customer", uselist=False, backref=backref("cchannel_customer")
    )
    cchannel_manager = relationship(
        "Manager", uselist=False, backref=backref("cchannel_manager")
    )
    cchannel_order_detail = relationship(
        "CChannelOrderDetails",
        uselist=False,
        backref="cchannel_order_detail",
        cascade="all, delete, delete-orphan",
    )


class CChannelOrderDetails(Base):
    __tablename__ = "cchannel_order_details"
    id = Column(Integer, primary_key=True, nullable=False)
    cchannel_order_id = Column(
        Integer,
        ForeignKey("cchannel_orders.id", ondelete="CASCADE"),
        nullable=False,
    )
    channel_height = Column(FLOAT(precision=2), nullable=False)
    channel_width = Column(FLOAT(precision=2), nullable=False)
    holes = Column(String, nullable=True)
    length_per_sheet = Column(FLOAT(precision=2), nullable=False)
    no_of_sheets = Column(Integer, nullable=False)
    total_length = Column(FLOAT(precision=4), nullable=False)
    thickness = Column(FLOAT(precision=2), nullable=False)
    zinc_grade = Column(Integer(), nullable=False)
    pick_up_time = Column(TIMESTAMP(timezone=True), nullable=False)
    production_stage = Column(Enum(utils.ProductionStage), nullable=False)
    notes = Column(String, nullable=True)


class RoofOrder(Base):
    __tablename__ = "roof_orders"

    id = Column(Integer, primary_key=True, nullable=False)
    customer_id = Column(
        Integer,
        ForeignKey("customers.id", ondelete="SET NULL"),
        nullable=True,
    )
    manager_id = Column(
        Integer,
        ForeignKey("managers.id"),
        nullable=True,
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now().astimezone(utils.LOCAL_TIME_ZONE),
    )
    roof_customer = relationship(
        "Customer", uselist=False, backref=backref("roof_customer")
    )
    roof_manager = relationship(
        "Manager", uselist=False, backref=backref("roof_manager")
    )
    roof_order_detail = relationship(
        "RoofOrderDetails",
        uselist=False,
        backref="roof_order_detail",
        cascade="all, delete, delete-orphan",
    )


class RoofOrderDetails(Base):
    __tablename__ = "roof_order_details"
    id = Column(Integer, primary_key=True, nullable=False)
    roof_order_id = Column(
        Integer,
        ForeignKey("roof_orders.id", ondelete="CASCADE"),
        nullable=False,
    )
    color = Column(String, nullable=False)
    manufacturer = Column(Enum(utils.ColorPlainManufacturer), nullable=False)
    length_per_sheet = Column(FLOAT(precision=2), nullable=False)
    no_of_sheets = Column(Integer, nullable=False)
    total_length = Column(FLOAT(precision=4), nullable=False)
    thickness = Column(FLOAT(precision=2), nullable=False)
    pick_up_time = Column(TIMESTAMP(timezone=True), nullable=False)
    production_stage = Column(Enum(utils.ProductionStage), nullable=False)
    notes = Column(String, nullable=True)


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True, unique=True)
    address = Column(String, nullable=True)
    gender = Column(Enum(utils.Gender), nullable=False)


class Manager(Base):
    __tablename__ = "managers"
    id = Column(Integer, primary_key=True, nullable=False)
    type = Column(Enum(utils.ManagerType), nullable=False)
    name = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now().astimezone(utils.LOCAL_TIME_ZONE),
    )


class Transcation(Base):
    __tablename__ = "transcations"

    id = Column(Integer, primary_key=True, nullable=False)
    order_id = Column(Integer, nullable=False)
    product_type = Column(Enum(utils.Product), nullable=False)
    transcation_type = Column(Enum(utils.TransType), nullable=False)
    production_stage = Column(Enum(utils.ProductionStage), nullable=False)
    modified_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now().astimezone(utils.LOCAL_TIME_ZONE),
    )


class ManagerLog(Base):
    __tablename__ = "manager_logs"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=True)
    type = Column(Enum(utils.ManagerType), nullable=False)
    manager_id = Column(Integer, nullable=True)
    transcation_type = Column(Enum(utils.TransType), nullable=False)


class CustomerLog(Base):
    __tablename__ = "customer_logs"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    gender = Column(Enum(utils.Gender), nullable=False)
    customer_id = Column(Integer, nullable=True)
    transcation_type = Column(Enum(utils.TransType), nullable=False)


# this will work only with session.delete(obj) Not with query.delete()
@event.listens_for(Customer, "after_insert")
def receive_after_insert(mapper: Mapper, connection, target: Customer):
    new_trans_logs = CustomerLog(
        name=target.name,
        phone=target.phone,
        address=target.address,
        gender=target.gender,
        customer_id=target.id,
        transcation_type=utils.TransType.insert,
    )
    db: Session = SessionLocal()
    db.add(new_trans_logs)
    db.commit()
    db.close()


# this will work only with session.delete(obj) Not with query.delete()
@event.listens_for(Customer, "before_delete")
def receive_before_delete(mapper: Mapper, connection, target: Customer):
    new_trans_logs = CustomerLog(
        name=target.name,
        phone=target.phone,
        address=target.address,
        gender=target.gender,
        customer_id=target.id,
        transcation_type=utils.TransType.delete,
    )

    db: Session = SessionLocal()
    db.add(new_trans_logs)
    db.commit()
    db.close()


@event.listens_for(Manager, "after_insert")
def receive_after_insert(mapper: Mapper, connection, target: Manager):
    new_trans_logs = ManagerLog(
        name=target.name,
        type=target.type,
        manager_id=target.id,
        transcation_type=utils.TransType.insert,
    )
    db: Session = SessionLocal()
    db.add(new_trans_logs)
    db.commit()
    db.close()


@event.listens_for(Manager, "before_delete")
def receive_before_delete(mapper: Mapper, connection, target: Manager):
    new_trans_logs = ManagerLog(
        name=target.name,
        type=target.type,
        manager_id=target.id,
        transcation_type=utils.TransType.delete,
    )
    db: Session = SessionLocal()
    db.add(new_trans_logs)
    db.commit()
    db.close()


@event.listens_for(DSOrder, "after_insert")
def receive_after_insert(mapper: Mapper, connection, target: DSOrder):

    new_detail_log: DSOrderDetails = target.ds_order_detail

    transcations = Transcation(
        order_id=target.id,
        product_type=utils.Product.ds,
        transcation_type=utils.TransType.insert,
        production_stage=new_detail_log.production_stage,
    )
    db: Session = SessionLocal()
    db.add(transcations)
    db.commit()
    db.close()


@event.listens_for(DSOrder, "before_delete")
def receive_before_delete(mapper: Mapper, connection, target: DSOrder):
    new_detail_log: DSOrderDetails = target.ds_order_detail

    transcations = Transcation(
        order_id=target.id,
        product_type=utils.Product.ds,
        transcation_type=utils.TransType.delete,
        production_stage=new_detail_log.production_stage,
    )
    db: Session = SessionLocal()
    db.add(transcations)
    db.commit()
    db.close()


@event.listens_for(CChannelOrder, "after_insert")
def receive_after_insert(mapper: Mapper, connection, target: CChannelOrder):
    new_detail_log: CChannelOrderDetails = target.cchannel_order_detail
    transcations = Transcation(
        order_id=target.id,
        product_type=utils.Product.c_channel,
        transcation_type=utils.TransType.insert,
        production_stage=new_detail_log.production_stage,
    )
    db: Session = SessionLocal()
    db.add(transcations)
    db.commit()
    db.close()


@event.listens_for(CChannelOrder, "before_delete")
def receive_before_delete(mapper: Mapper, connection, target: CChannelOrder):
    new_detail_log: CChannelOrderDetails = target.cchannel_order_detail
    transcations = Transcation(
        order_id=target.id,
        product_type=utils.Product.c_channel,
        transcation_type=utils.TransType.delete,
        production_stage=new_detail_log.production_stage,
    )
    db: Session = SessionLocal()
    db.add(transcations)
    db.commit()
    db.close()


@event.listens_for(RoofOrder, "after_insert")
def receive_after_insert(mapper: Mapper, connection, target: RoofOrder):
    new_detail_log: RoofOrderDetails = target.roof_order_detail
    transcations = Transcation(
        order_id=target.id,
        product_type=utils.Product.roof,
        transcation_type=utils.TransType.insert,
        production_stage=new_detail_log.production_stage,
    )
    db: Session = SessionLocal()
    db.add(transcations)
    db.commit()
    db.close()


@event.listens_for(RoofOrder, "before_delete")
def receive_before_delete(mapper: Mapper, connection, target: RoofOrder):
    new_detail_log: RoofOrderDetails = target.roof_order_detail

    transcations = Transcation(
        order_id=target.id,
        production_stage=new_detail_log.production_stage,
        product_type=utils.Product.roof,
        transcation_type=utils.TransType.delete,
    )
    db: Session = SessionLocal()
    db.add(transcations)
    db.commit()
    db.close()


# WE DID NOT USE IT. THE TRANSCATION MODELS GOT DIRECTLY UPDATED IN THE ROUTERS->UPDATE METHODS.
# this will work only with query.update(). Not with session.update(obj)
# @event.listens_for(SessionLocal, "after_bulk_update")
# def receive_after_bulk_update(update_context):
#     print(f"mapper is {update_context.mapper.class_}")
#     print(type(update_context))
#     print(type(update_context.mapper))
#     print(f"updated the values are {update_context.values}")
