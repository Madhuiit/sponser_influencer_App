from datetime import datetime
import numpy as np
from flask import Flask, render_template, redirect, request, session
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt
from models import db, User, Influencer, Campaign, Sponsor, Adreq, campaign_req


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'AB_CD'
db.init_app(app)

app.app_context().push()

@app.route('/')
def home():
    return render_template('user_deshboard.html')

@app.route('/register_influecer', methods=['GET', "POST"])
def influencer_register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        category = request.form.get("category")
        Nich = request.form.get("nich")
        followers = request.form.get("followers")
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print("User already Exist")
            return render_template('influencer_registration.html')
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()

            new_influencer = Influencer(username=username, password=password, category=category, Niche=Nich, followers=followers, user_id=new_user.id)
            db.session.add(new_influencer)
            db.session.commit()

            return render_template('user_deshboard.html')
    else:
        return render_template('influencer_registration.html')

@app.route('/register_sponser', methods=['GET', "POST"])
def sponser_register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        company_name = request.form.get("company_name")
        Industry = request.form.get("industry")
        budget = request.form.get("budget")
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print("User already Exist")
            return render_template('sponsor_registration.html')
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()

            new_sponsor = Sponsor(username=username, password=password, company_name=company_name, Industry=Industry, budget=budget, user_id=new_user.id)
            db.session.add(new_sponsor)
            db.session.commit()

            return render_template('user_deshboard.html')
    else:
        return render_template('sponsor_registration.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user is None:
            return render_template('user_deshboard.html')

        if user.username == "Admin":
            if user.password :
                return render_template('admin_dashboard.html')

        if user.flagged:
            return render_template('user_deshboard.html')

        sponsor = Sponsor.query.filter_by(username=username).first()
        if sponsor and not sponsor.flagged:
            if sponsor.password:
                session['username'] = sponsor.username
                return render_template('sponsor_profile.html', username= sponsor.username,id = sponsor.id,budget=sponsor.budget,company = sponsor.company_name)
            else:
                return render_template('user_deshboard.html')

        influencer = Influencer.query.filter_by(username=username).first()
        if influencer and not influencer.flagged:
            if influencer.password:
                session['username'] = influencer.username
                return render_template('influencer_profile.html', username= influencer.username,id = influencer.id,niche = influencer.Niche,category = influencer.category,followers = influencer.followers)
            else:
                flash('Incorrect password for Influencer.')
                return render_template('user_deshboard.html')

        return render_template('user_deshboard.html')

    return render_template('user_deshboard.html')
@app.route("/sponsor_profile")
def sponsor_profile():
    username = session.get("username")  # Corrected session usage
    sponsor = Sponsor.query.filter_by(username=username).first()  # Added .first()

    if sponsor is None:
        # Handle the case where no sponsor is found (e.g., redirect or show an error)
        return "Sponsor not found", 404

    return render_template(
        'sponsor_profile.html', 
        username=sponsor.username, 
        id=sponsor.id, 
        budget=sponsor.budget, 
        company=sponsor.company_name
    )

@app.route("/influencer_profile")
def influencer_profile():
    username = session.get("username")  # Corrected session usage
    influencer = Influencer.query.filter_by(username=username).first()  # Added .first()

    if influencer is None:
        # Handle the case where no sponsor is found (e.g., redirect or show an error)
        return "influencer not found", 404
        
    return render_template('influencer_profile.html', username= influencer.username,id = influencer.id,niche = influencer.Niche,category = influencer.category,followers = influencer.followers)

@app.route('/create_campaign', methods=['GET', 'POST'])
def create_campaign():
    if request.method == "POST":
        name = request.form.get('name')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        budget = request.form.get('budget')
        visibility = request.form.get('visibility')
        niche = request.form.get('niche')
        goals = request.form.get('goals')
        if 'username' in session:
            username = session['username']
            sponsor = Sponsor.query.filter_by(username=username).first()

        new_campaign = Campaign(name=name, description=description, start_date= datetime.strptime(start_date, '%m/%d/%Y'), end_date= datetime.strptime(end_date, '%m/%d/%Y'), budget=budget, visibility=visibility,nich =niche ,goals=goals, sponsor_id=sponsor.id)
        db.session.add(new_campaign)
        db.session.commit()
        return redirect('/go_to_campaign')

    return render_template('create_campaign.html')
@app.route("/go_to_campaign")
def go_to_campaign():
    if 'username' in session:
        username = session['username']
        sponsor = Sponsor.query.filter_by(username=username).first()
        campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()
        return render_template('go_to_campaign.html', campaigns=campaigns)
    return redirect('/login')
@app.route('/campaigns/<int:influencer_id>')
def campaigns(influencer_id):
    if 'username' in session:
        username = session['username']
        sponsor = Sponsor.query.filter_by(username=username).first()
        campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()
        return render_template('campaign_sponsor.html', campaigns=campaigns,influencer_id = influencer_id)
    return redirect('/login')

@app.route('/find_sponsor', methods=['GET', 'POST'])
def find_sponsor():
    influencers = []
    if request.method == 'POST':
        keyword = request.form.get('keyword')
        niche = request.form.get('niche')

        query = Influencer.query
        
        # Apply filters based on input
        if keyword and niche:
            # Filter by both keyword and niche
            query = query.filter(Influencer.username.ilike(f'%{keyword}%'), Influencer.Niche.ilike(f'%{niche}%'))
        elif keyword:
            # Filter only by keyword
            query = query.filter(Influencer.username.ilike(f'%{keyword}%'))
        elif niche:
            # Filter only by niche
            query = query.filter(Influencer.Niche.ilike(f'%{niche}%'))

        influencers = query.all()

    return render_template('find_sponsor.html', influencers=influencers)



@app.route('/find_campaign', methods=['GET', 'POST'])
def find_campaign():
    campaigns = []
    if request.method == 'POST':
        keyword = request.form.get('keyword')
        niche = request.form.get('niche')

        # Start with a base query
        query = Campaign.query.filter(Campaign.visibility == 'public')

        # Apply filters based on input
        if keyword and niche:
            # Filter by both keyword and niche
            query = query.filter(Campaign.name.ilike(f'%{keyword}%'), Campaign.nich.ilike(f'%{niche}%'))
        elif keyword:
            # Filter only by keyword
            query = query.filter(Campaign.name.ilike(f'%{keyword}%'))
        elif niche:
            # Filter only by niche
            query = query.filter(Campaign.nich.ilike(f'%{niche}%'))

        campaigns = query.all()

    return render_template('find_campaign.html', campaigns=campaigns)



@app.route('/create_request/<int:campaign_id>', methods=['GET', 'POST'])
def create_request(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    if campaign is None:
        return "Campaign not found!"
        
    influencer = Influencer.query.filter_by(username= session.get("username")).first()
    if not influencer:
        return "Influencer not found!"

    influencer_id = influencer.id
    status = "pending"
    new_request = campaign_req(campaign_id=campaign_id, influencer_id=influencer_id, status=status)
    db.session.add(new_request)
    db.session.commit()
    return "Request added successfully!"
@app.route("/sponsor_dashboard")
def sponsor_manage_req():
    username = session.get('username')
    if not username:
        return redirect('/login')

    sponsor = Sponsor.query.filter_by(username=username).first()
    campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()
    
    campaign_progress = []
    b = []
    
    for campaign in campaigns:
        requests = Adreq.query.filter_by(campaign_id=campaign.id, status='active').all()
        if requests: 
            total_time = campaign.end_date - campaign.start_date
            print( total_time, campaign.end_date , campaign.start_date)
            elapsed_time = datetime.now() - campaign.start_date
            print(elapsed_time , datetime.now() , campaign.start_date)
            progress = min((elapsed_time / total_time) * 100, 100)  # Cap at 100%
            campaign_progress.append({
                'campaign': campaign,
                'progress': progress
            })
    
        influencer_req = campaign_req.query.filter_by(campaign_id=campaign.id,status= "pending").first()
        if influencer_req is not None :
            b.append(influencer_req)
    
    return render_template('sponsor_dashboard.html', campaign_progress=campaign_progress, b = b)
    
    

@app.route('/update_request_status/<int:campaign_id>/<int:influencer_id>/<string:action>', methods=['POST'])
def update_request_status(campaign_id, influencer_id, action):
    # Retrieve the single request instance using .first()
    request = campaign_req.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()

    if not request:
        return "Request not found!"

    if action == 'accept':
        db.session.delete(request)
        db.session.commit
        new_request = campaign_req(campaign_id=campaign_id,influencer_id=influencer_id,status = "active")
        db.session.add(new_request)
    elif action == 'reject':
        # Delete the request instance
        db.session.delete(request)
    else:
        return "Invalid action!"

    db.session.commit()
    return redirect("/sponsor_dashboard")

@app.route('/update_request_status_influencer/<int:campaign_id>/<int:influencer_id>/<string:action>', methods=['GET','POST']) #update_request_status_influencer/1/None/accept
def update_request_status_influencer(campaign_id, influencer_id, action):
    # Retrieve the single request instance
    request = Adreq.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()
    if not request:
        return " request not found"
    else:
        message = request.message
        requirment = request.requirments
        payment = request.payment
        request_type = request.request_type

        if not request:
            return "Request not found!"

        if action == 'accept':
            db.session.delete(request)
            db.session.commit()
            new_add = Adreq(message=message, requirments=requirment, payment=payment, status= 'active', influencer_id=influencer_id,request_type=request_type ,campaign_id=campaign_id)
            db.session.add(new_add)
        elif action == 'reject':
            db.session.delete(request)
        else:
            return "Invalid action!"

    # Commit the changes to the database
        db.session.commit()

    return redirect("/influencer_dashboard")

@app.route('/create_req/<int:campaign_id>/<int:influencer_id>', methods=['GET', 'POST'])
def create_req(campaign_id,influencer_id):
    campaign = Campaign.query.get(campaign_id)
    if request.method == "POST":
        message = request.form.get('message')
        requirment = request.form.get("requirment")
        payment = request.form.get("payment")
        request_type = request.form.get('request_type')
        campaign_id = campaign.id

        influencer = Influencer.query.get(influencer_id)


        if request_type == 'private':
            influencer_id = influencer.id
        else:
            influencer_id = None

        new_add = Adreq(message=message, requirments=requirment, payment=payment, status= 'pending', influencer_id=influencer_id,request_type=request_type ,campaign_id=campaign.id)
        db.session.add(new_add)
        db.session.commit()
        add_reqs = Adreq.query.filter_by(campaign_id = campaign.id)

        return render_template("create_request_page.html",add_reqs=add_reqs)
    else:
        return render_template('create_request.html', campaign_id=campaign.id,influencer_id=influencer_id)

@app.route('/influencer_dashboard')
def influencer_dashboard():
    username = session.get('username')
    print(username)
    if not username:
        return redirect('/login')

    influencer = Influencer.query.filter_by(username=username).first()
    campaigns = Campaign.query.all()
    
    campaign_progress = []
    b = []

    
    for campaign in campaigns:
        requests = campaign_req.query.filter_by(campaign_id=campaign.id,influencer_id=influencer.id, status='active').all()
        if requests:
            total_time = campaign.end_date - campaign.start_date
            print( total_time, campaign.end_date , campaign.start_date)
            elapsed_time = datetime.now() - campaign.start_date
            print(elapsed_time , datetime.now() , campaign.start_date)
            progress = min((elapsed_time / total_time) * 100, 100)  # Cap at 100%
            campaign_progress.append({
                'campaign': campaign,
                'progress': progress
            })
        
        add_reqs = Adreq.query.filter_by(campaign_id=campaign.id,influencer_id=influencer.id ,status= "pending").first()
        print(add_reqs)
        if add_reqs is not None :
            b.append(add_reqs)
        

    return render_template('influencer_dashboard.html', campaign_progress=campaign_progress,sponsor_requests = b)
        
@app.route('/update_campaign/<int:campaign_id>', methods=['GET', 'POST'])
def update_campaign(campaign_id):
    campaign = Campaign.query.get(campaign_id) 

    if request.method == 'POST':
        campaign.name = request.form.get('name')
        campaign.description = request.form.get('description')
        campaign.start_date =  datetime.strptime(request.form.get('start_date'), '%m/%d/%Y')
        campaign.end_date =  datetime.strptime(request.form.get('end_date'), '%m/%d/%Y')
        campaign.budget = request.form.get('budget')
        campaign.visibility = request.form.get('visibility')  # Correct field name
        campaign.goals = request.form.get('goals')

        db.session.commit()
        return redirect('/go_to_campaign')

    return render_template('update.html', campaign=campaign)



@app.route('/delete_campaign/<int:campaign_id>', methods=['POST'])
def delete_campaign(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    db.session.delete(campaign)
    db.session.commit()
    return redirect('/campaigns')

#update and deletion of request
@app.route("/go_to_request")
def go_to_request():
    b = []
    if 'username' in session:
        username = session['username']
        sponsor = Sponsor.query.filter_by(username=username).first()
        campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()
        for campaign in campaigns:
            add_reqst =Adreq.query.filter_by(campaign_id = campaign.id ).all()
            for add_reqs in add_reqst:
                b.append(add_reqs)
        print(b)
        return render_template('create_request_page.html',add_reqs=b )



@app.route('/update_request/<int:request_id>', methods=['GET', 'POST'])
def update_request(request_id):
    req = Adreq.query.get(request_id)
    
    if req is None:
        return "Request not found"

    if request.method == "POST":
        req.requirments = request.form.get("requirment")
        req.payment = request.form.get("payment")
        req.request_type = request.form.get('request_type')
        db.session.commit()
        print("Request updated")
        return redirect('/go_to_request')

    return render_template('update_request.html', r=req)



@app.route('/delete_request/<int:request_id>', methods=['POST'])
def delete_request(request_id):
    req = Adreq.query.get(request_id)
    db.session.delete(req)
    db.session.commit()
    return redirect('/go_to_request')


 # this section implemetion for Admin above routs and methods for influencer and sponser
@app.route('/find_admin', methods=['GET', 'POST'])
def find_admin():
    search_results = {}

    if request.method == 'POST':
        keyword = request.form.get('keyword', '').strip()
        role = request.form.get('role', '').strip()

        # If keyword is None or empty, skip the filter or handle it as needed
        if keyword:
            if role == 'campaign':
                campaigns = Campaign.query.filter(
                    (Campaign.name.ilike(f'%{keyword}%')) |
                    (Campaign.description.ilike(f'%{keyword}%'))
                ).all()
                search_results['campaign'] = campaigns

            elif role == 'influencer':
                influencers = Influencer.query.filter(
                    (Influencer.username.ilike(f'%{keyword}%')) |
                    (Influencer.Niche.ilike(f'%{keyword}%'))
                ).all()
                search_results['influencer'] = influencers

            elif role == 'sponsor':
                sponsors = Sponsor.query.filter(
                    (Sponsor.username.ilike(f'%{keyword}%')) |
                    (Sponsor.company_name.ilike(f'%{keyword}%'))
                ).all()
                search_results['sponsor'] = sponsors
        else:
            # If keyword is empty, handle the case appropriately, such as returning all results
            if role == 'campaign':
                search_results['campaign'] = Campaign.query.all()
            elif role == 'influencer':
                search_results['influencer'] = Influencer.query.all()
            elif role == 'sponsor':
                search_results['sponsor'] = Sponsor.query.all()

    return render_template('find_admin.html', search_results=search_results)

@app.route('/flag/<entity>/<int:entity_id>', methods=['POST'])
def flag_entity(entity, entity_id):
    if entity == 'campaign':
        campaign = Campaign.query.get(entity_id)
        if campaign :
            campaign.flagged = True
            db.session.commit()
            return "campaign flagged sucessfully"
           
    elif entity == 'influencer':
        influencer = Influencer.query.get(entity_id)
        if influencer:
            influencer.flagged = True
            db.session.commit()
            return 'Influencer flagged successfully.'

            # Flag corresponding user
            user = User.query.filter_by(username=influencer.username).first()
            if user:
                user.flagged = True
                db.session.commit()

    elif entity == 'sponsor':
        sponsor = Sponsor.query.get(entity_id)
        if sponsor:
            sponsor.flagged = True
            db.session.commit()
            return 'Sponsor flagged successfully.'

            # Flag corresponding user
            user = User.query.filter_by(username=sponsor.username).first()
            if user:
                user.flagged = True
                db.session.commit()

    else:
        return 'Invalid entity type.'

    return redirect('/find_admin')

@app.route('/delete/<entity>/<int:entity_id>', methods=['POST'])
def delete_entity(entity, entity_id):
    if entity == 'campaign':
        campaign = Campaign.query.get(entity_id)
        if campaign:
            # Delete associated ads
            ads = Adreq.query.filter_by(campaign_id=campaign.id).all()
            for ad in ads:
                db.session.delete(ad)

            db.session.delete(campaign)
    elif entity == 'influencer':
        influencer = Influencer.query.get(entity_id)
        if influencer:
            user = User.query.filter_by(username=influencer.username).first()
            db.session.delete(influencer)
            if user:
                db.session.delete(user)
    elif entity == 'sponsor':
        sponsor = Sponsor.query.get(entity_id)
        if sponsor:
            user = User.query.filter_by(username=sponsor.username).first()
            db.session.delete(sponsor)
            if user:
                db.session.delete(user)

    db.session.commit()
    return redirect('/find_admin')

    
@app.route('/flagged_entities', methods=['GET'])
def flagged_entities():
    # Query for flagged entities
    flagged_campaigns = Campaign.query.filter_by(flagged=True).all()
    flagged_influencers = Influencer.query.filter_by(flagged=True).all()
    flagged_sponsors = Sponsor.query.filter_by(flagged=True).all()
    
    return render_template('flaged.html', 
                           flagged_campaigns=flagged_campaigns, 
                           flagged_influencers=flagged_influencers, 
                           flagged_sponsors=flagged_sponsors)
@app.route('/edit_influencer/<int:influencer_id>', methods=['GET', 'POST'])
def edit_influencer(influencer_id):
    influencer = Influencer.query.get(influencer_id)
    

    if influencer is None:
        return "Influencer not found"
    user = User.query.filter_by(username = influencer.username).first()

    if request.method == 'POST':
        influencer.username = request.form.get('username')
        influencer.password = request.form.get('password')
        influencer.category = request.form.get('category')
        influencer.Niche = request.form.get('Niche')
        influencer.followers = request.form.get('followers')
        if user:
            user.username = request.form.get('username')
            user.password = request.form.get("password")
        db.session.commit()
        
        return redirect('/login')  # Adjust the redirect as necessary

    return render_template('influencer_edit.html', influencer=influencer)

@app.route('/edit_sponsor/<int:sponsor_id>', methods=['GET', 'POST'])
def edit_sponsor(sponsor_id):
    sponsor = Sponsor.query.get(sponsor_id)

    if sponsor is None:
        return "Sponsor not found", 404

    user = User.query.filter_by(username=sponsor.username).first()  # Get the actual User object

    if request.method == 'POST':
        # Update Sponsor fields
        sponsor.company_name = request.form.get('company_name')
        sponsor.username = request.form.get('username')
        sponsor.password = request.form.get('password')
        sponsor.Industry = request.form.get('Industry')
        sponsor.budget = request.form.get('budget')

        # Update corresponding User fields
        if user:
            user.username = request.form.get('username')
            user.password = request.form.get("password")
        
        db.session.commit()
        return redirect('/login')  # Adjust the redirect as necessary

    return render_template('sponser_edit.html', sponsor=sponsor)
# Admin statistic
@app.route('/admin_stats')
def admin_stats():
    generate_plots()
    return render_template('admin_stats.html')

def generate_plots():
    active_campaigns = Campaign.query.filter_by(flagged=False).count()
    flagged_campaigns = Campaign.query.filter_by(flagged=True).count()

    plt.figure(figsize=(6, 4))
    plt.bar(['Active Campaigns', 'Flagged Campaigns'], [active_campaigns, flagged_campaigns], color=['green', 'red'])
    plt.title('Campaign Status')
    plt.ylabel('Number of Campaigns')
    plt.savefig('static/campaign_status.png')
    plt.close()

# Generate and save pie chart for flagged users
    flagged_influencers = Influencer.query.filter_by(flagged=True).count()
    flagged_sponsors = Sponsor.query.filter_by(flagged=True).count()

# Replace NaN values with 0
    flagged_influencers = 0 if np.isnan(flagged_influencers) else flagged_influencers
    flagged_sponsors = 0 if np.isnan(flagged_sponsors) else flagged_sponsors

    labels = ['Flagged Influencers', 'Flagged Sponsors']
    sizes = [flagged_influencers, flagged_sponsors]
    colors = ['orange', 'blue']

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.title('Flagged Users')
    plt.savefig('static/flagged_users.png')
    plt.close()
# sponser stats page
@app.route('/sponsor_stats')  # Make sure this matches what you're accessing
def sponsor_stats():
    username = session.get("username")
    
    sponsor = Sponsor.query.filter_by(username=username).first()
    sponsor_id = sponsor.id

    generate_sponsor_plots(sponsor_id)
    return render_template('sponsor_stats.html')


def generate_sponsor_plots(sponsor_id):
    # Retrieve all campaigns for the sponsor
    campaigns = Campaign.query.filter_by(sponsor_id=sponsor_id).all()
    
    if not campaigns:
        print(f"No campaigns found for sponsor ID {sponsor_id}")
        return

    active_campaigns = 0
    pending_campaigns = 0
    public_requests = 0
    private_requests = 0

    for campaign in campaigns:
        print(f"Processing campaign ID: {campaign.id} - Name: {campaign.name}")

        # Active and Pending Campaigns
        active_count = Adreq.query.filter_by(campaign_id=campaign.id, status='active').count()
        pending_count = Adreq.query.filter_by(campaign_id=campaign.id, status='pending').count()

        # Accumulate the totals
        active_campaigns += active_count
        pending_campaigns += pending_count

        # Public and Private Requests
        public_count = Adreq.query.filter_by(campaign_id=campaign.id, request_type='public').count()
        private_count = Adreq.query.filter_by(campaign_id=campaign.id, request_type='private').count()

        # Accumulate the totals
        public_requests += public_count
        private_requests += private_count

    # Debugging 

    # Plot generation (unchanged)
    plt.figure(figsize=(6, 4))
    plt.bar(['Active', 'Pending'], [active_campaigns, pending_campaigns], color=['green', 'orange'])
    plt.title('Campaign Status')
    plt.ylabel('Number of Campaigns')
    plt.savefig('static/campaign_status.png')
    plt.close()

    plt.figure(figsize=(6, 4))
    plt.bar(['Public Requests', 'Private Requests'], [public_requests, private_requests], color=['blue', 'purple'])
    plt.title('Request Type Distribution')
    plt.ylabel('Number of Requests')
    plt.savefig('static/flagged_users.png')
    plt.close()

@app.route('/influencer_stats')
def influencer_stats():
    username = session.get("username")
    influencer = Influencer.query.filter_by(username = username).first()
    influencer_id  = influencer.id
    generate_influencer_plots(influencer_id)
    return render_template('influencer_stats.html')

def generate_influencer_plots(influencer_id):
    # Ad Requests Sent vs. Accepted
    ad_requests_public = Adreq.query.filter_by(influencer_id=influencer_id, request_type="public").count()
    ad_requests_private = Adreq.query.filter_by(influencer_id=influencer_id, request_type='private').count()

    plt.figure(figsize=(6, 4))
    plt.bar(['Public Requests', 'Private Requests'], [ad_requests_public, ad_requests_private], color=['orange', 'green'])
    plt.title('Ad Request Status')
    plt.ylabel('Number of Requests')
    plt.savefig('static/campaign_status.png')
    plt.close()

    # Niche-wise Campaign Distribution
    campaign_reqs = campaign_req.query.filter_by(influencer_id=influencer_id).all()
    niche_count = {'fashion': 0, 'tech': 0, 'food': 0, 'fitness': 0}  # Example niches

    for req in campaign_reqs:
        campaign = Campaign.query.get(req.campaign_id)
        if campaign and campaign.nich in niche_count:
            niche_count[campaign.nich] += 1

    niches = list(niche_count.keys())
    niche_counts = list(niche_count.values())

    plt.figure(figsize=(6, 6))
    plt.pie(niche_counts, labels=niches, autopct='%1.1f%%', startangle=140)
    plt.title('Niche-wise Campaign Request')
    plt.savefig('static/flagged_users.png')
    plt.close()


@app.route("/admin_dashboard")
def admin_manage_req():

    campaigns = Campaign.query.all()
    
    campaign_progress = []
    
    for campaign in campaigns:

        requests = Adreq.query.filter_by(campaign_id=campaign.id, status='active').all()
        if requests: 
            total_time = campaign.end_date - campaign.start_date
            print( total_time, campaign.end_date , campaign.start_date)
            elapsed_time = datetime.now() - campaign.start_date
            print(elapsed_time , datetime.now() , campaign.start_date)
            progress = min((elapsed_time / total_time) * 100, 100)  # Cap at 100%
            campaign_progress.append({
                'campaign': campaign,
                'progress': progress
            })
            return render_template('admin_dashboard.html', campaign_progress=campaign_progress)
    return " Currentey there is no campaign Active"

@app.route('/logout')
def logout():
    session.clear()

    return redirect("/login")  

















if __name__ == '__main__':
    app.run(debug=True)
