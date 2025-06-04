# Welcome to the ODOO4PROJECTS Team! 🎉

Hey there, superstar! 🌟 We're thrilled to have you onboard. To keep our collaboration smooth and fun, we've put together some cool workflows and guidelines. Let's dive in!

## 1. GIT: Code Like a Pro 💻

- **Commit Messages Matter**: Think of commit messages as little love notes to your future self (and your teammates). Keep them clear and meaningful.
- **Branch Out**: Feel free to create branches as needed. It's like planting trees in our code forest. 🌳

**Pro Tip**: Head over to our git server at [https://git.odoo4projects.com](https://git.odoo4projects.com) and upload your public SSH key. This way, you can push via SSH without typing your username and password each time. Magic, right? ✨


1. Generate SSH Key:
```bash
ssh-keygen -t rsa -b 4096 -C "you@example.com"
```

2. Add SSH Key to Git Server: Copy your SSH key and add it to your Git profile.

```bash
cat ~/.ssh/id_rsa.pub
```

3. Upload this key to your account settngs on out git server

## 2. DOCKER: Your Odoo Playground 🐳

For a quick and easy Odoo setup, we use the official Docker images. Here's your treasure map:

- **Install Docker**: On Ubuntu, run:
```bash
sudo apt-get install docker.io docker-compose
```
**Launch Odoo:** Fire up your instance with:

```bash
sudo docker-compose up
```

**IMPORTANT**:Due to the Odoo image, you need to change the permissions of your data/odoo-web-data directory:

```bash
sudo chmod 777 data/odoo-web-data
```

## 3. **QUALITY:** Code Like a Rockstar 🌟

We love good code, and we know you do too! Here's how to keep your code dazzling:

-    **Document Everything:** Good documentation is like leaving a trail of breadcrumbs. Make it easy for others to follow.
-    **Avoid Redundancies:** Use functions and sub-reports to keep your code DRY (Don't Repeat Yourself).
-    **Embrace the Odoo Way:** Follow best practices to make the most of Odoo's awesome features.

## 4. **AUTOMATIC INSTANCE RESTARTS**: Magic in Action 🎩✨

Here’s where the magic happens. 🪄 Whenever you push to a repository with an Odoo instance attached, something cool happens: Automatic Restart

Module Availability: Module Installation/Update: After the restart, your newly pushed module will be available for installation or update in the Odoo instance. It’s like waving a magic wand! 🪄

Why This Rocks: 
**Seamless Integration**: No more manual restarts. Focus on coding while we handle the rest. 
**AUTOMATIC INSTANCE RESTARTS**: Magic in Action 🎩✨

