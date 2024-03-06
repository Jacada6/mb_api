import os
import time
from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import sql
from psycopg2 import OperationalError

# Create Flask app
app = Flask(__name__)

# Database connection
conn = None
while not conn:
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname="assignment",
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port="5432"
        )
    # Add delay if PostgreSQL is not ready yet
    except OperationalError:
        print("PostgreSQL is not ready yet. Waiting for 5 seconds...")
        time.sleep(5)

# Error handling for SQL injection
def sanitize_input(value):
    return value.replace("'", "''")

# Root Page
@app.route('/')
def mainpage():
    return 'API is running'

# Query Endpoint
@app.route('/assignment/query', methods=['POST'])
def query():
    data = request.get_json()
    # Handle invalid request data
    if not data:
        return jsonify({
            "error": "Invalid request data"
        }), 400

    # Parse request data
    filters = data.get('filters', {})
    ordering = data.get('ordering', [])
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('page_size', default=10, type=int)

    # Construct SQL query
    query = sql.SQL("SELECT * FROM report_output")
    where_clauses = []
    order_clauses = []
    # Construct WHERE clauses
    for column, value in filters.items():
        sanitized_value = sanitize_input(value)
        where_clauses.append(sql.SQL("{} = {}").format(sql.Identifier(column), sql.SQL(sanitized_value)))
    # Construct ORDER BY clauses
    for order in ordering:
        for column, direction in order.items():
            order_clauses.append(sql.SQL("{} {}").format(sql.Identifier(column), sql.SQL(direction)))
    # Construct final query
    if where_clauses:
        query += sql.SQL(" WHERE {}").format(sql.SQL(" AND ").join(where_clauses))
    if order_clauses:
        query += sql.SQL(" ORDER BY {}").format(sql.SQL(", ").join(order_clauses))
    query += sql.SQL(" LIMIT {} OFFSET {}").format(sql.SQL(str(page_size)), sql.SQL(str((page - 1) * page_size)))

    try:
        # Execute query
        cur = conn.cursor()
        cur.execute(query)
        results = cur.fetchall()

        # Return results
        return jsonify({
            "page": page,
            "page_size": page_size,
            "count": len(results),
            "results": results
        }), 200
    # Handle database errors
    except Exception as e:
        # Rollback database changes
        conn.rollback()
        return jsonify({
            "error": str(e)
        }), 500
    # Close database connection
    finally:
        cur.close()

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)