# Event-Driven-Notification-System

### 30 Days of DevOps - Project 2

This project is an **event-driven notification system** designed to send notifications based on real-time game schedules using **AWS Lambda**, **Amazon SNS (Simple Notification Service)**, and **Amazon EventBridge**. The system fetches data from an external API, processes it using AWS Lambda, and sends notifications to subscribers based on the game status.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Diagram of Game Days Alert](#diagram-of-game-days-alert)
3. [Setup Instructions](#setup-instructions)
    - [Clone the Repository](#1-clone-the-repository)
    - [Install Dependencies](#2-install-dependencies)
    - [Set Up the .env File](#3-set-up-the-env-file)
    - [Set Up the .gitignore File](#4-set-up-the-gitignore-file)
4. [Features](#features)

5. [License](#license)

---

## Project Overview

The **Event-Driven-Notification-System** allows users to get notifications about upcoming or in-progress games (e.g., NBA games). It uses **AWS Lambda** for processing, **Amazon SNS** for sending notifications, and **Amazon EventBridge** to schedule events. The system works by fetching data from an external API (e.g., BallDontLie) and formatting it before sending the updates to users via SNS.

---

### Diagram of Game Days Alert

![Event Driven Architecture](EventDrivenArchitect.drawio.png)

## Setup Instructions

### 1. Clone the Repository

To get started, clone the repository to your local machine:

```bash
git clone https://github.com/Alexpeain/Event-Driven-Notification-System.git
cd Event-Driven-Notification-System
```
### 2. Install Dependencies

``` bash 
    pip install -r requirements.txt
```

### 3. Set Up the .env File

``` bash
  SECRET_KEY=mysecretkey12345
  SNS_TOPIC_ARN=arn:aws:sns:your-region:your-account-id:your-topic-name
  API_KEY=your-api-key-here

```
### 4. Set Up the .gitignore File
```bash 
# Python
__pycache__/
*.pyc
*.pyo
venv/

# Environment files
.env

# IDE configurations
.vscode/
.idea/

```
## Features

### AWS Lambda

### Amazon SNS (Simple Notification Service)

### Amazon EventBridge


