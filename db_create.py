import mysql.connector

# Connect to the MySQL server
cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345678"
)

# Create a cursor object to execute SQL queries
cursor = cnx.cursor()

# Create the "courses" database
cursor.execute("CREATE DATABASE files_db")
cursor.execute("SHOW DATABASES")

for db in cursor:
    print(db)

# Close the cursor and connection
cursor.close()
cnx.close()





@app.route("/", methods=["POST"])
def upload_file():
    uploaded_file = request.files['file']  # Access uploaded file
    file_type = request.form['options']  # Access selected file type
    # Access selected repository (if any)
    existing_repo = request.form.get('reps')
    # Access new repository name (if any)
    new_repo = request.form.get('new_rep')

    # Process the file and repository information (e.g., save the file and store metadata)
    # ...

    print(f"Uploaded file: {uploaded_file.filename}")
    print(f"File type: {file_type}")
    if existing_repo:
        print(f"Selected repository: {existing_repo}")
    else:
        print(f"New repository name: {new_repo}")

    # Save the file and its metadata to the database
    new_file = File(name=uploaded_file.filename, type=file_type,
                    repository=existing_repo if existing_repo else new_repo)
    db.session.add(new_file)
    db.session.commit()

    if result:
        return render_template('index.html', result=result)
    else:
        return render_template('index.html')