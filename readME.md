# Bob - The Whisky Recommendation AI Agent

Bob is an intelligent AI agent designed for the BAXUS ecosystem that analyzes users' virtual bars and provides personalized whisky recommendations for their wishlists.

## Overview

Bob analyzes your existing whisky collection to understand your preferences, then suggests new bottles that would complement your bar. The system leverages machine learning algorithms to identify patterns in your collection and make informed recommendations based on:

- Flavor profiles
- Regions and distilleries
- Price points
- Age statements
- Rarity and uniqueness

## Features

- **Collection Analysis**: Deep analysis of your existing bottles to identify patterns and preferences
- **Personalized Recommendations**: Tailored bottle suggestions based on your collection
- **Complementary Selections**: Recommendations that fill gaps in your collection
- **Price-Conscious Suggestions**: Options that respect your typical spending range
- **Detailed Reasoning**: Clear explanations for why each bottle was recommended

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/AbdulAbdullah/recomend.git
   cd bob-whisky-recommender
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   python manage.py migrate
   ```

5. Load initial data (whisky bottle database):
   ```bash
   python manage.py loaddata fixed_bottles.json
   ```

## Usage

### Start the Server

```bash
python manage.py runserver
```

The API will be available at http://localhost:8000/

### API Endpoints

- **GET /api/recommendations/{username}/**
  - Provides personalized recommendations for a specific user
  - Returns JSON with recommended bottles and reasoning

- **GET /api/analyze/{username}/**
  - Analyzes the user's collection and returns insights
  - Returns JSON with collection analysis data

- **POST /api/update-preferences/**
  - Updates user preferences for more tailored recommendations
  - Accepts JSON body with preference parameters

### Example

```bash
curl -X GET "http://localhost:8000/api/recommendations/your_username/"
```


### Code Structure

- **api/**: API endpoints and serializers
- **recommendation_engine/**: Core recommendation algorithms
- **data_integration/**: Integration with external BAXUS APIs
- **data/**: Static data files including bottle catalog
