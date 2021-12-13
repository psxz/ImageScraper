# -*- coding: utf-8 -*-
"""
Created on Sat Dec 11 02:43:13 2021

@author: Priyam
"""


from ScraperCore import ImageCrawler

from multiprocessing import Process
from pathlib import Path
import uuid, json

from flask import (
    Flask,
    request,
    make_response,
    jsonify
)

# from flask_apscheduler import APScheduler



app = Flask(__name__)


# For job submission.
@app.route('/jobs', methods=['POST'])
def Submit_Job():
    if request.method == "POST":
        try:
            content_type = request.headers.get('Content-Type')
            if (content_type == 'application/json'):
                JobInfo = request.get_json()
                JobInfo['job_id'] = str(uuid.uuid4())
                
                # Multiprocess class for this job.
                begin = processClass(JobInfo)
                
                filepath = "job_info/"+ JobInfo['job_id']
                Path(filepath).mkdir(parents=True, exist_ok=True)
                
                # Creating job info file to return.
                with open(filepath+'/info.txt', 'w') as outfile:
                    json.dump(JobInfo, outfile)
                
                # Creating job status file.
                status = {'completed': 0, 'in_progress': len(JobInfo['urls'])}
                with open(filepath+'/status.txt', 'w') as outfile:
                    json.dump(status, outfile)
                
                print(JobInfo)
                return make_response(jsonify(JobInfo), 200)
        
        except:
            return make_response('Invalid JSON', 400)
    

# For checking status of job.
@app.route('/jobs/<job_id>/status', methods=['GET'])
def Job_Status(job_id):
    if request.method == 'GET':
        try:
            filepath = "job_info/"+ job_id
            with open(filepath+'/status.txt', 'r') as outfile:
                data = json.load(outfile)
            
            return make_response(jsonify(data), 200)
        except:
            return make_response('Invalid job_id', 404)
    

# For getting result of completed job.
@app.route('/jobs/<job_id>/result', methods=['GET'])
def Job_Result(job_id):
    if request.method == 'GET':
        try:
            filepath = "job_info/"+ job_id
            with open(filepath+'/results.txt', 'r') as outfile:
                data = json.load(outfile)
            
            return make_response(jsonify(data), 200)
        except:
            return make_response('Invalid job_id or job still running', 404)


# Multiprocess worker class for each job.
class processClass:
    def __init__(self, JobInfo):
        self.JobInfo = JobInfo
        p = Process(target=self.run, args=())
        p.daemon = True
        p.start()

    def run(self):
        crawler = ImageCrawler(self.JobInfo['job_id'], self.JobInfo['urls'], self.JobInfo['workers'])
        crawler.scrape_site()





if __name__ == "__main__":
   app.run(debug= False, port= 8080, use_reloader=False)
   
   # scheduler = APScheduler()
   # scheduler.api_enabled = True
   # scheduler.init_app(app)
   # scheduler.start()
    
    
    
    
    
    
   