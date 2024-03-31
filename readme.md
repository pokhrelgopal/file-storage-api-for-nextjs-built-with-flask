# File Store

## Overview

This project serves as a storage for files and folders, while building a fullstack NextJS application. It includes instructions for setting up the project environment and resolving initial database creation issues.

## Requirements

- Docker

## Getting Started

1. Clone the repository.
2. Navigate to the project directory.

## Usage

To start the project, run the following command in the project directory:

`docker-compose up --build`

Note: If the database hasn't been created, an error will occur.

## Database Setup

To create the necessary database, follow these steps:

1. Connect to the PostgreSQL container:

`docker exec -it <your_postgres_container_id> psql -U postgres`

Note: Here `postgres` is defined in `docker-compose.yaml`

Replace `<your_postgres_container_id>` with your PostgreSQL container ID.

2. Once connected to the PostgreSQL shell, create the database:

## File Structure

- **template**: Unused directory.
- **static**: Unused directory.

## Notes

- This project serves as a storage for files and folders, while building a fullstack NextJS application.
- The provided code may not be optimized but serves as a functional template.

## Disclaimer

The code provided in this project is primarily for personal use and may require adjustments to fit specific requirements or best practices. Use at your own discretion.

## Author

Gopal Pokhrel
