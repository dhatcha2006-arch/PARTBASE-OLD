from datetime import datetime, timedelta
from app.extensions import db

class Area(db.Model):
    __tablename__ = "areas"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)

    users = db.relationship("User", backref="area", lazy=True)
    shops = db.relationship("Shop", backref="area", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "pincode": self.pincode,
            "lat": self.lat,
            "lng": self.lng
        }

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=True)
    area_id = db.Column(db.Integer, db.ForeignKey("areas.id"), nullable=True)
    lat = db.Column(db.Float, nullable=True)
    lng = db.Column(db.Float, nullable=True)
    is_phone_verified = db.Column(db.Boolean, default=False)
    active_role = db.Column(db.String(20), default="seeker")  # 'seeker' | 'employer'
    free_slots = db.Column(db.String(200), default="anytime")  # comma-separated: weekday_evening, weekend, anytime
    is_admin = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    seeker_profile = db.relationship("SeekerProfile", backref="user", uselist=False, lazy=True, cascade="all, delete-orphan")
    shop = db.relationship("Shop", backref="owner", uselist=False, lazy=True, cascade="all, delete-orphan")
    applications = db.relationship("Application", backref="seeker", lazy=True)
    tickets = db.relationship("Ticket", backref="raised_by", lazy=True)
    draft = db.relationship("Draft", backref="user", uselist=False, lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "phone": self.phone,
            "name": self.name,
            "area_id": self.area_id,
            "area_name": self.area.name if self.area else None,
            "is_phone_verified": self.is_phone_verified,
            "active_role": self.active_role,
            "free_slots": self.free_slots.split(",") if self.free_slots else [],
            "is_admin": self.is_admin,
            "is_blocked": self.is_blocked,
            "created_at": self.created_at.isoformat()
        }

class SeekerProfile(db.Model):
    __tablename__ = "seeker_profiles"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    interests = db.Column(db.String(255), default="")  # comma-separated: shop_helper, packing, data_entry, tutoring, delivery, event_staff
    free_slots = db.Column(db.String(100), default="anytime")
    rating_avg = db.Column(db.Float, default=0.0)
    jobs_completed = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "interests": [i.strip() for i in self.interests.split(",") if i.strip()],
            "free_slots": [s.strip() for s in self.free_slots.split(",") if s.strip()],
            "rating_avg": round(self.rating_avg, 1),
            "jobs_completed": self.jobs_completed
        }

class Shop(db.Model):
    __tablename__ = "shops"
    id = db.Column(db.Integer, primary_key=True)
    owner_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    shop_name = db.Column(db.String(150), nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey("areas.id"), nullable=True)
    lat = db.Column(db.Float, nullable=True)
    lng = db.Column(db.Float, nullable=True)
    verification_status = db.Column(db.String(30), default="unverified")  # unverified | pending | verified | rejected | info_requested
    proof_type = db.Column(db.String(20), nullable=True)  # photo | maps_link
    proof_value = db.Column(db.String(500), nullable=True)
    rating_avg = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)

    jobs = db.relationship("Job", backref="shop", lazy=True, cascade="all, delete-orphan")
    payments = db.relationship("Payment", backref="shop", lazy=True)

    @property
    def is_verified(self):
        return self.verification_status == "verified"

    def to_dict(self):
        return {
            "id": self.id,
            "shop_name": self.shop_name,
            "owner_name": self.owner_name,
            "address": self.address,
            "area_name": self.area.name if self.area else None,
            "verification_status": self.verification_status,
            "is_verified": self.is_verified,
            "rating_avg": round(self.rating_avg, 1),
            "rating_count": self.rating_count
        }

class Job(db.Model):
    __tablename__ = "jobs"
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey("shops.id"), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # shop_helper, delivery, event_staff, tutoring, data_entry, packing
    title = db.Column(db.String(150), nullable=False)
    day_option = db.Column(db.String(30), default="today")  # today | tomorrow | weekend
    job_date = db.Column(db.Date, nullable=True)
    start_time = db.Column(db.String(30), nullable=True)
    end_time = db.Column(db.String(30), nullable=True)
    time_range = db.Column(db.String(50), nullable=True)  # e.g. "5:00 pm to 9:00 pm"
    pay_amount = db.Column(db.Integer, nullable=False)
    pay_type = db.Column(db.String(20), default="hour")  # hour | day
    people_needed = db.Column(db.Integer, default=1)
    hired_count = db.Column(db.Integer, default=0)
    details = db.Column(db.Text, nullable=True)
    address = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default="open")  # pending_review | open | closed | hidden | deleted | completed
    is_boosted = db.Column(db.Boolean, default=False)
    boost_expires_at = db.Column(db.DateTime, nullable=True)
    view_count = db.Column(db.Integer, default=0)
    report_count = db.Column(db.Integer, default=0)
    scam_flag = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    applications = db.relationship("Application", backref="job", lazy=True, cascade="all, delete-orphan")
    reports = db.relationship("Report", backref="job", lazy=True, cascade="all, delete-orphan")
    views = db.relationship("View", backref="job", lazy=True, cascade="all, delete-orphan")
    payments = db.relationship("Payment", backref="job", lazy=True)

    @property
    def is_currently_boosted(self):
        if not self.is_boosted:
            return False
        if self.boost_expires_at and self.boost_expires_at < datetime.utcnow():
            return False
        return True

    @property
    def is_filled(self):
        return self.hired_count >= self.people_needed

    def to_dict(self, seeker_lat=None, seeker_lng=None):
        from app.utils.geo import haversine_distance, build_google_maps_url
        distance_km = None
        target_lat = self.shop.lat if self.shop and self.shop.lat else (self.shop.area.lat if self.shop and self.shop.area else None)
        target_lng = self.shop.lng if self.shop and self.shop.lng else (self.shop.area.lng if self.shop and self.shop.area else None)
        
        if seeker_lat is not None and seeker_lng is not None and target_lat and target_lng:
            distance_km = haversine_distance(seeker_lat, seeker_lng, target_lat, target_lng)

        area_name = self.shop.area.name if (self.shop and self.shop.area) else "Chennai"
        shop_title = self.shop.shop_name if self.shop else ""

        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "shop_name": shop_title,
            "shop_verified": self.shop.is_verified if self.shop else False,
            "shop_rating": round(self.shop.rating_avg, 1) if self.shop else 0.0,
            "shop_rating_count": self.shop.rating_count if self.shop else 0,
            "area_name": area_name,
            "day_option": self.day_option,
            "time_range": self.time_range or f"{self.start_time or ''} - {self.end_time or ''}",
            "pay_amount": self.pay_amount,
            "pay_type": self.pay_type,
            "pay_display": f"₹{self.pay_amount}/{self.pay_type}",
            "people_needed": self.people_needed,
            "hired_count": self.hired_count,
            "status": self.status,
            "is_boosted": self.is_currently_boosted,
            "distance_km": distance_km,
            "details": self.details,
            "created_at": self.created_at.isoformat(),
            "directions_url": build_google_maps_url(shop_title, area_name)
        }

class Application(db.Model):
    __tablename__ = "applications"
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    seeker_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    note = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default="applied")  # applied | shortlisted | hired | completed | withdrawn | rejected
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

    ratings = db.relationship("Rating", backref="application", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "job_id": self.job_id,
            "seeker_id": self.seeker_id,
            "seeker_name": self.seeker.name if self.seeker else "Seeker",
            "seeker_phone": self.seeker.phone if self.seeker else "",
            "note": self.note,
            "status": self.status,
            "applied_at": self.applied_at.isoformat()
        }

class View(db.Model):
    __tablename__ = "views"
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    seeker_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Rating(db.Model):
    __tablename__ = "ratings"
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"), nullable=True)
    rater_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    ratee_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    direction = db.Column(db.String(30), nullable=False)  # seeker_to_shop | shop_to_seeker
    stars = db.Column(db.Integer, nullable=False)  # 1 to 5
    positive_tags = db.Column(db.String(255), default="")  # comma-separated
    red_tags = db.Column(db.String(255), default="")       # comma-separated
    comment = db.Column(db.Text, nullable=True)
    revealed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    rater = db.relationship("User", foreign_keys=[rater_id], backref="ratings_given")
    ratee = db.relationship("User", foreign_keys=[ratee_id], backref="ratings_received")

    def to_dict(self):
        return {
            "id": self.id,
            "job_id": self.job_id,
            "stars": self.stars if self.revealed else None,
            "direction": self.direction,
            "revealed": self.revealed,
            "positive_tags": self.positive_tags.split(",") if self.positive_tags else [],
            "red_tags": self.red_tags.split(",") if self.red_tags else [],
            "comment": self.comment if self.revealed else None,
            "created_at": self.created_at.isoformat()
        }

class Report(db.Model):
    __tablename__ = "reports"
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    reporter_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    reason = db.Column(db.String(50), nullable=False)  # asked_money | fake_shop | wrong_location_pay | rude_unsafe | other
    details = db.Column(db.Text, nullable=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reporter = db.relationship("User", foreign_keys=[reporter_id], backref="reports_made")

class Ticket(db.Model):
    __tablename__ = "tickets"
    id = db.Column(db.Integer, primary_key=True)
    raised_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # seeker | employer
    issue_type = db.Column(db.String(50), nullable=False)  # scam_fee_request | fake_applicant | wrong_pay | boost_payment_failed | other
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=True)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default="open")  # open | in_review | resolved
    admin_reply = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    job = db.relationship("Job", foreign_keys=[job_id], backref="tickets")
    reports = db.relationship("Report", backref="ticket", lazy=True)

    @property
    def ticket_code(self):
        return f"T-{self.id}"

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.ticket_code,
            "role": self.role,
            "issue_type": self.issue_type,
            "job_id": self.job_id,
            "job_title": self.job.title if self.job else None,
            "description": self.description,
            "status": self.status,
            "admin_reply": self.admin_reply,
            "created_at": self.created_at.isoformat()
        }

class Payment(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey("shops.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    amount = db.Column(db.Integer, default=49)
    method = db.Column(db.String(20), default="upi")  # upi | card
    status = db.Column(db.String(20), default="success")  # pending | success | failed
    provider_ref = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "shop_id": self.shop_id,
            "job_id": self.job_id,
            "amount": self.amount,
            "method": self.method,
            "status": self.status,
            "provider_ref": self.provider_ref,
            "created_at": self.created_at.isoformat()
        }

class OTPRequest(db.Model):
    __tablename__ = "otp_requests"
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    code_hash = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    resend_available_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_locked(self):
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False

    def is_expired(self):
        return datetime.utcnow() > self.expires_at

    def can_resend(self):
        return datetime.utcnow() >= self.resend_available_at

class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # delete_job | dismiss_reports | warn_employer | verify_shop | reject_shop | reply_ticket | resolve_ticket | block_user
    target_type = db.Column(db.String(30), nullable=False)  # job | shop | ticket | user
    target_id = db.Column(db.Integer, nullable=False)
    note = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    admin = db.relationship("User", foreign_keys=[admin_id])

class Draft(db.Model):
    __tablename__ = "drafts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    payload = db.Column(db.Text, nullable=False)  # JSON string
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
