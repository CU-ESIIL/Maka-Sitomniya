# Contributing to Maka Sitomniya 

Welcome to Maka Sitomniya! We’re excited to have you contribute. Whether you're a coder, instructor, group member or researcher, your help is appreciated.

## 📌 How to Contribute
You can contribute in several ways:
- **Report Issues** (Bugs, Feature Requests, Documentation)
- **Suggest Enhancements**
- **Submit Code Changes**
- **Improve Documentation**
- **Help Review Pull Requests**

## 📝 Submitting Issues
If you find a bug or have a suggestion, submit an issue:
1. Go to the **"Issues"** tab.
2. Click **"New Issue."**
3. Use the templates (if available) or describe the problem in detail:
   - **Steps to reproduce**
   - **Expected vs. actual behavior**
   - **Screenshots (if applicable)**

Please be respectful, follow principles of Wolakota, and check existing issues before opening a new one.

## 🔧 Making Code Changes
### **1. Fork & Clone the Repository**
1. Click the **"Fork"** button at the top-right of the repository.
2. Clone your fork to your local machine:
   - git clone https://github.com/YOUR-USERNAME/Maka-Sitomniya.git
   - cd PROJECT-NAME
3. Set the original repo as the upstream:
   - git remote add upstream https://github.com/CU-ESIIL/Maka-Sitomniya.git
4. Always create a new branch for changes:
   - git checkout -b feature-branch
5. Make Changes & Commit
   - Keep commits small and meaningful.
   - Follow the Pep 8 code style Python and tidyverse for R.
   - Write clear commit messages:
         - git commit -m "Add feature: description"
6. Push & Create a Pull Request (PR)
   - Push your branch to GitHub:
         - git push origin feature-branch
   - Open a Pull Request:
       - Go to your fork on GitHub.
       - Click "Compare & pull request."
       - Add a title and description explaining your changes.
       - Request a review from team members.
7. Reviewing Pull Requests
   - Be kind and constructive in feedback.
   - Suggest improvements, but respect different perspectives.
   - Merge changes only after they pass reviews and tests.

📚 Documentation Contributions
If you're improving documentation:
   - Follow Markdown formatting.
   - Add clear examples/screenshots.
   - Keep it simple and beginner-friendly.

🖥️ Using GitHub Desktop (For Non-Technical Users)
>GitHub Desktop makes it easier to contribute without using the command line.
1. Install GitHub Desktop
   - Download it from GitHub Desktop.
   - Install and log in with your GitHub account.
2. Clone the Repository
   - Open GitHub Desktop.
   - Click "File" → "Clone Repository."
   - Select "GitHub.com" and choose the repository Maka Sitomniya.
   - Click "Clone."
3. Make Changes
   - Open the repository folder on your computer.
   - Edit files as needed (e.g., in Notepad or VS Code or your preferred editor).
   - Return to GitHub Desktop, where changes will be listed.
   - Write a summary of your changes and click "Commit to main/branch."
4. Push Changes
   - Click "Push origin" to upload your changes.
   - On GitHub, open a Pull Request to submit your changes.

🔄 Handling Merge Conflicts
Merge conflicts happen when two people edit the same part of a file. Here’s how to fix them:
1. Identify the Conflict
   - If you see an error like this when pulling changes:
   - CONFLICT (content): Merge conflict in file.txt
   - It means Git doesn’t know which version to keep.
2. Open the Conflicted File
The file will contain markers like this:
   - <<<<<<< HEAD
   - Your changes here
   - =======
   - Someone else's changes
   - >>>>>>> feature-branch
3. Manually Resolve the Conflict:
   - Decide which version to keep, or merge them manually.
   - Then remove the conflict markers (<<<<, ====, >>>>).
4. Mark as resolved:
   - git add filename.txt
   - git commit -m "Resolved merge conflict in filename.txt"
5. Then push your changes again:
   - git push origin your-branch
If you need help, feel free to ask in GitHub Discussions or in our project Slack.

💡 Need Help?
If you’re new to GitHub or have a question about how to do something:
   - Check out GitHub Docs.
   - Ask questions in GitHub Discussions
   - Ask questions in our project Slack
   - Contact a member of the Tech Team 














