import database, os, util, bcrypt
import os
import util


UPLOAD_FOLDER_FOR_QUESTIONS = 'static/images/questions/'
UPLOAD_FOLDER_FOR_ANSWERS = 'static/images/answers/'

def check_password_repeat(password, password_repeat):
    return password == password_repeat

def hash_password(user_input):
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(user_input.encode(encoding="utf-8"), salt)
    return hash.hex()

@database.connection_handler
def check_if_user_exists(cursor, login:str):
    query = """
    SELECT login
    FROM users
    WHERE login = %(login)s
    """
    data = {'login': login}
    cursor.execute(query, data)
    return cursor.fetchone()

@database.connection_handler
def get_password_from_base(cursor, login):
    query = """
    SELECT password
    FROM users
    WHERE login = %(login)s
    """
    data = {'login': login}
    cursor.execute(query, data)
    return cursor.fetchone()

def check_password(password:str, password_from_base:hex):
    password_bytes = bytes.fromhex(password_from_base)
    return bcrypt.checkpw(password.encode(encoding="utf-8"), password_bytes)

@database.connection_handler
def get_user_id(cursor, login):
    query = """
        SELECT id
        FROM users
        WHERE login = %(login)s
        """
    data = {'login': login}
    cursor.execute(query, data)
    return cursor.fetchone()

@database.connection_handler
def add_new_user(cursor, login:str, password:hex, current_date:str):
    query = """
          INSERT INTO users (login, password, registration_date) 
          VALUES (%(login)s, %(password)s, %(date)s); """
    data = {'login': login, 'password': password, 'date': current_date}
    cursor.execute(query, data)

@database.connection_handler
def get_users_list(cursor):
    query = """
        SELECT u.id, u.login, u.registration_date, 
            COUNT(DISTINCT q.id) AS num_questions,
            COUNT(DISTINCT a.id) AS num_answers,
            COUNT(DISTINCT c.id) AS num_comments
        FROM users u
        LEFT JOIN question q ON u.id = q.author
        LEFT JOIN answer a ON u.id = a.author
        LEFT JOIN comment c ON u.id = c.author
        GROUP BY u.id;
       """
    cursor.execute(query)
    return cursor.fetchall()

@database.connection_handler
def get_user_data(cursor, user_id):
    query = """
        SELECT u.id, u.login, u.registration_date, 
            COUNT(DISTINCT q.id) AS num_questions,
            COUNT(DISTINCT a.id) AS num_answers,
            COUNT(DISTINCT c.id) AS num_comments
        FROM users u
        LEFT JOIN question q ON u.id = q.author
        LEFT JOIN answer a ON u.id = a.author
        LEFT JOIN comment c ON u.id = c.author
        WHERE u.id = %(id)s
        GROUP BY u.id;
       """
    data = {'id': user_id}
    cursor.execute(query, data)
    return cursor.fetchone()

@database.connection_handler
def get_user_questions(cursor, user_id):
    query = """
    SELECT id, submission_time, title, message
    FROM question
    WHERE author = %(user_id)s
    """
    data = {'user_id': user_id}
    cursor.execute(query, data)
    return cursor.fetchall()

@database.connection_handler
def get_user_answers(cursor, user_id):
    query = """
    SELECT id, submission_time, message 
    FROM answer
    WHERE author = %(user_id)s
    """
    data = {'user_id': user_id}
    cursor.execute(query, data)
    return cursor.fetchall()

@database.connection_handler
def get_all_questions(cursor, order_by, order_direction):
    if order_direction == "DESC":
        query = """
            SELECT id, submission_time, view_number, vote_number, title, message, 
            COALESCE((SELECT COUNT(answer.question_id)
            FROM answer 
            WHERE answer.question_id = question.id GROUP by answer.question_id), 0) as answer_number, 
            (SELECT login FROM users WHERE id = question.author) as author_name
            FROM question
            ORDER BY {} DESC
            """.format(order_by)
    else: 
        query = """
        SELECT id, submission_time, view_number, vote_number, title, message, 
        COALESCE((SELECT COUNT(answer.question_id)
              FROM answer 
              WHERE answer.question_id = question.id GROUP by answer.question_id), 0) as answer_number
        FROM question
        ORDER BY {} ASC
        """.format(order_by)

    data = {'order': order_by}
    cursor.execute(query, data)
    return cursor.fetchall()


@database.connection_handler
def get_questions_number(cursor):
    query = """
        SELECT COUNT(*) as count_questions
        FROM question 
       """
    cursor.execute(query)
    return cursor.fetchone()


@database.connection_handler
def get_latest_questions(cursor, number_of_questions:int):
    query = """
        SELECT id, submission_time, view_number, vote_number, title, message, 
        COALESCE((SELECT COUNT(answer.question_id)
        FROM answer 
        WHERE answer.question_id = question.id 
        GROUP by answer.question_id), 0) as answer_number,
        (SELECT login FROM users WHERE id = question.author) as author_name
        FROM question
        ORDER BY submission_time DESC 
        LIMIT %(question_number)s;
    """
    data = {'question_number': number_of_questions}
    cursor.execute(query, data)
    return cursor.fetchall()


@database.connection_handler
def get_all_question_tags(cursor):
    query = """
    SELECT question_id, tag_id, 
    (SELECT tag.name FROM tag WHERE tag.id = question_tag.tag_id) as tag_name
    FROM question_tag;
    """
    cursor.execute(query)
    return cursor.fetchall()


@database.connection_handler
def get_question(cursor, id):
    query = """
        SELECT id, submission_time, view_number, vote_number, title, message, image, author, 
        (SELECT login FROM users WHERE id = question.author) as author_name
        FROM question
        WHERE id = %(id)s
       """
    data = {'id': id}
    cursor.execute(query, data)
    return cursor.fetchone()
        

@database.connection_handler
def get_answer(cursor, answer_id):
    query = """
        SELECT id, submission_time, vote_number, question_id, message, image
        FROM answer
        WHERE id = %(id)s
       """
    data = {'id': answer_id}
    cursor.execute(query, data)
    return cursor.fetchone()
        

@database.connection_handler
def get_answers(cursor, question_id):
    query = """
        SELECT id, submission_time, vote_number, question_id, message, image, author, acceptance,  
        (SELECT login FROM users WHERE id = answer.author) as author_name
        FROM answer
        WHERE question_id = %(id)s
        ORDER by id DESC
       """
    data = {'id': question_id}
    cursor.execute(query, data)
    return cursor.fetchall()


@database.connection_handler
def get_comments_question(cursor, question_id):
    query = """
        SELECT id, question_id, message, submission_time, edited_number, author,
        (SELECT login FROM users WHERE id = comment.author) as author_name
        FROM comment
        WHERE question_id = %(id)s
        ORDER by id ASC
       """
    data = {'id': question_id}
    cursor.execute(query, data)
    return cursor.fetchall()


@database.connection_handler
def get_comments_answer(cursor):
    query = """
    SELECT comment.answer_id, comment.id, comment.message, comment.submission_time, edited_number,
    (SELECT login FROM users WHERE id = comment.author) as author_name
    FROM comment
    INNER JOIN answer ON answer.id = comment.answer_id;
       """
    cursor.execute(query)
    return cursor.fetchall()


@database.connection_handler
def get_comment(cursor, comment_id):
    query = """
    SELECT id, question_id, message, submission_time, edited_number
        FROM comment
        WHERE id = %(id)s    
    """
    data = {'id': comment_id}
    cursor.execute(query, data)
    return cursor.fetchone()


@database.connection_handler
def edit_comment(cursor, current_date:str, comment_message:str, comment_id):
    query = """
    UPDATE comment 
    SET (message, submission_time, edited_number) = (%(message)s, %(date)s, edited_number + 1)
    WHERE id = %(id)s    
    """
    data = {'message': comment_message, 'date': current_date, 'id': comment_id}
    cursor.execute(query, data)


@database.connection_handler
def edit_answer(cursor, current_date:str, answer_message:str, answer_id):
    query = """
    UPDATE answer 
    SET (message, submission_time) = (%(message)s, %(date)s)
    WHERE id = %(id)s    
    """
    data = {'message': answer_message, 'date': current_date, 'id': answer_id}
    cursor.execute(query, data)


@database.connection_handler
def add_question(cursor, current_date:str, your_question:dict, image:str, author:int):
    try:
        query = """
            INSERT INTO question (submission_time, title, message, image, author) 
            VALUES (%(date)s, %(title)s, %(message)s, %(image)s, %(author)s)
        """
        data = {'date': current_date, 'title': your_question['title'], 'message': your_question['message'], 'image': image, 'author': author}
        cursor.execute(query, data)
    except:
        raise ValueError("Wrong values types provided for database input.")


def save_question_image(file):
    if file.filename != "":
        file_name = util.get_unique_file_name()
        file_name_with_extension =  file_name + ".jpg"
        file.save(os.path.join(UPLOAD_FOLDER_FOR_QUESTIONS, file_name_with_extension))
        return UPLOAD_FOLDER_FOR_QUESTIONS + file_name_with_extension
    else:
        return "no-image"


def update_question_image(file, image):
    if file.filename != "":
        image != "no-image" and os.remove(image)
        file_name = util.get_unique_file_name()
        file_name_with_extension =  file_name + ".jpg"
        file.save(os.path.join(UPLOAD_FOLDER_FOR_QUESTIONS, file_name_with_extension))
        return UPLOAD_FOLDER_FOR_QUESTIONS + file_name_with_extension
    else:
        return image


def save_answer_image(file):
    if file.filename != "":
        file_name = util.get_unique_file_name()
        file_name_with_extension =  file_name + ".jpg"
        file.save(os.path.join(UPLOAD_FOLDER_FOR_ANSWERS, file_name_with_extension))
        return UPLOAD_FOLDER_FOR_ANSWERS + file_name_with_extension
    else:
        return "no-image"


@database.connection_handler
def add_answer(cursor, current_date, your_answer:dict, image:str, author:int):
    try:
        query = """
            INSERT INTO answer (submission_time, question_id, message, image, author) 
            VALUES (%(date)s, %(id)s, %(message)s, %(image)s, %(author)s)
        """
        data = {'date': current_date, 'id': your_answer["question_id"], 'message': your_answer["message"], 'image': image, 'author': author}
        cursor.execute(query, data)
    except:
        raise ValueError("Wrong values types provided for database input.")


@database.connection_handler
def add_comment_question(cursor, question_comment, id:int, author):
    current_date = util.get_current_date()
    query = """
          INSERT INTO comment (question_id, message, submission_time, author) 
          VALUES (%(id)s, %(comment)s, %(date)s, %(author)s); """
    data = {'id': id, 'comment': question_comment, 'date': current_date, 'author': author}
    cursor.execute(query, data)


@database.connection_handler
def add_comment_answer(cursor, answer_comment, answer_id:int, author):
    current_date = util.get_current_date()
    query = """
          INSERT INTO comment (answer_id, message, submission_time, author) 
          VALUES (%(id)s, %(comment)s, %(date)s, %(author)s); """
    data = {'id': answer_id, 'comment': answer_comment, 'date': current_date, 'author': author}
    cursor.execute(query, data)


@database.connection_handler
def add_vote_question(cursor, id:int):
    query = """
        UPDATE question
        SET vote_number = vote_number + 1
        WHERE id = %(id)s
    """
    data = {'id': id}
    cursor.execute(query, data)


@database.connection_handler
def substract_vote_question(cursor, id:int):
    query = """
        UPDATE question
        SET vote_number = vote_number - 1
        WHERE id = %(id)s
    """
    data = {'id': id}
    cursor.execute(query, data)


@database.connection_handler
def add_vote_answer(cursor, id:int):
    query = """
        UPDATE answer
        SET vote_number = vote_number + 1
        WHERE id = %(id)s
    """
    data = {'id': id}
    cursor.execute(query, data)


@database.connection_handler
def substract_vote_answer(cursor, id:int):
    query = """
        UPDATE answer
        SET vote_number = vote_number - 1
        WHERE id = %(id)s
    """
    data = {'id': id}
    cursor.execute(query, data)

@database.connection_handler
def remove_question(cursor, question_id, image):
    if image['image'] != 'no-image':
        os.remove(image['image'])
    query = """
    DELETE FROM question
    WHERE id = %(id)s
    """
    data = {'id': question_id}
    cursor.execute(query, data)

@database.connection_handler
def get_all_answers_ids(cursor, question_id:int):
    query = """
        SELECT id FROM answer
        WHERE question_id = %(id)s
    """
    data = {'id': question_id}
    cursor.execute(query, data)
    return cursor.fetchall()

@database.connection_handler
def get_question_image_path(cursor, id:int):
    query = """
        SELECT image FROM question
        WHERE id = %(id)s
    """
    data = {'id': id}
    cursor.execute(query, data)
    return cursor.fetchone()

@database.connection_handler
def get_answer_image_path(cursor, answer_id:int):
    query = """
        SELECT image FROM answer
        WHERE id = %(id)s
    """
    data = {'id': answer_id}
    cursor.execute(query, data)
    return cursor.fetchone()

@database.connection_handler
def remove_comment(cursor, comment_id:int):
    query = """
    DELETE FROM comment
    WHERE id = %(id)s
    """
    data = {'id': comment_id}
    cursor.execute(query, data)

@database.connection_handler
def remove_all_question_comments(cursor, question_id, answers_id_list):
    query = """
    DELETE FROM comment
    WHERE question_id = %(qid)s
    OR answer_id IN %(aids)s
    """
    data = {'qid': question_id, 'aids': answers_id_list}
    cursor.execute(query, data)


@database.connection_handler
def remove_all_answer_comments(cursor, answer_id):
    query = """
    DELETE FROM comment
    WHERE answer_id = %(id)s
    """
    data = {'id': answer_id}
    cursor.execute(query, data)


@database.connection_handler
def remove_answer(cursor, answer_id:int, image:str):
    if image['image'] != 'no-image':
        os.remove(image['image'])
    query = """
    DELETE FROM answer
    WHERE id = %(id)s
    """
    data = {'id': answer_id}
    cursor.execute(query, data)


@database.connection_handler
def update_question(cursor, question_id, question_date, question_title, question_message, question_image):
    query = """
    UPDATE question 
    SET (submission_time, title, message, image) = (%(date)s, %(title)s, %(message)s, %(image)s)
    WHERE id = %(id)s
    """
    data = {'id': question_id, 'date': question_date, 'title': question_title, 'message': question_message, 'image': question_image}
    cursor.execute(query, data)


@database.connection_handler
def count_view(cursor, id:int):
    query = """
        UPDATE question 
        SET view_number = view_number + 1
        WHERE id = %(id)s
    """
    data = {'id': id}
    cursor.execute(query, data)


@database.connection_handler
def search_for_questions(cursor, search_argument):
    query = """
        SELECT id, submission_time, view_number, vote_number, title, message, 
            COALESCE((SELECT COUNT(answer.question_id)
            FROM answer 
            WHERE answer.question_id = question.id GROUP by answer.question_id), 0) as answer_number 
        FROM question 
        WHERE id IN (SELECT DISTINCT question_id
                        FROM answer 
                        WHERE message LIKE %(search)s)
            OR title LIKE %(search)s 
            OR message LIKE %(search)s
        ORDER BY submission_time DESC
    """
    data = {'search': '%' + search_argument + '%'}
    cursor.execute(query, data)
    return cursor.fetchall()


@database.connection_handler
def search_for_questions_by_tag(cursor, tag_id):
    query = """
        SELECT * FROM question
        WHERE question.id IN (SELECT question_id FROM question_tag WHERE tag_id = %(tag)s)
        ORDER BY submission_time DESC
    """
    data = {'tag': tag_id}
    cursor.execute(query, data)
    return cursor.fetchall()


@database.connection_handler
def get_tags_list(cursor):
    query = "SELECT * FROM tag"
    cursor.execute(query)
    return cursor.fetchall()


@database.connection_handler
def get_question_tags(cursor, question_id):
    query = """
        SELECT * FROM tag 
        WHERE id IN (SELECT tag_id FROM question_tag WHERE question_id = %(id)s)"""
    data = {'id': question_id}
    cursor.execute(query, data)
    return cursor.fetchall()


@database.connection_handler
def add_new_tag(cursor, new_tag):
    query = "INSERT INTO tag (name) VALUES (%(tag)s)"
    data = {'tag': new_tag}
    cursor.execute(query, data)
 

@database.connection_handler
def get_tag_id(cursor, tag):
    query = "SELECT id FROM tag WHERE name = %(tag)s"
    data = {'tag': tag}
    cursor.execute(query, data)
    return cursor.fetchone()


@database.connection_handler
def add_tag_to_question(cursor, question_id, tag_id):
    query = "INSERT INTO question_tag (question_id, tag_id) VALUES (%(qid)s, %(tid)s)"
    data = {'qid': question_id, 'tid': tag_id}
    cursor.execute(query, data)


@database.connection_handler
def delete_tag(cursor, tag_id, question_id):
    query = "DELETE from question_tag WHERE question_id = %(qid)s AND tag_id = %(tid)s"
    data = {'qid': question_id, 'tid': tag_id}
    cursor.execute(query, data)

@database.connection_handler
def delete_all_question_tags(cursor, question_id):
    query = "DELETE from question_tag WHERE question_id = %(qid)s"
    data = {'qid': question_id}
    cursor.execute(query, data)

def add_markups_to_questions(questions_list, searching_phrase):
    for question in questions_list:
        question['title'] = question['title'].replace(searching_phrase, '<mark>' + searching_phrase + '</mark>')
        question['message'] = question['message'].replace(searching_phrase, '<mark>' + searching_phrase + '</mark>')
    return questions_list

@database.connection_handler
def accept_answer(cursor, answer_id):
    query = """
    UPDATE answer 
    SET acceptance = 1
    WHERE id = %(answer_id)s
    """
    data = {'answer_id': answer_id}
    cursor.execute(query, data)

@database.connection_handler
def unaccept_answer(cursor, answer_id):
    query = """
    UPDATE answer 
    SET acceptance = 0
    WHERE id = %(answer_id)s
    """
    data = {'answer_id': answer_id}
    cursor.execute(query, data)