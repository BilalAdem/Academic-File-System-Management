import os

def create_project_structure():
  """
  Creates the project directory structure and initializes some files.
  """

  project_dir = "academic_file_system"
  folders = [
      "app",
      "config",
      "migrations",
      "static/css",
      "static/js",
      "templates",
      "templates/courses"
  ]
  files = [
      "requirements.txt",
      os.path.join(project_dir, "app.py"),
      os.path.join(project_dir, "config.py"),
      os.path.join(project_dir, "templates", "base.html"),
      os.path.join(project_dir, "templates", "index.html"),
  ]

  # Create the project directory (if it doesn't exist)
  if not os.path.exists(project_dir):
    os.makedirs(project_dir)

  # Create all folders
  for folder in folders:
    os.makedirs(os.path.join(project_dir, folder), exist_ok=True)

  # Create empty files
  for file in files:
    with open(file, 'w') as f:
      pass  # Empty file

  print(f"Project directory structure created at: {project_dir}")

# Initialize the project structure
create_project_structure()





mime_types = {
    '.txt': 'text/plain',
    '.pdf': 'application/pdf',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.xlsm': 'application/vnd.ms-excel.sheet.macroEnabled.12',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    '.doc': 'application/msword',
    '.ppt': 'application/vnd.ms-powerpoint',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.zip': 'application/zip',
    '.rar': 'application/x-rar-compressed'
}




app.route('/download/<int:file>', methods=['GET'])
def download_file(file):
    file = db.session.query(File).filter_by(id=file).first()
    file_data = fs.get(ObjectId(file.mongo_file_id))
    if file_data:
        mime_type = mime_types.get(file.name.rsplit('.', 1)[1].lower())
        # Set appropriate MIME type for the file
        response = Response(file_data.read(), mimetype=mime_type)
        if 'pdf' or 'image' in mime_type:
            response.headers['Content-Disposition'] = 'inline'
        else:
            response.headers['Content-Disposition'] = 'attachment'

        return response
    else:
        return "File not found!", 404