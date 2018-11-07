import os
import io
import string
import random
import re

import json
from six.moves.urllib.request import urlopen
from six.moves.urllib.parse import urlencode
from functools import wraps
from werkzeug.utils import secure_filename
from datetime import datetime

from flask import Flask, g, flash, send_file, render_template, url_for, abort, jsonify, redirect, request, make_response, session
import psycopg2

import db
import auth

app = Flask(__name__)

# def id_generator(size=13, chars=string.ascii_uppercase + string.digits):
#         return ''.join(random.SystemRandom().choice(chars) for _ in range(size))

@app.before_first_request
def initialize():
    db.setup()
    auth.setup()
    global auth0
    auth0 = auth.auth0

#Used to count number of tags by type
def countPost():
    numberOfType = []

    with db.get_db_cursor() as cur:
        cur.execute("SELECT tag.name, count(tag.name) as numberOfType from post_tag INNER JOIN tag ON post_tag.tag_id = tag.tag_id WHERE tag.type != 'Start Time' GROUP BY tag.name;")
        for row in cur:
            if row not in numberOfType:
                numberOfType.append(row)

    return numberOfType

def countTime():
    numberOfTime = []
    with db.get_db_cursor() as cur:
        cur.execute("SELECT tag.name, count(tag.name) as numberOfType from post_tag INNER JOIN tag ON post_tag.tag_id = tag.tag_id WHERE tag.type = 'Start Time' GROUP BY tag.name;")
        for row in cur:
            if row not in numberOfTime:
                numberOfTime.append(row)

    return numberOfTime

def countSize():
    numberOfSize = []
    with db.get_db_cursor() as cur:
        cur.execute("SELECT tag.name, count(tag.name) as numberOfType from post_tag INNER JOIN tag ON post_tag.tag_id = tag.tag_id WHERE tag.type = 'Size' GROUP BY tag.name;")
        for row in cur:
            if row not in numberOfSize:
                numberOfSize.append(row)

    return numberOfSize

# Protected Page. Only accessible after login
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in session:
            # Redirect to Login page here
            return redirect('/')
        return f(*args, **kwargs)

    return decorated

# uncomment following 3 lines when 404 page has been created.
# @app.errorhandler(404)
# def page_not_found(error):
#     return render_template("404.html"), 404


@app.route('/')
def home():
    return render_template("home.html")

# Auth0 callback after login


@app.route('/update', methods=['POST'])
def update():
    link_res = request.form.get("link")
    user_id = request.form.get("id")
    with db.get_db_cursor(commit=True) as cur:
        try:
            cur.execute("update register set avator=%s where id=%s",
                        (link_res,user_id))
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
    return redirect(url_for("profile"))

@app.route('/callback')
def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }

    with db.get_db_cursor(commit=True) as cur:

            # cur.execute("""IF EXISTS (SELECT * FROM register where user_id=%s) BEGIN END
            # ELSE BEGIN insert into register (name,user_id,avator) values (%s,%s,%s) END;""",(session.get('profile').get('user_id'),userinfo['name'],userinfo['sub'],userinfo['picture']))
        cur.execute("INSERT INTO register (user_id,name,avator) values (%s,%s,%s) ON CONFLICT (user_id) DO NOTHING;",
                    (userinfo['sub'], userinfo['name'], userinfo['picture']))
        # user_id_res=[record["user_id"] for record in cur]
        # if  user_id_res==session.get('profile').get('user_id'):
        #     return redirect('/')
        # else :
        #cur.execute("""insert into register (name,user_id,avator) values (%s,%s,%s)""", (userinfo['name'],userinfo['sub'],userinfo['picture']))

        # cur.execute("""IF EXISTS (SELECT * FROM register where user_id=%s) BEGIN END
        # ELSE BEGIN insert into register (name,user_id,avator) values (%s,%s,%s) END;""",(session.get('profile').get('user_id'),userinfo['name'],userinfo['sub'],userinfo['picture']))
        # cur.execute("INSERT INTO register (user_id,name,avator) values (%s,%s,%s) ON CONFLICT (user_id) DO NOTHING;",
        #             (userinfo['sub'], userinfo['name'], userinfo['picture']))
        # user_id_res=[record["user_id"] for record in cur]
        # if  user_id_res==session.get('profile').get('user_id'):
        #     return redirect('/')
        # else :
        #cur.execute("""insert into register (name,user_id,avator) values (%s,%s,%s)""", (userinfo['name'],userinfo['sub'],userinfo['picture']))

    return redirect('/')

# Auth0 Login
@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=os.environ['AUTH0_CALLBACK_URL'], audience='https://' + os.environ['AUTH0_DOMAIN']+'/userinfo')

# Auth0 Logout


@app.route('/logout')
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {'returnTo': url_for(
        'home', _external=True), 'client_id': os.environ['AUTH0_CLIENT_ID']}
    app.logger.info(auth0.api_base_url + '/v2/logout?' + urlencode(params))
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

# Profile Page
@app.route('/profile')
@requires_auth
def profile():
    #     with db.get_db_cursor() as cur:

    #             cur.execute("""select  name,email from register where id=%s;""",userinfo['sub']  )

    #             usr_name=[record["name"] for record in cur]
    #             usr_email=[record["email"] for record in cur]

    #             usr_name=[record["name"] for record in cur]
    #             usr_email=[record["email"] for record in cur]

    # return render_template('profile.html',usr_name=session.get('profile').get('name'),avator=session.get('profile').get('picture'))
    # with db.get_db_cursor() as cur:
    #     cur.execute("SELECT picture_id, filename FROM picture order by picture_id desc")
    #     images = [record for record in cur]
    with db.get_db_cursor() as cur:
        cur.execute("SELECT * FROM register where user_id=%s;",
                        (session.get('profile').get('user_id'),))
        user_id_res = [record["id"] for record in cur]
        tagsql = "select * from tag limit 40;"
        usersql = "select * from register where id = %s;"

        try:
            postsql = "SELECT *,picture_id FROM post,picture where post.post_id=picture.post_id and publisher_id=%s order by time DESC;"
           # postsql_all="""select picture_id from picture where post_id in (select * from post where publisher_id = %s order by time DESC);""";
            # Build tag array
            cur.execute(tagsql)
            tagArray = [dict((cur.description[i][0], value) \
               for i, value in enumerate(row)) for row in cur.fetchall()]
            #print(tagArray)

            #  Build users array
            cur.execute(usersql,(user_id_res[0],))
            userArray = [dict((cur.description[i][0], value) \
               for i, value in enumerate(row)) for row in cur.fetchall()]
            print(str(userArray[0]))

            # cur.execute(postsql,(user_id_res,))
            # post_id=[record["post_id"] for record in cur]
            # pictures_id=dict()
            # for i in post_id:
            #     cur.execute("SELECT * FROM picture where post_id=%s;",
            #                 (i,))
            #     picture_id=[record["picture_id"] for record in cur]
            #     pictures_id.append()
            cur.execute(postsql,(user_id_res[0],))
            postArray = [dict((cur.description[i][0], value) \
               for i, value in enumerate(row)) for row in cur.fetchall()]
            print(str(postArray))



        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
    return render_template('profile.html', userInfo=userArray[0], tagInfo=tagArray, postInfo=postArray)
# upload imaage into data base


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ['png', 'jpg']


# TODO For BATU, create upload to handle our form in profile html
@app.route('/upload', methods=['POST'])
def upload():
    title_res = request.form.get("title")
    status_res = request.form.get("status")
    location_res = request.form.get("location")
    budget_res = request.form.get("budget")
    text_res = request.form.get("text")
    tags_res = request.form.getlist("tags[]")
    print(str(tags_res))
    name_res = request.form.get("name")
    phone_res = request.form.get("phone")
    is_designer_res = request.form.get("designer")

    dt = datetime.now()

    if 'file' not in request.files:
        flash("no file part")
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash("no selected file")
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        # convert the flask object to a regular file object
        data = request.files['file'].read()

    with db.get_db_cursor(commit=True) as cur:
        # we are storing the original filename for demo purposes
        # might be useful to also/instead save the file extension or mime type

        cur.execute("SELECT * FROM register where user_id=%s;",
                    (session.get('profile').get('user_id'),))
        user_id_res = [record["id"] for record in cur]
        cur.execute("insert into post (publisher_id,time,title, status,location,budget,content) values (%s,%s,%s,%s,%s,%s, %s)",
                    (user_id_res[0], dt, title_res, status_res, location_res, budget_res, text_res))
        cur.execute(
            "SELECT MAX(post_id) AS maxid FROM post where publisher_id=%s;", (user_id_res[0],))
        post_id_res = [record["maxid"] for record in cur]
        cur.execute("insert into picture (register_id,post_id,img) values (%s,%s,%s)",
                    (user_id_res[0], post_id_res[0], data))
        for i in tags_res:
            cur.execute("insert into post_tag (post_id,tag_id) values (%s,%s)",
                        (post_id_res[0], i ))
        if (is_designer_res=="designer"):
            is_designer=True
        else:
            is_designer=False
        cur.execute("update register set name=%s,phone=%s,isDesigner=%s where id=%s",
                    (name_res, phone_res, is_designer,user_id_res[0]))

    return redirect(url_for("profile"))


@app.route('/img/<int:img_id>')
def serve_img(img_id):
    with db.get_db_cursor() as cur:
        cur.execute("SELECT * FROM picture where picture_id=%s", (img_id,))
        #cur.execute("SELECT * FROM picture;")
        image_row = cur.fetchone()

        # in memory binary stream
        stream = io.BytesIO(image_row["img"])

        return send_file(
            stream,
            attachment_filename="pic")

@app.route('/search', methods=['POST'])
def search():
    # get search type, '0' for team search '1' for client search
    type = request.form.get("type")
    # search text
    input = request.form.get("input")

    # Next improvement '[(\s)*(,|\.|;)+(\s)*]+'
    # Using regular expression to split search text
    inputArr = re.split('[,|\.|;|,\s|\.\s|;\s]+', input)

    # store db query results
    data = []

    # team search logic
    if type == '0':
        for item in inputArr:
            with db.get_db_cursor() as cur:
                cur.execute("SELECT register.avator, register.name, post.post_id, post.title, post.content, post.status, post.time, post.location, post.budget FROM post_tag INNER JOIN tag ON tag.tag_id=post_tag.tag_id INNER JOIN post ON post_tag.post_id=post.post_id INNER JOIN register ON post.publisher_id=register.id WHERE register.isdesigner and LOWER(tag.name) LIKE LOWER('%%%s%%');"
                            % (item))
                for row in cur:
                    if row not in data:
                        data.append(row)
         # Not matching data logic
        if not data:
            with db.get_db_cursor() as cur:
                cur.execute("SELECT register.avator, register.name, post.post_id, post.title, post.content, post.status, post.time, post.location, post.budget FROM post INNER JOIN register ON post.publisher_id=register.id WHERE register.isdesigner;")
                for row in cur:
                    if row not in data:
                        data.append(row)
    # client search
    if type == '1':
        for item in inputArr:
            with db.get_db_cursor() as cur:
                cur.execute("SELECT register.avator, register.name, post.post_id, post.title, post.content, post.status, post.time, post.location, post.budget FROM post_tag INNER JOIN tag ON tag.tag_id=post_tag.tag_id INNER JOIN post ON post_tag.post_id=post.post_id INNER JOIN register ON post.publisher_id=register.id WHERE NOT register.isdesigner and LOWER(tag.name) LIKE LOWER('%%%s%%');"
                            % (item))
                for row in cur:
                    if row not in data:
                        data.append(row)
        # Not matching data logic
        if not data:
            with db.get_db_cursor() as cur:
                cur.execute("SELECT register.avator, register.name, post.post_id, post.title, post.content, post.status, post.time, post.location, post.budget FROM post INNER JOIN register ON post.publisher_id=register.id WHERE NOT register.isdesigner;")
                for row in cur:
                    if row not in data:
                        data.append(row)

    # else:
    #     # get search type, '0' for team search '1' for client search
    #     type = request.form.get("type")
    #     # store db query results
    #     data = []

    #     # team search logic
    #     if type == '0':
    #         with db.get_db_cursor() as cur:
    #             cur.execute(
    #                 "SELECT post.post_id, post.title, post.content, post.status, post.location, post.budget FROM post INNER JOIN register ON post.publisher_id=register.id WHERE register.isdesigner;")
    #             for row in cur:
    #                 if row not in data:
    #                     data.append(row)
    #     # client search
    #     if type == '1':
    #         with db.get_db_cursor() as cur:
    #             cur.execute(
    #                 "SELECT post.post_id, post.title, post.content, post.status, post.location, post.budget FROM post INNER JOIN register ON post.publisher_id=register.id WHERE NOT register.isdesigner;")
    #             for row in cur:
    #                 if row not in data:
    #                     data.append(row)

    numberOfType = countPost()
    numberOfTime = countTime()
    numberOfSize = countTime()

    return render_template("search.html", type=type, data=data, numberOfType=numberOfType, numberOfSize=numberOfSize, numberOfTime=numberOfTime)

@app.route('/searchteam')
def searchteam():
    data = []
    with db.get_db_cursor() as cur:
                cur.execute("SELECT register.avator, register.name, post.post_id, post.title, post.content, post.status, post.time, post.location, post.budget FROM post INNER JOIN register ON post.publisher_id=register.id WHERE register.isdesigner;")
                for row in cur:
                    if row not in data:
                        data.append(row)

    numberOfType = countPost()

    return render_template("search.html", data=data, numberOfType=numberOfType)

@app.route('/searchclient')
def searchclient():
    data = []
    with db.get_db_cursor() as cur:
                cur.execute("SELECT register.avator, register.name, post.post_id, post.title, post.content, post.status, post.time, post.location, post.budget FROM post INNER JOIN register ON post.publisher_id=register.id WHERE NOT register.isdesigner;")
                for row in cur:
                    if row not in data:
                        data.append(row)

    numberOfType = countPost()

    return render_template("search.html", data=data, numberOfType=numberOfType)

@app.route('/post_info/<int:post_id>')
def post_info(post_id):
    tags=[]

    with db.get_db_cursor(commit=True) as cur:
        # we are storing the original filename for demo purposes
        # might be useful to also/instead save the file extension or mime type
        cur.execute("SELECT * FROM post where post_id=%s;",
                    (post_id,))
        postArray = [dict((cur.description[i][0], value) \
               for i, value in enumerate(row)) for row in cur.fetchall()]
        # user_id_res = [record["publisher_id"] for record in cur]
        # post_title_res = [record["title"] for record in cur]
        # post_time_res = [record["time"] for record in cur]
        # post_content_res = [record["content"] for record in cur]
        # # post_status_res = [record["status"] for record in cur]
        # post_location_res = [record["location"] for record in cur]
        # post_budget_res = [record["budget"] for record in cur]
        # post_area_res = [record["area"] for record in cur]
        # # post_tag_id_res = [record["tag_id"] for record in cur]
        # post_saved_times_res = [record["saved_times"] for record in cur]
        # post_closed_res = [record["closed"] for record in cur]
        # post_views_res = [record["views"] for record in cur]

        cur.execute("SELECT * FROM post_tag where post_id=%s;",
                    (post_id,))
        post_tags_id_res = [record["tag_id"] for record in cur]
        for i in post_tags_id_res:
            cur.execute("SELECT * FROM tag where tag_id=%s;",
                    (i,))
            tag_name=[record["name"] for record in cur]
            tags.append(tag_name[0])
        cur.execute("SELECT count(reviewer_id) as count FROM review where post_id=%s;",
                    (post_id,))
        count_reviewer_id=[record["count"] for record in cur]
        cur.execute("SELECT * FROM review where post_id=%s;",
                    (post_id,))
        commentArray = [dict((cur.description[i][0], value) \
               for i, value in enumerate(row)) for row in cur.fetchall()]
        # post_comment_res=[record["comment"] for record in cur]
        # post_comment_time=[record["time"] for record in cur]
        # post_comment_reviewer_id=[record["reviewer_id"] for record in cur]
        # post_comment_rate=[record["rate"] for record in cur]
        if (count_reviewer_id[0]>0):
            cur.execute("SELECT * FROM register where id=%s;",
                        (commentArray[0]["reviewer_id"],))
            commentArray_name_avator = [dict((cur.description[i][0], value) \
               for i, value in enumerate(row)) for row in cur.fetchall()]
            # post_comment_reviewer_name=[record["name"] for record in cur]
            # post_comment_reviewer_avator=[record["avator"] for record in cur]
        cur.execute("SELECT * FROM register where id=%s;",
                    (postArray[0]["publisher_id"],))
        post_user_Array = [dict((cur.description[i][0], value) \
               for i, value in enumerate(row)) for row in cur.fetchall()]
        # post_user_name=[record["name"] for record in cur]
        # post_user_avator=[record["avator"] for record in cur]
        # post_user_phone=[record["phone"] for record in cur]
        # post_user_email=[record["email"] for record in cur]
        # post_user_id=[record["user_id"] for record in cur]

        cur.execute("SELECT picture_id FROM picture where post_id=%s;",
                    (post_id,))
        post_pictures=[record["picture_id"] for record in cur]
        postArray[0]["views"]=postArray[0]["views"]+1
        cur.execute("update post set views=%s where post_id=%s;",
                        (postArray[0]["views"],post_id))
        toemail = post_user_Array[0]["email"]
        tophone = post_user_Array[0]["phone"]
        if not toemail:
            toemail = "no email avaliable"
        if not tophone:
            tophone = "no phone avaliable"

        if 'profile' not in session:
            return render_template("post_info.html",display_image=post_pictures[0], post_id_store=post_id,pop_login=0,post_title=postArray[0]["title"],
                                    user_profile_image=post_user_Array[0]["avator"],user_name=post_user_Array[0]["name"],team_client_description=postArray[0]["content"],
                                    tagArray=tags,phone = "log in to see", email = "log in to see",views=postArray[0]["views"],
                                    saved_time=postArray[0]["saved_times"])
        else:
            if (session.get('profile').get('user_id')==post_user_Array[0]["user_id"]):
                closed_tag_visible=1
                return render_template("post_info.html",display_image=post_pictures[0], post_id_store=post_id,pop_login=0,post_title=postArray[0]["title"],
                                         user_profile_image=post_user_Array[0]["avator"],user_name=post_user_Array[0]["name"],team_client_description=postArray[0]["content"],
                                            closed_tag_visible=1,tagArray=tags,phone = tophone, email = toemail,views=postArray[0]["views"],
                                    saved_time=postArray[0]["saved_times"])
            else:
                return render_template("post_info.html",display_image=post_pictures[0], post_id_store=post_id,pop_login=0,post_title=postArray[0]["title"],
                                         user_profile_image=post_user_Array[0]["avator"],user_name=post_user_Array[0]["name"],team_client_description=postArray[0]["content"],
                                            closed_tag_visible=0,tagArray=tags,phone = tophone, email = toemail,views=postArray[0]["views"],
                                    saved_time=postArray[0]["saved_times"])

@app.route('/post_info_upload/<int:post_id>',methods=['POST'])
def post_info_upload(post_id):
    saved_res = request.form.get("saved")
    closed_res = request.form.get("closed")
    #contact_res = request.form.get("contact")
    comment_content_res = request.form.get("comment_content")
    stars_res = request.form.get("stars")
    dt = datetime.now()

    with db.get_db_cursor(commit=True) as cur:
        # we are storing the original filename for demo purposes
        # might be useful to also/instead save the file extension or mime type
        cur.execute("SELECT * FROM post where post_id=%s;",
                    (post_id,))
        postArray = [dict((cur.description[i][0], value) \
               for i, value in enumerate(row)) for row in cur.fetchall()]
        # post_saved_times_res = [record["saved_times"] for record in cur]
        # post_closed_res = [record["closed"] for record in cur]
        # post_views_res = [record["views"] for record in cur]
        # user_id_res = [record["publisher_id"] for record in cur]
        cur.execute("SELECT * FROM register where id=%s;",
                    (postArray[0]["publisher_id"],))
        post_user_id=[record["user_id"] for record in cur]


        # postArray[0]["views"]=postArray[0]["views"]+1
        # cur.execute("insert into post (saved_times,closed,views) values (%s,%s, %s)",
        #             (post_saved_times_res[0], post_closed_res[0], post_views_res[0]))

        if 'profile' not in session:
            return redirect(url_for("post_info",post_id=post_id,pop_login=1))
        else:
            if (saved_res==1):
                postArray[0]["saved_times"]=postArray[0]["saved_times"]+1
            if (closed_res==1 and session.get('profile').get('user_id')==post_user_id[0]):
                postArray[0]["closed"]=True
            cur.execute("update post set saved_times=%s,closed=%s where post_id=%s;",(postArray[0]["saved_times"], postArray[0]["closed"],post_id))
            # cur.execute("insert into post (saved_times,closed) values (%s,%s)",
            #             (postArray[0]["saved_times"], postArray[0]["closed"]))
            cur.execute("SELECT * FROM register where user_id=%s;",
                            (session.get('profile').get('user_id'),))
            comment_user_id = [record["id"] for record in cur]
            cur.execute("insert into review (reviewer_id,comment,time,rate,post_id) values (%s,%s,%s,%s,%s)",
                        (comment_user_id[0], comment_content_res, dt, stars_res,post_id))
            if (saved_res==1):
                cur.execute("insert into post_saved (post_id,user_id) values (%s, %s)",
                        (post_id, comment_user_id[0]))
            return redirect(url_for("post_info",post_id=post_id,pop_login=0))

@app.route('/selfie',methods=['POST'])
def selfie():
    if 'file' not in request.files:
        flash("no file part")
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash("no selected file")
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        # convert the flask object to a regular file object
        data = request.files['file'].read()

        with db.get_db_cursor(commit=True) as cur:
            cur.execute("SELECT * FROM register where user_id=%s;",
                        (session.get('profile').get('user_id'),))
            user_id_res = [record["id"] for record in cur]
            cur.execute("update register set avator=%s where id=%s",
                        (data,user_id_res[0]))
    return redirect(url_for("profile"))


if __name__ == '__main__':
    app.run()
