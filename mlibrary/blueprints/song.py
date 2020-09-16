"""
    :author: Jinfen Li
    :url: https://github.com/LiJinfen
"""

from flask import render_template, redirect, url_for, request, Blueprint, jsonify
from flask_login import current_user, login_required
from mlibrary.extensions import db
from mlibrary.forms import ProfileForm
from mlibrary.models import Song


song_bp = Blueprint('song', __name__)

online_users = []


@song_bp.route('/')
def index():

    if current_user.is_authenticated:

        return redirect(url_for('.home'))

    else:
        return render_template('auth/login.html')


@song_bp.route('/home')
def home():

    if current_user.is_authenticated:
        if current_user.is_admin:
            q1 = db.session.query(Song.name, Song.artist, db.func.count(Song.user_id)).group_by(Song.name, Song.artist).all()
            q2 = db.session.query(Song.artist, db.func.count(Song.user_id)).group_by(Song.artist).all()
            table1 = [[q[0], q[1],q[2]] for q in q1]
            table2 = [[q[0], q[1]] for q in q2]

            return render_template('song/admin_home.html', table1=table1, table2=table2)
        else:

            songs = Song.query.filter_by(user_id=current_user.id).all()
            allSongs = [[song.name, song.artist, song.createTime.strftime('%Y-%m-%d'), song.id] for song in songs]


            return render_template('song/user_home.html', songs=allSongs)
    else:
        return render_template('auth/login.html')


@song_bp.route('/createsong', methods=['POST'])
def createsong():


    name = request.form['name']
    artist = request.form['artist']
    song = Song.query.filter_by(user_id=current_user.id).all()

    for s in song:
        if s.name == name and s.artist == artist:
            return jsonify({"message": 'The song already exists, please re-enter.',
                            "result": 0,
                            "error": ''
                            })


    userHasSong = Song(user_id=current_user.id, name=name, artist=artist)

    db.session.add(userHasSong)
    db.session.commit()

    data={'name':userHasSong.name,'artist':userHasSong.artist,'time':userHasSong.createTime.strftime('%Y-%m-%d'), 'id':userHasSong.id,
          'deleteurl':url_for('song.deleteroom', song_id=userHasSong.id)}


    return jsonify({"message": 'successfully added to your library!',
                    "result": 1,
                    "error": '',
                    "data":data
                    })


@song_bp.route('/song/delete/<song_id>', methods=['DELETE'])
def deleteroom(song_id):

    Song.query.filter_by(id=song_id).delete()
    db.session.commit()
    return '', 204


@song_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.nickname = form.nickname.data
        current_user.github = form.github.data
        current_user.website = form.website.data
        current_user.bio = form.bio.data
        db.session.commit()
        return redirect(url_for('.home'))
    # flash_errors(form)
    return render_template('song/profile.html', form=form)