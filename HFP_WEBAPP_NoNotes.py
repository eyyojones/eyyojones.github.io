
from flask import Flask, render_template, request, escape, session, copy_current_request_context
from HFP_C3_mod_copy2 import letter_tally
from checker import check_logged_in
from DBcm import UseDatabase, Connection_Error, CredentialsError, SQLError
from time import sleep
from threading import Thread

app = Flask(__name__)

app.config['dbconfig'] = {'host': '127.0.0.1',                          
                          'user': 'root',
                          'password': 'mysql',
                          'database': 'letter_tallylogDB'}


app.secret_key = 'YouWillNeverGuessMySecretKey'

@app.route('/login')
def do_login() -> str:
    session['logged_in'] = True 
    return 'You are logged in' 

@app.route('/logout')
def do_logout() -> str:
    session.pop('logged_in')  
    return 'You are now logged out'


@app.route('/search4', methods=['POST'])  
def flaskfunc_lt() -> 'html':

    @copy_current_request_context 
    def log_request(req: 'flask_request', res: str) -> None:
        sleep(15)  
        with UseDatabase(app.config['dbconfig']) as cursor:
                _SQL="""insert into log
                        (phrase, letters, ip, browser_string,results)
                        values
                        (%s,%s,%s,%s,%s)""" 
                cursor.execute(_SQL, (req.form['phrase'],              
                                req.form['letters'],            
                                req.remote_addr,
                                req.user_agent.browser,
                                res, ))
                
        phrase = request.form['phrase']
        letters = request.form['letters']
        title = 'here are your results:'
        results = str(letter_tallys(phrase,letters))
        try:
            t = Thread(target=log_request, args=(request,results))
            t.start()
        except Exception as err:
            print('*****Logging failed with this error:', str(err))
        return render_template('results.html',the_phrase=phrase,
                               the_letters=letters,
                               the_title=title,
                               the_results=results,)

@app.route('/')    
@app.route('/entry',methods=['GET'])
def flaskfunc_html_rt() -> 'html':
        return render_template('entry.html',the_title='entry title ex.')
        
@app.route('/viewlog')
@check_logged_in
def view_the_log() -> 'html':
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
                _SQL="""select phrase, letters, ip, browser_string, results
                        from letter_tallylogDB.log"""
                cursor.execute(_SQL)
                contents = cursor.fetchall()
        titles=('Phrase', 'Letters', 'Remote_addr', 'User_agent', 'Results')
        return render_template('viewlog.html',
                               the_title='View Log',
                               the_row_titles=titles,
                               the_data=contents,)
    except Connection_Error as err:
        print('*****Databse may be turned off.', str(err))
    except CredentialsError as err:
        print('*****check MySQL login credentials:', str(err))
    except Exception as err:
        print('*****some error occurred.',str(err))
    
print('We start off in:', __name__) 
if __name__== '__main__':
        app.run(debug=True)
        print('And end up in: ', __name__)

