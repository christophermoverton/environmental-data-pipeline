# Environmental Data Pipeline

A scalable data pipeline designed for the collection, processing, and analysis of environmental data using Apache Airflow, Apache Spark, JupyterLab, and PostgreSQL. This project leverages Docker Compose to orchestrate multiple services, providing a robust framework for environmental data workflows.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Directory Structure](#directory-structure)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Setting Up API Keys](#setting-up-api-keys)
  - [Running the Airflow DAGs](#running-the-airflow-dags)
  - [Running Spark Jobs with Airflow](#running-spark-jobs-with-airflow)
- [Services](#services)
- [Contributing](#contributing)
- [License](#license)

## Overview

The Environmental Data Pipeline project provides a modular and extensible platform for processing and analyzing various types of environmental data. It utilizes Apache Airflow for orchestration, Apache Spark for scalable data processing, JupyterLab for interactive analysis, and PostgreSQL for data storage.

## Features

- **Orchestration with Apache Airflow**: Manage workflows and schedule tasks.
- **Scalable Processing with Apache Spark**: Perform large-scale data processing.
- **Interactive Analysis with JupyterLab**: Explore and analyze data using Jupyter notebooks.
- **Data Storage with PostgreSQL**: Store processed data in a structured format.
- **High-Performance Analytics with ClickHouse**: Optional integration for fast, analytical queries.
- **Dockerized Environment**: Easily deploy and manage services with Docker Compose.

## Directory Structure

The project is organized as follows:

```
environmental-data-pipeline/
│
├── airflow/
│   ├── dags/                     # Airflow DAGs (Directed Acyclic Graphs)
│       ├── environmental_data_dag.py    # DAG for data collection
│       └── spark_processing_dag.py       # DAG for Spark data processing
│   ├── logs/                     # Airflow logs
│   └── plugins/                  # Custom plugins for Airflow
│
├── notebooks/
│   ├── analysis.ipynb            # Jupyter notebook for data analysis
│
├── spark-app/
│   └── data_processing.py        # Spark job scripts for data processing
│
├── docker-compose.yml            # Docker Compose configuration file
└── postgresql-42.7.4.jar         # PostgreSQL JDBC driver for Spark
```

## Architecture

The pipeline consists of several interconnected components:

- **Airflow**: Manages the scheduling and orchestration of data processing tasks.
- **Spark**: Provides a distributed computing framework for data processing.
- **JupyterLab**: Offers an environment for interactive data exploration.
- **PostgreSQL**: Serves as the primary data warehouse.
- **ClickHouse (optional)**: Provides a high-performance, columnar storage option for analytics.

## Getting Started

### Prerequisites

Ensure that you have the following installed:

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Git](https://git-scm.com/)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/christophermoverton/environmental-data-pipeline.git
   cd environmental-data-pipeline
   ```

2. **Start the Docker Compose services:**

   ```bash
   docker-compose up -d
   ```

   This command will set up and start all services defined in the `docker-compose.yml` file.

## Usage

### Setting Up API Keys

Before running the pipeline, ensure that you have valid API keys for the required data sources. These API keys must be set as environment variables:

- **OpenWeatherMap API Key**: Set the `OPENWEATHERMAP_API_KEY` environment variable with your API key from [OpenWeatherMap](https://openweathermap.org/api).
- **AirVisual API Key**: Set the `AIRVISUAL_API_KEY` environment variable with your API key from [AirVisual](https://www.iqair.com/world-air-quality).

To set the environment variables in your local environment, add the following to your `.bashrc` or `.zshrc` file:

```bash
export OPENWEATHERMAP_API_KEY=your_openweathermap_api_key
export AIRVISUAL_API_KEY=your_airvisual_api_key
```

Alternatively, set these variables in the Docker Compose file under the Airflow services:

```yaml
environment:
  - OPENWEATHERMAP_API_KEY=your_openweathermap_api_key
  - AIRVISUAL_API_KEY=your_airvisual_api_key
```

### Running the Airflow DAGs

1. **Access the Airflow Web UI**:

   Navigate to [http://localhost:8090](http://localhost:8090) to access the Airflow web interface. Use the default credentials (`admin`/`admin`) unless you have changed them.

2. **Trigger the Environmental Data DAG**:

   - **DAG Name**: `environmental_data_dag`
   - **Description**: Fetches weather and air quality data for multiple cities and stores it in a PostgreSQL database.
   - **Schedule**: Runs hourly (`@hourly`).

   In the Airflow web UI, go to the "DAGs" tab, find `environmental_data_dag`, and toggle it to "on." Click the "Trigger DAG" button to run it manually or wait for the scheduled run.

### Running Spark Jobs with Airflow

The `spark_processing_dag.py` DAG manages the execution of Spark jobs for data processing:

- **DAG Name**: `spark_processing_dag`
- **Description**: Runs Spark jobs for data processing.
- **Schedule**: Runs daily (`@daily`).

#### Running the DAG

1. **Enable the Spark Processing DAG**:

   In the Airflow web UI, find the `spark_processing_dag` and toggle it to "on."

2. **Trigger the DAG**:

   Click on the "Trigger DAG" button next to `spark_processing_dag` to run it manually or wait for the daily schedule.

#### Monitoring and Logs

- **Monitoring**: Use the Airflow UI to monitor task execution, view logs, and check the status of each task.
- **Logs**: Logs for task executions are stored in the `./airflow/logs` directory and are accessible through the Airflow web interface.

### Database Access

The weather and air quality data are inserted into the PostgreSQL database. Use any PostgreSQL client to connect:

- **Host**: `localhost`
- **Port**: `5432`
- **User**: `airflow`
- **Password**: `airflow`
- **Database**: `airflow`

### JupyterLab

Access JupyterLab at [http://localhost:8888](http://localhost:8888) to analyze data collected by the pipeline. Notebooks can be found in the `notebooks` directory.

## Services

- **Airflow**: Manages data collection and processing tasks.
- **PostgreSQL**: Stores collected and processed data.
- **ClickHouse (optional)**: High-performance analytical database.
- **Spark**: Distributed data processing using master and worker nodes.
- **JupyterLab**: Interactive data exploration and analysis environment.

## Contributing

Contributions are welcome! Please follow the steps below to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m 'Add your feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a Pull Request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---
