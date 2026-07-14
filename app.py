import os
import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_wtf.csrf import CSRFProtect
from database import get_db_connection, init_db

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
csrf = CSRFProtect(app)

# Use a flag to ensure the database is initialized only once
db_initialized = False

@app.before_request
def setup():
    global db_initialized
    if not db_initialized:
        init_db()
        db_initialized = True

# Custom Jinja2 filter for date formatting
@app.template_filter('strftime')
def format_datetime(value, format="%Y-%m-%d"):
    if isinstance(value, datetime.date):
        return value.strftime(format)
    elif isinstance(value, str):
        try:
            date_obj = datetime.datetime.strptime(value, "%Y-%m-%d").date()
            return date_obj.strftime(format)
        except ValueError:
            return value
    return value

def validate_date(date_str):
    try:
        datetime.datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except (ValueError, TypeError):
        return False

def validate_amount(amount_str):
    try:
        val = float(amount_str)
        return val > 0
    except (ValueError, TypeError):
        return False

def validate_required(value, max_length=200):
    if not value or not isinstance(value, str):
        return False
    return 0 < len(value.strip()) <= max_length

@app.route('/')
def dashboard():
    conn = get_db_connection()
    today = datetime.date.today()

    # Fetch and process all upcoming monthly and custom bills
    monthly_bills = conn.execute('SELECT * FROM monthly_bills WHERE is_paid = 0 ORDER BY due_date ASC').fetchall()
    custom_bills = conn.execute('SELECT * FROM custom_bills WHERE is_paid = 0 ORDER BY due_date ASC').fetchall()
    
    upcoming_bills = []
    for bill in monthly_bills:
        due_date = datetime.datetime.strptime(bill['due_date'], '%Y-%m-%d').date()
        remaining_days = (due_date - today).days
        upcoming_bills.append({
            'id': bill['id'],
            'bill_name': bill['bill_name'],
            'amount': bill['amount'],
            'due_date': bill['due_date'],
            'remaining_days': remaining_days,
            'type': 'monthly'
        })
    
    for bill in custom_bills:
        due_date = datetime.datetime.strptime(bill['due_date'], '%Y-%m-%d').date()
        remaining_days = (due_date - today).days
        upcoming_bills.append({
            'id': bill['id'],
            'bill_name': bill['bill_name'],
            'amount': bill['amount'],
            'due_date': bill['due_date'],
            'remaining_days': remaining_days,
            'type': 'custom'
        })
    
    upcoming_bills.sort(key=lambda x: x['remaining_days'])

    # Fetch and process other data sections
    emis = conn.execute('SELECT * FROM emis ORDER BY due_date ASC').fetchall()
    events = conn.execute('SELECT * FROM events ORDER by event_date ASC').fetchall()

    # Corrected logic for Recharges
    recharges = conn.execute('SELECT * FROM recharges').fetchall()
    recharges_with_days = []
    for recharge in recharges:
        recharge_date = datetime.datetime.strptime(recharge['recharge_date'], '%Y-%m-%d').date()
        expiry_date = recharge_date + datetime.timedelta(days=recharge['valid_days'])
        remaining_days = (expiry_date - today).days
        recharges_with_days.append({
            'id': recharge['id'],
            'contact_name': recharge['contact_name'],
            'plan_amount': recharge['plan_amount'],
            'recharge_date': recharge['recharge_date'],
            'valid_days': recharge['valid_days'],
            'remaining_days': remaining_days,
            'expiry_date': expiry_date
        })
    
    # Calculate summary
    total_upcoming_amount = sum(bill['amount'] for bill in upcoming_bills if bill['remaining_days'] >= 0)
    paid_monthly_bills = conn.execute('SELECT * FROM monthly_bills WHERE is_paid = 1').fetchall()
    paid_custom_bills = conn.execute('SELECT * FROM custom_bills WHERE is_paid = 1').fetchall()
    total_paid_amount = sum(bill['amount'] for bill in paid_monthly_bills) + sum(bill['amount'] for bill in paid_custom_bills)

    conn.close()
    return render_template('dashboard.html', 
                           upcoming_bills=upcoming_bills, 
                           emis=emis, 
                           recharges=recharges_with_days, 
                           events=events,
                           total_upcoming_amount=total_upcoming_amount,
                           total_paid_amount=total_paid_amount)

@app.route('/mark_paid/<type>/<int:id>', methods=['POST'])
def mark_paid(type, id):
    conn = get_db_connection()
    if type == 'monthly':
        conn.execute('UPDATE monthly_bills SET is_paid = 1 WHERE id = ?', (id,))
    elif type == 'custom':
        conn.execute('UPDATE custom_bills SET is_paid = 1 WHERE id = ?', (id,))
    elif type == 'recharge':
        conn.execute('DELETE FROM recharges WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/delete/<type>/<int:id>', methods=['POST'])
def delete_item(type, id):
    conn = get_db_connection()
    if type == 'monthly':
        conn.execute('DELETE FROM monthly_bills WHERE id = ?', (id,))
    elif type == 'custom':
        conn.execute('DELETE FROM custom_bills WHERE id = ?', (id,))
    elif type == 'recharge':
        conn.execute('DELETE FROM recharges WHERE id = ?', (id,))
    elif type == 'emi':
        conn.execute('DELETE FROM emis WHERE id = ?', (id,))
    elif type == 'event':
        conn.execute('DELETE FROM events WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))


@app.route('/add/<type>', methods=['POST'])
def add_item(type):
    data = request.form
    errors = []
    
    if type == 'recharge':
        if not validate_required(data.get('contact_name')):
            errors.append('Contact name is required (max 200 chars)')
        if not validate_date(data.get('recharge_date')):
            errors.append('Invalid recharge date')
        try:
            valid_days = int(data.get('valid_days', 0))
            if valid_days <= 0:
                errors.append('Valid days must be positive')
        except (ValueError, TypeError):
            errors.append('Valid days must be a number')
        if not validate_amount(data.get('plan_amount')):
            errors.append('Plan amount must be a positive number')
    elif type == 'emi':
        if not validate_required(data.get('emi_name')):
            errors.append('EMI name is required')
        if not validate_date(data.get('due_date')):
            errors.append('Invalid due date')
        if not validate_amount(data.get('amount')):
            errors.append('Amount must be a positive number')
    elif type == 'event':
        if not validate_required(data.get('event_name')):
            errors.append('Event name is required')
        if not validate_date(data.get('event_date')):
            errors.append('Invalid event date')
    elif type == 'monthly_bill':
        if not validate_required(data.get('bill_name')):
            errors.append('Bill name is required')
        if not validate_amount(data.get('amount')):
            errors.append('Amount must be a positive number')
        if not validate_date(data.get('due_date')):
            errors.append('Invalid due date')
    elif type == 'custom_bill':
        if not validate_required(data.get('bill_name')):
            errors.append('Bill name is required')
        if not validate_required(data.get('bill_type')):
            errors.append('Bill type is required')
        if not validate_date(data.get('due_date')):
            errors.append('Invalid due date')
        if not validate_amount(data.get('amount')):
            errors.append('Amount must be a positive number')
    else:
        abort(400)
    
    if errors:
        return jsonify({'errors': errors}), 400
    
    conn = get_db_connection()
    try:
        if type == 'recharge':
            conn.execute('INSERT INTO recharges (contact_name, recharge_date, valid_days, plan_amount) VALUES (?, ?, ?, ?)',
                         (data['contact_name'].strip(), data['recharge_date'], int(data['valid_days']), float(data['plan_amount'])))
        elif type == 'emi':
            conn.execute('INSERT INTO emis (emi_name, due_date, amount) VALUES (?, ?, ?)',
                         (data['emi_name'].strip(), data['due_date'], float(data['amount'])))
        elif type == 'event':
            conn.execute('INSERT INTO events (event_name, event_date, notes) VALUES (?, ?, ?)',
                         (data['event_name'].strip(), data['event_date'], data.get('notes', '').strip()))
        elif type == 'monthly_bill':
            conn.execute('INSERT INTO monthly_bills (bill_name, amount, due_date) VALUES (?, ?, ?)',
                         (data['bill_name'].strip(), float(data['amount']), data['due_date']))
        elif type == 'custom_bill':
            conn.execute('INSERT INTO custom_bills (bill_name, bill_type, due_date, amount) VALUES (?, ?, ?, ?)',
                         (data['bill_name'].strip(), data['bill_type'].strip(), data['due_date'], float(data['amount'])))
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for('dashboard'))

@app.route('/edit/<type>/<int:id>', methods=['POST'])
def edit_item(type, id):
    data = request.form
    errors = []
    
    if type == 'recharge':
        if not validate_required(data.get('contact_name')):
            errors.append('Contact name is required')
        if not validate_date(data.get('recharge_date')):
            errors.append('Invalid recharge date')
        if not validate_amount(data.get('valid_days')) or int(data.get('valid_days', 0)) <= 0:
            errors.append('Valid days must be positive')
        if not validate_amount(data.get('plan_amount')):
            errors.append('Plan amount must be positive')
    elif type == 'emi':
        if not validate_required(data.get('emi_name')):
            errors.append('EMI name is required')
        if not validate_date(data.get('due_date')):
            errors.append('Invalid due date')
        if not validate_amount(data.get('amount')):
            errors.append('Amount must be positive')
    elif type == 'event':
        if not validate_required(data.get('event_name')):
            errors.append('Event name is required')
        if not validate_date(data.get('event_date')):
            errors.append('Invalid event date')
    elif type == 'monthly':
        if not validate_required(data.get('bill_name')):
            errors.append('Bill name is required')
        if not validate_amount(data.get('amount')):
            errors.append('Amount must be positive')
        if not validate_date(data.get('due_date')):
            errors.append('Invalid due date')
    elif type == 'custom':
        if not validate_required(data.get('bill_name')):
            errors.append('Bill name is required')
        if not validate_required(data.get('bill_type')):
            errors.append('Bill type is required')
        if not validate_date(data.get('due_date')):
            errors.append('Invalid due date')
        if not validate_amount(data.get('amount')):
            errors.append('Amount must be positive')
    else:
        abort(400)
    
    if errors:
        return jsonify({'errors': errors}), 400
    
    conn = get_db_connection()
    try:
        if type == 'recharge':
            conn.execute('UPDATE recharges SET contact_name=?, recharge_date=?, valid_days=?, plan_amount=? WHERE id=?',
                         (data['contact_name'].strip(), data['recharge_date'], int(data['valid_days']), float(data['plan_amount']), id))
        elif type == 'emi':
            conn.execute('UPDATE emis SET emi_name=?, due_date=?, amount=? WHERE id=?',
                         (data['emi_name'].strip(), data['due_date'], float(data['amount']), id))
        elif type == 'event':
            conn.execute('UPDATE events SET event_name=?, event_date=?, notes=? WHERE id=?',
                         (data['event_name'].strip(), data['event_date'], data.get('notes', '').strip(), id))
        elif type == 'monthly':
            conn.execute('UPDATE monthly_bills SET bill_name=?, amount=?, due_date=? WHERE id=?',
                         (data['bill_name'].strip(), float(data['amount']), data['due_date'], id))
        elif type == 'custom':
            conn.execute('UPDATE custom_bills SET bill_name=?, bill_type=?, due_date=?, amount=? WHERE id=?',
                         (data['bill_name'].strip(), data['bill_type'].strip(), data['due_date'], float(data['amount']), id))
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for('dashboard'))

@app.route('/get_item/<type>/<int:id>')
def get_item(type, id):
    conn = get_db_connection()
    if type == 'recharge':
        item = conn.execute('SELECT * FROM recharges WHERE id = ?', (id,)).fetchone()
    elif type == 'emi':
        item = conn.execute('SELECT * FROM emis WHERE id = ?', (id,)).fetchone()
    elif type == 'event':
        item = conn.execute('SELECT * FROM events WHERE id = ?', (id,)).fetchone()
    elif type == 'monthly':
        item = conn.execute('SELECT * FROM monthly_bills WHERE id = ?', (id,)).fetchone()
    elif type == 'custom':
        item = conn.execute('SELECT * FROM custom_bills WHERE id = ?', (id,)).fetchone()
    conn.close()
    if item:
        return jsonify(dict(item))
    return jsonify({'error': 'Item not found'}), 404

@app.route('/paid_bills')
def paid_bills():
    conn = get_db_connection()
    monthly_paid = conn.execute('SELECT * FROM monthly_bills WHERE is_paid = 1 ORDER BY due_date DESC').fetchall()
    custom_paid = conn.execute('SELECT * FROM custom_bills WHERE is_paid = 1 ORDER BY due_date DESC').fetchall()
    all_paid_bills = [dict(row) for row in monthly_paid] + [dict(row) for row in custom_paid]
    conn.close()
    return render_template('paid.html', paid_bills=all_paid_bills)

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', '0') == '1')
