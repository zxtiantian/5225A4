# Bird Recognition System

A full-stack web application for bird species recognition using images, videos, and audio. The system leverages advanced AI models for detection and classification, and provides a user-friendly interface for uploading, searching, and subscribing to bird notifications.

## Features

- **Bird Recognition**: Upload images, videos, or audio files to recognize bird species using AI models (YOLO for images/videos, BirdNET for audio).
- **Search**: Search the database for recognized birds by tags or species, with support for images, videos, and audio.
- **Audio, Image, and Video Support**: Unified interface for all media types, with tailored result displays and playback.
- **Subscription**: Subscribe to notifications for specific bird species and receive email alerts when new detections occur.
- **User Authentication**: Secure login and registration using AWS Cognito.
- **History**: View your past recognition results (if enabled).
- **Responsive UI**: Modern, mobile-friendly interface built with Vue 3 and Element Plus.

## Tech Stack

- **Frontend**: Vue 3, Element Plus, AWS Amplify, AWS S3, AWS Cognito
- **Backend**: AWS Lambda (Python), DynamoDB, S3, SNS
- **AI Models**: YOLO (image/video), BirdNET (audio)

## Project Structure

```
frontend/         # Vue 3 + Element Plus frontend
  src/
    views/        # Main pages (Upload, Search, Subscribe, Home, etc.)
    components/   # Reusable UI components
    utils/        # Utility functions (S3 upload, etc.)
backend/
  audio_model/    # Lambda for audio recognition
  lambda_image/   # Lambda for image recognition
  lambda_search/  # Lambda for search APIs
  ...
```

## Getting Started

### Prerequisites
- Node.js >= 16
- Python >= 3.8
- AWS account (for S3, Lambda, DynamoDB, Cognito, SNS)

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

- Configure AWS Amplify and S3 credentials in `frontend/src/utils/s3Upload.js` and `aws-exports.js`.
- Update API endpoints in the code if needed.

### Backend Setup

- Deploy Lambda functions in `audio_model/`, `lambda_image/`, and `lambda_search/` to AWS Lambda.
- Set up DynamoDB tables, S3 buckets, and SNS topics as referenced in the code.
- Update environment variables and resource ARNs as needed.

### Usage

- **Upload**: Go to the Upload page, select an image, video, or audio file, and start recognition.
- **Search**: Use the Search page to find recognized birds by tags or species. Audio results can be played directly in the browser.
- **Subscribe**: On the Subscribe page, enter your email and select bird species to receive notifications.
- **History**: (If enabled) View your recognition history from the profile menu.


