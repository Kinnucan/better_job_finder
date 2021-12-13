from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import pprint
import sys
sys.path.append('../')
from scrapers import linkedin_scraping

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
CORS(app)

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Database of jobs


class Jobs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Float)
    job_title = db.Column(db.String(200), nullable=False)
    employer = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200))
    salary = db.Column(db.Integer, nullable=True)
    required_skills = db.Column(db.String(200), nullable=True)
    years_experience = db.Column(db.Integer, nullable=True)
    education_level = db.Column(db.String(200), nullable=True)
    employment_type = db.Column(db.String(200), nullable=True)
    job_post_link = db.Column(db.String(300), nullable=True)

    def __repr__(self):
        return '(Job Title: %r)' % self.job_title


db.drop_all()
db.create_all()
db.session.commit()


class JobsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Jobs

# Receives search data from the frontend and then returns a response object
@app.route("/getSearchResults", methods=['POST', 'GET'])
def getSearchResults():
    response_object = {'status': 'success'}
    print(request.get_json())

    if request.method == 'POST':
        db.session.query(Jobs).delete()
        db.session.commit()
        userSearch = dict(request.get_json())
        linkedinJobs = linkedin_scraping.main(userSearch)
        for job in linkedinJobs:
            job["required_skills"] = str(job["required_skills"])
            job["education_level"] = str(job["education_level"])
            db.session.add(Jobs(**job))
            db.session.commit()
        pp = pprint.PrettyPrinter()
        pp.pprint(linkedinJobs)
        return jsonify(linkedinJobs)
    else:
        jobs = Jobs.query.order_by(Jobs.score * -1).all()
        jobs_schema = JobsSchema(many=True)
        output = jobs_schema.dump(jobs)
        print(output)
        return jsonify(output)


if __name__ == '__main__':
    app.run(debug=True)
