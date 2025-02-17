from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    influencer = db.relationship('Influencer', backref='user',uselist = False)
    sponsor = db.relationship('Sponsor', backref='user',uselist = False)
    flagged = db.Column(db.Boolean, default=False)

class Influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    Niche = db.Column(db.String(50), nullable=False)
    followers = db.Column(db.Integer, nullable=False)
    flagged = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(150), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.String(20), nullable=False)
    nich = db.Column(db.String(20),nullable=False)
    goals = db.Column(db.String(150), nullable=False)
    flagged = db.Column(db.Boolean, default=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)

class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    Industry = db.Column(db.String(150), nullable=False)
    budget = db.Column(db.Float, nullable=False)
    flagged = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    campaign = db.relationship('Campaign', backref="sponsor")

class Adreq(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'),nullable = False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'),nullable = True)
    message = db.Column(db.String(150), nullable=False)
    requirments = db.Column(db.String(150), nullable=False)
    payment = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(150), nullable=False)
    request_type = db.Column(db.String(50), nullable=False)  # 'public' or 'private

class campaign_req(db.Model):
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), primary_key=True)
    status = db.Column(db.String(150), nullable=False)
