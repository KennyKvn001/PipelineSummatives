# Student Dropout Prediction System

[![Demo Video](https://img.youtube.com/vi/SZQVec1enb0)](https://www.youtube.com/watch?v=SZQVec1enb0)

## Project Description

The Student Dropout Prediction System is a machine learning application that predicts a student's risk of dropping out of an academic program based on several key factors. The system analyzes student data such as academic performance, financial status, and demographic information to calculate the probability of dropout and classify the risk level as low, medium, or high.

### Key Features

- **Prediction Tool**: Input student data to get instant dropout risk assessment
- **Data Visualization**: View analytics and insights on dropout patterns
- **Admin Dashboard**: Upload training data and retrain the model when needed
- **MongoDB Integration**: Store prediction results and training data
- **Responsive Design**: Works on desktop and mobile devices

## System Architecture

The application consists of two main components:

1. **Backend API (FastAPI)**: Handles predictions, data processing, and model management
2. **Frontend UI (React)**: Provides user interface for making predictions and managing the system

## How It Works

### Student Dropout Prediction Process

1. **Data Collection**: The system collects key student metrics:

   - Academic performance (courses approved, grades)
   - Financial factors (tuition payment status, scholarship status)
   - Personal factors (age, gender)

2. **Prediction Processing**: When a user submits student data, the system:

   - Standardizes the input data to match model requirements
   - Passes the data to the trained ML model
   - Calculates dropout probability
   - Categorizes risk level (low, medium, high)
   - Stores the prediction in MongoDB

3. **Visualization & Analysis**: The system provides insights on:
   - Risk distribution across student population
   - Impact of different factors on dropout probability
   - Historical prediction trends

### Model Training and Management

1. **Data Upload**: Administrators can upload CSV files with historical student data
2. **Preprocessing**: The system transforms and normalizes the data
3. **Training**: A neural network model is trained on the processed data
4. **Evaluation**: Performance metrics like accuracy and precision are calculated
5. **Deployment**: The new model is saved and used for future predictions

## Deployment Instructions

### Docker Deployment (Recommended)

#### Prerequisites

- Docker and Docker Compose installed
- Git

#### Steps to Deploy

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/student-dropout-prediction.git
   cd student-dropout-prediction
   ```

2.Create a .env file in the root directory:

````CopyMONGODB_URI=mongodb://mongodb:27017
MONGO_DB=student_dropout
MONGO_CONNECT_TIMEOUT_MS=5000
ENVIRONMENT=production```

3.Build and run the Docker containers:
```bashCopydocker-compose up -d --build```

4.Access the application:

Frontend: http://localhost:3000
Backend API: http://localhost:8000
API Documentation: http://localhost:8000/docs
````
